# ⚓ 大海战 · H5 版

原版 Flash 游戏《大海战》的网页版,基于 [Ruffle](https://ruffle.rs) Flash 模拟器在浏览器中原样运行原始 SWF 文件,画面、贴图、声音、操作与交互逻辑与原版完全一致。

**在线游玩:** https://dahaizhan.pages.dev

## 运行原理

- `dahaizhan.swf` 是游戏本体(Flash 5 / ActionScript 1,640×420,12fps),所有贴图、音效、逻辑均内嵌其中;
- `ruffle/` 目录是自托管的 Ruffle WASM 模拟器(0.5.0),在浏览器中模拟 Flash Player 运行时,直接执行 SWF 原始字节码,不依赖任何第三方 CDN;
- 页面提供按比例自适应缩放、全屏、重新开始等功能,移动端浏览器可将触控映射为鼠标操作。

## 本地运行

Flash/WASM 需要通过 HTTP 访问(不能直接双击打开 HTML),任意静态服务器均可:

```bash
cd dahaizhan
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 目录结构

```
├── index.html          # 游戏页面
├── dahaizhan.swf       # 原始游戏文件
└── ruffle/             # 自托管 Ruffle 模拟器
    ├── ruffle.js       # 加载器
    ├── core.ruffle.*.js / *.wasm   # 模拟器内核
    └── LICENSE_*       # Ruffle 许可证(Apache-2.0 / MIT)
```

## 部署(Cloudflare Pages)

```bash
wrangler pages project create dahaizhan --production-branch=main
wrangler pages deploy . --project-name=dahaizhan
```

## 常见问题

- **没有声音?** 浏览器自动播放策略会拦截声音,点击一次游戏画面即可开启;
- **画面大小?** 页面按原始舞台比例(640:420)自适应缩放,点击「⛶ 全屏」可获得最佳体验;
- **手机可以玩吗?** 可以,Ruffle 会自动把触控转换为鼠标事件,单指点击/拖动即可。
