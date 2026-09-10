#!/usr/bin/env python3
"""生成《大海战》中文版 SVG 矢量替换图(与原版同等清晰度)"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
import os, math

FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'SourceHanSansCN-Bold.otf')
OUT = '/tmp/build_cn/svg'
os.makedirs(OUT, exist_ok=True)

font = TTFont(FONT_PATH)
glyphset = font.getGlyphSet()
cmap = font.getBestCmap()
UPM = font['head'].unitsPerEm

def char_path(ch, size, x, y):
    gname = cmap[ord(ch)]
    glyph = glyphset[gname]
    s = size / UPM
    spen = SVGPathPen(glyphset, ntos=lambda v: f'{v:.2f}')
    tpen = TransformPen(spen, Transform(s, 0, 0, -s, x, y))
    glyph.draw(tpen)
    return spen.getCommands()

def text_width(text, size):
    return sum(glyphset[cmap[ord(c)]].width for c in text) * size / UPM

def text_path(text, size, *, center=None, left=None, fill, spacing=0.0, shadow=None, shadow_off=1.0):
    """left=(x, baseline_y) 或 center=(cx, 垂直中心)"""
    w = text_width(text, size) + spacing * (len(text) - 1)
    if center is not None:
        x = center[0] - w / 2
        base_y = center[1] + size * 0.35
    else:
        x, base_y = left
    parts = []
    def emit(color, dx, dy):
        cx = x
        for ch in text:
            if ch == ' ':
                cx += size * 0.5 + spacing
                continue
            d = char_path(ch, size, cx, base_y + dy)
            if d:
                parts.append(f'<path d="{d}" fill="{color}"/>')
            cx += glyphset[cmap[ord(ch)]].width * size / UPM + spacing
    if shadow:
        emit(shadow, shadow_off, shadow_off)
    emit(fill, 0, 0)
    return '\n'.join(parts)

def dot_path(cx, cy, r, fill):
    pts = []
    for i in range(8):
        a = math.pi * 2 * i / 8
        pts.append(f'{cx + r*math.cos(a):.2f} {cy + r*math.sin(a):.2f}')
    return f'<path d="M {" L ".join(pts)} Z" fill="{fill}"/>'

def rect_path(x0, y0, x1, y1, fill):
    return f'<path d="M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z" fill="{fill}"/>'

def svg(cid, w, h, body):
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'
    open(f'{OUT}/{cid}.svg', 'w').write(doc)
    print(f'svg {cid} ({w}x{h}, {len(doc)}B)')

GRAY = '#cccccc'; GOLD = '#ffcc00'; ORANGE = '#ff9900'; LYELLOW = '#ffff99'
TITLE_GOLD = '#ffe98c'

# 90 加载中... (63x12)
svg(90, 63, 12, text_path('加载中...', 11, center=(31.5, 6.5), fill='#00ff00'))

# 121 输入你的名字: + 输入框 (317x22)
body = rect_path(107.5, 0.5, 317.5, 21.5, '#000000') + '\n' + \
       rect_path(108.5, 1.5, 316.5, 20.5, '#333333') + '\n' + \
       text_path('输入你的名字:', 14, center=(51, 11.5), fill=GOLD, shadow='#000000', shadow_off=1.0)
svg(121, 317, 22, body)

# 127 进入 (30x9)
svg(127, 30, 9, text_path('进入', 9, center=(15, 4.8), fill=GOLD, shadow='#000000', shadow_off=1.0))

# 163/164 页脚 (293x10)
footer = '原作:BATTLESHIPS - GENERAL QUARTERS II v2.7 © 2003 F.Winters'
svg(163, 293, 10, text_path(footer, 9, center=(146.5, 5.2), fill=GRAY))
svg(164, 293, 10, text_path(footer, 9, center=(146.5, 5.2), fill=GRAY))

# 168 舰队布阵 (153x18, 黑色)
svg(168, 153, 18, text_path('舰队布阵', 19, center=(76.5, 9.2), fill='#000000', spacing=9))

# 175 作战说明 (230x100, 橙色)
body = text_path('作战说明:', 14, left=(18, 2 + 14 * 0.86), fill=ORANGE)
for i, step in enumerate(['点击选择一艘军舰。', '用左右方向键旋转军舰。', '点击海面棋盘放置军舰。']):
    ytop = 22 + i * 22
    body += '\n' + text_path(f'{i+1}.', 12, left=(1, ytop + 12 * 0.86), fill=ORANGE)
    body += '\n' + text_path(step, 12, left=(18, ytop + 12 * 0.86), fill=ORANGE)
svg(175, 230, 100, body)

# 256 电脑 / 266 玩家(斜置 -30°)
def rotated_text(cid, text, size, w, h, fill, angle=-30):
    a = math.radians(angle)
    cx, cy = w / 2, h / 2
    cos_a, sin_a = math.cos(a), math.sin(a)
    parts = []
    tw = text_width(text, size)
    x0 = cx - tw / 2
    base = cy + size * 0.35
    for ch in text:
        gw = glyphset[cmap[ord(ch)]].width * size / UPM
        px, py = x0 + gw / 2, base
        rx = cx + (px - cx) * cos_a - (py - cy) * sin_a
        ry = cy + (px - cx) * sin_a + (py - cy) * cos_a
        gname = cmap[ord(ch)]
        s = size / UPM
        spen = SVGPathPen(glyphset, ntos=lambda v: f'{v:.2f}')
        tp = TransformPen(spen, Transform(cos_a * s, sin_a * s, -sin_a * s, cos_a * s, rx, ry))
        glyphset[gname].draw(tp)
        d = spen.getCommands()
        if d:
            parts.append(f'<path d="{d}" fill="{fill}"/>')
        x0 += gw
    svg(cid, w, h, '\n'.join(parts))

rotated_text(256, '电脑', 20, 77, 45, '#ffffff')
rotated_text(266, '玩家', 17, 58, 34, '#ffffff')

# 280 船名清单 — 标定:几何边界 62.1x134.1,原点=名字左缘(svg 尺寸=几何尺寸 → 缩放1.0)
# 目标舞台行顶: 262/293/325/357/388 − 261 → 基线 = 顶 + 9.9
names = ['航空母舰', '战列舰', '护卫舰', '潜艇', '扫雷舰']
body = []
for i, nm in enumerate(names):
    base = 10.9 + 31.5 * i
    body.append(text_path(nm, 11.5, left=(0, base), fill='#ffffff'))
svg(280, 62.1, 134.1, '\n'.join(body))

# 290 战斗结束 (109x17, 黑色)
svg(290, 109, 17, text_path('战斗结束', 16, center=(54.5, 8.8), fill='#000000', spacing=6))

# 300 再玩一次 (55x10)
svg(300, 55, 10, text_path('再玩一次', 9, center=(27.5, 5.2), fill=GOLD, shadow='#000000', shadow_off=1.0))

# 303 作战结果面板 (247x85)
body = text_path('作战结果', 17, left=(2, 1 + 17 * 0.86), fill=TITLE_GOLD)
body += '\n' + rect_path(122.5, 31, 123.5, 84, GRAY)
body += '\n' + rect_path(244.5, 31, 245.5, 84, GRAY)
dots = []
for x in range(2, 246, 5):
    dots.append(dot_path(x, 53, 0.9, GRAY))
    dots.append(dot_path(x, 84, 0.9, GRAY))
body += '\n' + '\n'.join(dots)
body += '\n' + text_path('玩家:', 13, left=(3, 62 + 13 * 0.35), fill=LYELLOW)
svg(303, 247, 85, body)

# 317 重新开始 (43x10)
svg(317, 43, 10, text_path('重新开始', 8, center=(21.5, 5.2), fill=GOLD, shadow='#000000', shadow_off=1.0))

# 319 警告面板 (295x48)
body = text_path('警告!!', 14, center=(147.5, 9), fill=GOLD)
body += '\n' + text_path('你的军舰还没有全部部署!', 13, center=(147.5, 26), fill=LYELLOW)
body += '\n' + text_path('点击“重新开始”按钮重新布阵。', 13, center=(147.5, 41), fill=LYELLOW)
svg(319, 295, 48, body)

# 空 SVG(删除 Miniclip 等元素)
EMPTY_DIMS = {107:(248,25),110:(310,49),111:(290,30),112:(286,25),114:(288,8),132:(121,20),
              135:(75,8),136:(75,8),138:(75,8),140:(79,8),141:(79,8),142:(79,8),
              144:(43,8),145:(43,8),146:(43,8),292:(208,10),293:(208,10),295:(139,9)}
for cid, (w, h) in EMPTY_DIMS.items():
    svg(cid, w, h, '')

print('\nSVG 全部生成完毕')
