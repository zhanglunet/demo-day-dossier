# wechat-article-publish · Claude Code Skill

把一个已完成的技术项目变成一篇可发布的 **微信公众号** 长文 —— 包含写作 / 配图 / 转换 / 半自动发布。

针对 **个人订阅号**（无 API 权限）设计。所有流程基于浏览器 UI 自动化，最后「群发」按钮永远人工。

## 流水线 5 阶段

```
项目盘点 → 写叙事 md → 7 张配图 → md → 公众号 HTML → 半自动贴 → 用户群发
```

详细 SOP 见 [`SKILL.md`](./SKILL.md)。

## 文件布局

```
skills/wechat-article-publish/
├── SKILL.md                              ← Skill 入口（5 阶段 SOP）
├── README.md                             ← 当前文件
├── templates/
│   ├── article.md.tmpl                   ← 五段结构文章框架
│   ├── cover-1200x675.html.tmpl          ← 封面图模板（16:9）
│   ├── pipeline-1200x600.html.tmpl       ← 多阶段流水线图
│   ├── parallel-1200x700.html.tmpl       ← 并行/对比 + 维度框架
│   └── pyramid-1200x600.html.tmpl        ← 金字塔 / 统计图
├── scripts/
│   ├── md2wechat.py                      ← markdown → inline-style HTML
│   ├── wechat_publish.py                 ← Playwright 半自动（兜底）
│   ├── render-image.sh                   ← Chrome headless 截图 @2x
│   ├── set-clipboard-html.sh             ← 设剪贴板为 «class HTML»
│   └── send-cmd-v.sh                     ← 远程发 Cmd+V 到浏览器
└── examples/
    └── demo-day-dossier-2026/            ← 首跑参考
        ├── article.md                    ← 实战记原文 (4200 字)
        └── README.md                     ← 案例说明
```

## 快速跑（手动版）

```bash
SKILL=~/.claude/skills/wechat-article-publish

# 阶段 1：你自己写 markdown（参考 templates/article.md.tmpl）

# 阶段 2：生成 7 张图
$SKILL/scripts/render-image.sh templates/cover.html  images/00-cover.png 1200 675
$SKILL/scripts/render-image.sh "https://my-site/"    images/01-hero.png  1280 800
# ...

# 阶段 3：md → 公众号 HTML
python3 $SKILL/scripts/md2wechat.py docs/article.md /tmp/article.html

# 阶段 4：剪贴板 + 浏览器
$SKILL/scripts/set-clipboard-html.sh /tmp/article.html
open "https://mp.weixin.qq.com/cgi-bin/home"
# 在 Chrome 里手动登录 + 新建图文 + 点正文区
$SKILL/scripts/send-cmd-v.sh "Google Chrome"

# 阶段 5：用户保存草稿 → 公众号 App 群发（永远人工）
```

但通常你不需要手动跑这些 —— 用 Claude Code 调本 skill，按 `SKILL.md` 的阶段流走。

## 关键技术细节

1. **剪贴板必须 `«class HTML»` 类型**。`pbcopy` 给 `text/plain`，公众号编辑器解析成裸字符串。
2. **外链图自动镜像**。粘贴时公众号会异步把所有 `<img src=https://...>` 抓到自己 CDN（mmbiz.qpic.cn），文章永久可读。
3. **用日常 Chrome 而非 Playwright Chromium**。日常 Chrome 已是登录态，省扫码；Playwright 临时 profile 关浏览器 = 登录丢。
4. **个人订阅号没 API**。`draft/add` 等接口对未认证账号 401。所有路径都是浏览器 UI 半自动。

## 安装为 Claude Code Skill

```bash
cp -r skills/wechat-article-publish ~/.claude/skills/wechat-article-publish
```

之后在 Claude Code 里：

```
/wechat-article-publish ~/dev/your-project
```

## 首跑案例

**「56 个路演项目，一个人，一晚上」**（基于 demo-day-dossier 项目）：

- 字数 4200 字 · 配图 7 张 · 整体耗时 3 小时
- 公众号：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>
- 网页版：<https://qiji-roadshow-2026.pages.dev/story>
- 源文件：[`examples/demo-day-dossier-2026/article.md`](./examples/demo-day-dossier-2026/article.md)
