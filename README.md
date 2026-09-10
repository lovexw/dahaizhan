# ⚓ 大海战 · 中文版

原版 Flash 游戏《Battleships - General Quarters II v2.7》(F.Winters / Miniclip, 2003)的网页中文版。基于 [Ruffle](https://ruffle.rs) 模拟器运行,画面、声音、玩法与原版完全一致。

**在线游玩:** https://dahaizhan.pages.dev

## 中文版说明

- 游戏内全部界面文字、船名、将军播报均已中文化;
- 去除了 Miniclip 片头广告与全部外链按钮,加载后直接进入输入名字画面;
- 军舰名称:航空母舰 / 战列舰 / 护卫舰 / 潜艇 / 扫雷舰;
- 手机端自动显示虚拟方向键(◀ ▶),用于布阵阶段旋转军舰;
- 默认玩家名"小海军",可在输入框随意修改。

## 玩法

1. 输入名字 → 点击"进入";
2. 左栏点击选择军舰,左右方向键转向,点击己方海面布阵(共 5 艘);
3. 布阵完毕自动开战,点击右侧敌军海域开炮;
4. 击沉敌方全部 5 艘军舰获胜。
5. 彩蛋:名字输入 `bsgq` 可显示敌舰位置。

## 本地运行

```bash
cd dahaizhan
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 中文版是怎么做的

`tools/` 目录包含完整的汉化构建链,可复现:

```
tools/gen_svgs.py      # 用思源黑体字形生成 15 张矢量文字替换图(SVG)
tools/build.py         # 主构建脚本:
                       #   1. 翻译 ActionScript 对话/船名/提示(ffdec 反编译→改写→回写)
                       #   2. ffdec 批量替换 33 个 Shape(SVG 矢量替换 + 清空 Miniclip 元素)
                       #   3. 清空 8 个外链按钮脚本
                       #   4. 预加载器改为跳过片头直接进标题画面
tools/upgrade_swf6.py  # SWF5→SWF6 结构升级(UTF-8 字符串 + ClipActions 字段转换)
```

关键技术点:
- **随机数函数修复**:原 SWF 的 `getRandomvalue` 用了 `("" + Rng).length` 这种依赖
  AS1 宽松语义的写法,ffdec 反编译往返会把它错误渲染成 `"" + Rng.length`(对数字
  取属性 = undefined),重编译后随机数恒为 NaN——电脑 AI 坐标全部越界、炮击溢出
  棋盘、胜负判定错乱。构建脚本里已替换为标准的 `Math.floor(Math.random() * Rng) + min`。
- **SWF 版本 5→6**:为了让中文字符串以 UTF-8 编码生效,必须升级版本号,同时转换
  ClipActions 的 UI16→UI32 事件标志结构(`upgrade_swf6.py` 处理,含自测);
- **中文渲染**:游戏使用设备字体(Helvetica 等),Ruffle 的 `deviceFontRenderer: "canvas"`
  让浏览器字体渲染动态文字(将军播报等),天然支持中文;
- **静态文字**:原版把界面文字转成了矢量图形,用思源黑体字形逐个生成同尺寸同颜色的
  SVG 替换回去,保持原版清晰度。

构建依赖(需要在 /tmp 准备):`ffdec`(JPEXS 反编译器)、JRE 17、导出的原版脚本。

## 目录结构

```
├── index.html          # 游戏页面(自适应/全屏/虚拟方向键)
├── dahaizhan.swf       # 原版游戏
├── dahaizhan_cn.swf    # 中文版游戏(构建产物)
├── fonts/              # 思源黑体(汉化字形来源)
├── tools/              # 汉化构建链
└── ruffle/             # 自托管 Ruffle 模拟器
```

## 部署(Cloudflare Pages)

```bash
wrangler pages deploy . --project-name=dahaizhan
```

## 常见问题

- **没有声音?** 浏览器自动播放策略会拦截,点击一次游戏画面即可;
- **手机方向键在哪?** 触屏设备右下角自动显示;也可用工具栏按钮开关;
- **如何重新开始?** 页面下方"↻ 重新开始"按钮。
