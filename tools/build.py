#!/usr/bin/env python3
"""《大海战》中文版构建:翻译脚本 → ffdec 批量替换 → 版本号升级(SWF5→6 UTF-8)

前置条件:
  1. 用 ffdec 导出原版脚本: java -jar ffdec.jar -export script /tmp/build_cn/scripts dahaizhan.swf
  2. 生成替换 SVG:        python3 tools/gen_svgs.py
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FFDEC = '/tmp/ffdec/ffdec.jar'
JAVA = '/tmp/jdk-17.0.20.1+1-jre/Contents/Home/bin/java'
SRC_SWF = '/Users/xw/Downloads/flash-game/dahaizhan.swf'
SCRIPT_DIR = '/tmp/build_cn/scripts/scripts'
BUILD = '/tmp/build_cn'
SVG = BUILD + '/svg'
OUT_SWF = os.path.join(HERE, '..', 'dahaizhan_cn.swf')

# ============ 第一步:准备翻译后的脚本 ============
work_scripts = BUILD + '/scripts_patched'
if os.path.exists(work_scripts):
    shutil.rmtree(work_scripts)
shutil.copytree(SCRIPT_DIR, work_scripts)

def patch(relpath, pairs):
    p = os.path.join(work_scripts, relpath)
    s = open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, f'未找到: {old[:60]} in {relpath}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)

FRAME1 = 'frame_1/DoAction.as'
patch(FRAME1, [
    ('"All ships have been deployed!"', '"所有军舰都部署完毕!"'),
    ('"Do not place ships on top of each other"', '"军舰不能叠在一起哦"'),
    ('"Place your ship within the game grid!"', '"请把军舰放进海面棋盘里!"'),
    ('"We have lost"', '"我们输了……"'),
    ('"Our " + shipP[ciTempShipNum].name + " has been sunk !"', '"我们的" + shipP[ciTempShipNum].name + "被击沉了!"'),
    ('"We have destroyed the enemy\\\'s " + shipC[plHitShipNum].name + ", sir!"', '"报告长官!我们击沉了敌方的" + shipC[plHitShipNum].name + "!"'),
    ('"We have WON!!"', '"我们赢啦!!"'),
    ('"We have allready shot this position, sir!"', '"报告长官!这个位置已经打过了!"'),
    ('"Well done, " + myname + ", well done!"', '"干得漂亮, " + myname + ", 真棒!"'),
    ('"You should sign up, " + myname + "!"', '"你应该去参军, " + myname + "!"'),
    ('"Don\\\'t you love the smell of burned steel, " + myname + "?"', '"喜欢钢铁烧焦的味道吗, " + myname + "?"'),
    ('"War is hell, right, " + myname + "?"', '"战争很残酷, 对吧, " + myname + "?"'),
    ('"Do you want some more, " + myname + "?"', '"还想再来一发吗, " + myname + "?"'),
    ('"This is too easy, " + myname + "!"', '"这太简单啦, " + myname + "!"'),
    ('"We won this battle, " + myname + ", not the war!"', '"这场战斗我们赢了, " + myname + ", 但战争还没结束!"'),
    ('"An impressive victory, " + myname + "!"', '"辉煌的胜利, " + myname + "!"'),
    ('"Let\\\'s get some medals, " + myname + "!"', '"去赢一枚勋章吧, " + myname + "!"'),
    ('"It\\\'s good to have you back, " + myname + "!"', '"欢迎归队, " + myname + "!"'),
    ('"You can keep your boat, " + myname + "!"', '"这支舰队就交给你啦, " + myname + "!"'),
    ('var myname = "Anonymous";', 'var myname = "小海军";'),
    ('"Minesweeper"', '"扫雷舰"'),
    ('"Submarine"', '"潜艇"'),
    ('"Frigate"', '"护卫舰"'),
    ('"Battleship"', '"战列舰"'),
    ('"Aircraft Carrier"', '"航空母舰"'),
    ('admData[0] = "Great shot !";', 'admData[0] = "打得好!";'),
    ('admData[1] = "Payback time !";', 'admData[1] = "该报仇了!";'),
    ('admData[2] = "Allright !";', 'admData[2] = "很好!";'),
    ('admData[3] = "Take that !";', 'admData[3] = "接招!";'),
    ('admData[4] = "Yeah !";', 'admData[4] = "耶!";'),
    ('admData[5] = "Way to go !";', 'admData[5] = "干得漂亮!";'),
    ('admData[6] = "Bullseye !";', 'admData[6] = "正中靶心!";'),
    ('admData[7] = "Strike One !";', 'admData[7] = "一击命中!";'),
    ('admData[8] = "Bingo !";', 'admData[8] = "中了!";'),
    ('admData[9] = "Okay ! !";', 'admData[9] = "好样的!!";'),
    ('admData[10] = "HIT !";', 'admData[10] = "命中!";'),
])

patch('DefineSprite_82/frame_1/DoAction.as', [
    ('"Congratulations, the entire enemy fleet has been annihilated!"', '"恭喜!敌方舰队全军覆没!"'),
])

BTN_EMPTY = 'on(release){\n}'
BUTTONS = ['DefineButton2_133', 'DefineButton2_139', 'DefineButton2_143',
           'DefineButton2_147', 'DefineButton2_166', 'DefineButton2_289',
           'DefineButton2_294', 'DefineButton2_318']
for b in BUTTONS:
    p = os.path.join(work_scripts, b, 'BUTTONCONDACTION on(release).as')
    assert os.path.exists(p), p
    open(p, 'w', encoding='utf-8').write(BTN_EMPTY)

print('脚本翻译完成')


# 修改预加载器:加载完成后直接跳到标题画面(CutScene01),跳过 Miniclip 片头
PRELOADER = 'DefineSprite_89/frame_1/PlaceObject2_87_2/CLIPACTIONRECORD onClipEvent(enterFrame).as'
p = os.path.join(work_scripts, PRELOADER)
s = open(p, encoding='utf-8').read()
assert 'gotoAndPlay("continue")' in s
s = s.replace('gotoAndPlay("continue")', 'gotoAndStop("CutScene01")')
open(p, 'w', encoding='utf-8').write(s)

print('预加载器已改为跳过片头')

# ============ 第二步:组装 ffdec -replace 参数 ============
pairs = []
for cid in [90, 121, 127, 163, 164, 168, 175, 256, 266, 280, 290, 300, 303, 317, 319]:
    pairs += [str(cid), f'{SVG}/{cid}.svg']
for cid in [107, 110, 111, 112, 114, 132, 135, 136, 138, 140, 141, 142, 144, 145, 146, 292, 293, 295]:
    pairs += [str(cid), f'{SVG}/{cid}.svg']
pairs += ['123', f'{BUILD}/name123.txt']
pairs += ['/DefineSprite_89/frame_1/PlaceObject2_87_2/CLIPACTIONRECORD onClipEvent(enterFrame)',
          f'{work_scripts}/DefineSprite_89/frame_1/PlaceObject2_87_2/CLIPACTIONRECORD onClipEvent(enterFrame).as']
pairs += ['/frame_1/DoAction', f'{work_scripts}/{FRAME1}']
pairs += ['/DefineSprite_82/frame_1/DoAction', f'{work_scripts}/DefineSprite_82/frame_1/DoAction.as']
for b in BUTTONS:
    pairs += [f'/{b}/BUTTONCONDACTION on(release)', f'{work_scripts}/{b}/BUTTONCONDACTION on(release).as']

cmd = [JAVA, '-jar', FFDEC, '-replace', SRC_SWF, BUILD + '/step1.swf'] + pairs
print('运行 ffdec 替换(共 %d 项)...' % (len(pairs) // 2))
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-1500:])
    print('STDERR:', r.stderr[-2000:])
    sys.exit(1)

# ============ 第三步:SWF5→6 升级(UTF-8 字符串 + ClipActions UI16→UI32) ============
sys.path.insert(0, HERE)
from upgrade_swf6 import upgrade
upgrade(BUILD + '/step1.swf', OUT_SWF)
print('中文版已生成:', os.path.abspath(OUT_SWF))
