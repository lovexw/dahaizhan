#!/usr/bin/env python3
"""SWF5 → SWF6 升级:版本号 + ClipActions 结构转换

SWF5 → SWF6 差异(经原文件逐字节核对):
1. 字符串编码:ANSI → UTF-8(中文所需)
2. CLIPACTIONS 顶层:保留UI16(不变) + allEventFlags UI16 → UI32
3. CLIPACTIONRECORD:事件标志 UI16 → UI32(本文件无 KeyPress 事件,无快键码)
4. 终止符:UI16 0 → UI32 0
"""
import struct
import sys


class Reader:
    def __init__(self, data, pos=0):
        self.d = data
        self.p = pos

    def u8(self):
        v = self.d[self.p]
        self.p += 1
        return v

    def u16(self):
        v = int.from_bytes(self.d[self.p:self.p + 2], 'little')
        self.p += 2
        return v

    def u32(self):
        v = int.from_bytes(self.d[self.p:self.p + 4], 'little')
        self.p += 4
        return v

    def raw(self, n):
        v = self.d[self.p:self.p + n]
        self.p += n
        return bytes(v)


class Writer:
    def __init__(self):
        self.out = bytearray()

    def u8(self, v):
        self.out.append(v)

    def u16(self, v):
        self.out += struct.pack('<H', v)

    def u32(self, v):
        self.out += struct.pack('<I', v)

    def raw(self, b):
        self.out += b


def u16_to_u32(w, v):
    """SWF 事件标志 UI16(值均 <0x10000)→ UI32 小端"""
    w.u16(v)
    w.u16(0)


def convert_clip_actions(r):
    """转换 CLIPACTIONS:SWF5 → SWF6"""
    w = Writer()
    w.u16(r.u16())                 # 顶层保留字段 UI16(两版本一致)
    u16_to_u32(w, r.u16())         # allEventFlags: UI16 → UI32
    while True:
        ev = r.u16()               # 记录事件标志(UI16)
        if ev == 0:
            w.u32(0)               # 终止符:UI16 0 → UI32 0
            break
        u16_to_u32(w, ev)          # 记录事件:UI16 → UI32
        alen = r.u32()
        w.u32(alen)                # 动作长度 UI32(不变)
        w.raw(r.raw(alen))         # 动作字节(不变)
    return bytes(w.out)


def skip_matrix(r):
    start = r.p
    d = r.d

    def bit(i):
        return (d[start + (i >> 3)] >> (7 - (i & 7))) & 1

    i = 0
    if bit(0):
        i = 1
        nb = 0
        for k in range(5):
            nb = (nb << 1) | bit(i + k)
        i += 5 + 2 * nb
    else:
        i = 1
    if bit(i):
        i += 1
        nb = 0
        for k in range(5):
            nb = (nb << 1) | bit(i + k)
        i += 5 + 2 * nb
    else:
        i += 1
    nb = 0
    for k in range(5):
        nb = (nb << 1) | bit(i + k)
    i += 5 + 2 * nb
    return (i + 7) >> 3


def skip_cxform(r):
    start = r.p
    d = r.d

    def bit(i):
        return (d[start + (i >> 3)] >> (7 - (i & 7))) & 1

    has_add = bit(0)
    has_mul = bit(1)
    nb = 0
    for k in range(4):
        nb = (nb << 1) | bit(2 + k)
    i = 6 + (4 * nb if has_mul else 0) + (4 * nb if has_add else 0)
    return (i + 7) >> 3


def process_tag(r, w):
    code_len = r.u16()
    code = code_len >> 6
    long_form = (code_len & 0x3f) == 0x3f
    ln = r.u32() if long_form else code_len & 0x3f
    body = r.raw(ln)

    if code == 0:
        w.u16(0)
        return True

    if code == 26 and ln > 0 and (body[0] & 0x80):
        cr = Reader(body)
        cw = Writer()
        flags = cr.u8()
        cw.u8(flags)
        cw.u16(cr.u16())                     # depth
        if flags & 0x02:
            cw.u16(cr.u16())                 # characterId
        if flags & 0x04:
            n = skip_matrix(cr)
            cw.raw(cr.raw(n))                # matrix
        if flags & 0x08:
            n = skip_cxform(cr)
            cw.raw(cr.raw(n))                # colorTransform(CXFORMWITHALPHA)
        if flags & 0x10:
            cw.u16(cr.u16())                 # ratio
        if flags & 0x20:                     # name
            start = cr.p
            while cr.d[cr.p] != 0:
                cr.p += 1
            cr.p += 1
            cw.raw(cr.d[start:cr.p])
        if flags & 0x40:
            cw.u16(cr.u16())                 # clipDepth
        cw.raw(convert_clip_actions(cr))
        emit_tag(w, 26, bytes(cw.out))
        return False

    if code == 39:                           # DefineSprite:递归
        cr = Reader(body)
        cw = Writer()
        cw.u16(cr.u16())                     # charId
        cw.u16(cr.u16())                     # frameCount
        while True:
            if process_tag(cr, cw):
                break
        emit_tag(w, 39, bytes(cw.out))
        return False

    emit_tag(w, code, bytes(body), long_form, ln)
    return False


def emit_tag(w, code, body, long_form=None, ln=None):
    n = len(body)
    if long_form is None:
        long_form = n >= 0x3f
    if not long_form and n < 0x3f:
        w.u16((code << 6) | n)
    else:
        w.u16((code << 6) | 0x3f)
        w.u32(n)
    w.raw(body)


def upgrade(path_in, path_out):
    data = open(path_in, 'rb').read()
    assert data[:3] == b'FWS', '需要未压缩 SWF(FWS)'
    nbits = (data[8] >> 3) & 0x1f
    body_start = 8 + ((5 + 4 * nbits + 7) >> 3) + 4
    header = bytearray(data[:body_start])
    header[3] = 6                            # 版本号 5 → 6
    r = Reader(data, body_start)
    w = Writer()
    while True:
        if process_tag(r, w):
            break
    out = bytearray(header) + bytearray(w.out)
    struct.pack_into('<I', out, 4, len(out))
    open(path_out, 'wb').write(bytes(out))
    print(f'SWF6 升级完成: {path_out} ({len(out)} 字节)')


if __name__ == '__main__':
    upgrade(sys.argv[1], sys.argv[2])
