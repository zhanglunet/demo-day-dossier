---
name: wechat-article-publish
description: |
  把一个已完成的技术项目（代码 / 数据 / 部署 URL 都到位）变成一篇可发布的 **微信公众号** 长文：
  (1) 叙事性 markdown 文章（钩子 → 痛点 → 方案 → 意义 → CTA 五段结构），
  (2) 7 张配图（1 张 16:9 封面 + N 张自定义 SVG/CSS 插图 + N 张线上页面截图，Chrome headless @2x Retina），
  (3) 把 markdown 转成公众号编辑器友好的 inline-style HTML，
  (4) 用 macOS 剪贴板的 «class HTML» 类型 + osascript 远程 Cmd+V，把内容半自动贴进公众号编辑器，
  (5) 用户保存草稿 → 公众号 App 群发。

  适用场景：你刚做完一个值得对外讲的项目，希望把它写成公众号文章并发布出去 —— 而你是个人订阅号（没 API）。

  显式触发：「把这个项目写成公众号文章发出去」「写一篇公众号实战记」「我的个人订阅号能不能自动发文」「项目做完了帮我写公众号推文 + 发」。

  不适用于：API 可用的认证服务号（直接走 `draft/add` 接口最快）、纯营销软文（这个 skill 假定有真东西讲）、非中文内容（模板和提示词都是中文）。
---

# /wechat-article-publish — 项目到公众号的半自动管道

你的角色是 **公众号推文 Lead**，把一个已完成的技术项目变成可发布的微信公众号长文 + 配图 + 半自动贴进编辑器的完整流程。

本 skill 最早是为 `demo-day-dossier`（奇绩 2026 春季 56 项目 DD）写实战记发文时搭建并泛化的。首跑产出：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>，从「项目做完」到「公众号上线」约 3 小时。

---

## 流水线阶段

```
[阶段 0] 项目盘点 — 拿到完成的项目（代码 / 部署 URL / 数据 / 截图）
        ↓
[阶段 1] 写叙事性 markdown 文章（钩子 → 痛点 → 方案 → 意义 → CTA）
        ↓
[阶段 2] 生成配图（封面 + 自定义插图 + 线上页面截图）
        ↓
[阶段 3] markdown → 公众号 inline-style HTML
        ↓
[阶段 4] 半自动贴进公众号编辑器（剪贴板 «class HTML» + osascript Cmd+V）
        ↓
[阶段 5] 用户保存草稿 → 公众号 App 群发
```

---

## 参数

- `$ARGUMENTS`：项目的工作目录 + 可选元数据。
  - 示例：`/wechat-article-publish ~/dev/Blog/demo-day-dossier`
  - 项目目录通常需要包含：source code、deployed URL、a clear "what we did" history
- 可选 flag：
  - `--article-only`：跳过阶段 4-5（只产出 markdown + HTML，不开浏览器）
  - `--images-only`：跳过 markdown 写作，只生成图片
  - `--author=<name>`：公众号文章作者署名
  - `--src-url=<url>`：原文链接（指向项目主页或 story 页）

---

## ⚠️ 关键前提（不读会踩坑）

### 0. 三个"经验值数百小时"的坑

| 坑 | 现象 | 解法 |
|----|------|------|
| 剪贴板类型错 | Cmd+V 后正文区**逐字显示 `<section><h1>...` 裸标签字符串** | 必须用 `osascript ... as «class HTML»`，**不能** `pbcopy`。`pbcopy` 给的是 `text/plain`，公众号编辑器当字符串处理。 |
| 浏览器选错 | Playwright Chromium 临时 profile 关浏览器 = 登录丢、selector 易碎 | 主流程用**日常 Chrome**（已是登录态，省扫码）。Playwright 当兜底。 |
| API 不开放 | 个人订阅号想调 `draft/add` 直接 401 | **不要试图走 API**。所有路径都是浏览器 UI 半自动。最后一步「群发」永远人工。 |

### 1. 个人订阅号能做什么 / 不能做什么

| 能 | 不能 |
|---|------|
| 写文章 + 配图准备 | 通过 API 创建草稿 |
| markdown → 公众号 HTML 转换 | 通过 API 群发 |
| 剪贴板自动设 HTML 类型 | 拿 AppSecret / access_token |
| 自动开浏览器 + Cmd+V | 跳过手动「群发」点击 |
| 提示用户去公众号 App 群发 | 替用户决定推送时机 |

### 2. 系统/工具依赖

```bash
# macOS 自带（不用装）
osascript  pbcopy  pbpaste

# 项目自身需要
python3 >= 3.9
pip3 install --user markdown          # md → HTML

# 可选（增强体验）
pip3 install --user playwright        # 想用 Playwright 兜底时
python3 -m playwright install chromium

# 系统设置 → 隐私与安全 → 辅助功能
# 给 Terminal / iTerm / 你的 shell host 勾上「辅助功能」权限
# 否则 osascript 发 keystroke 会失败
```

---

## 阶段 0 — 项目盘点

跑 skill 前确认手上有：

| 资产 | 说明 |
|------|------|
| **完成的项目** | 代码、数据、跑通的 demo |
| **部署 URL（至少 1 个）** | 文章里要给读者"现在就看"的入口 |
| **GitHub 仓库**（强烈建议） | 文末 CTA 让读者 fork |
| **关键数据 / 截图** | 自定义插图要用到的数字、对比、流程 |
| **一段"为什么做这件事"** | 文章开头的钩子来源 |

如果项目没部署、没数据，先回去补齐再来。这个 skill 不适合"包装空壳"。

---

## 阶段 1 — 叙事性 markdown 文章

### 1.1 五段结构（在 `templates/article.md.tmpl` 里）

```
1. 钩子（开篇）—— 描绘一个具体场景，让读者代入
   "X 天 / 一面墙 / 22 张截图..."

2. 痛点 —— 为什么这件事难，传统方案做不到
   "如果按一个项目 30 分钟算，56 个要 28 小时..."

3. 方案（主体）—— 你是怎么做的，分阶段展开
   "把它变成一个 SOP / Skill / 流水线..."
   每个阶段 1 个小标题 + 200-400 字
   关键阶段用 **「核心」徽章** + 图

4. 意义 —— 为什么这件事值得做
   "让一个人具备一个 N 人团队的产能 / 模板化可复用 / 开源..."

5. CTA（结尾）—— 读者下一步该干嘛
   "现在就看 → 链接 / clone 一份 / 用在你的下一个项目..."
```

### 1.2 文体风格约束

- **不要"科普口吻"**。读者已经知道 AI / 编程是什么，直接讲你做的事。
- **数字要具体**。"30 分钟"比"很快"好；"$10-50M"比"大几千万"好。
- **承认局限**。"selector 一年改 2-3 次"、"个人订阅号没 API"等坦诚记述，比假装一切顺利可信得多。
- **避免营销文案**。VC / 分析师式的冷淡口吻最稳。
- 用「中文角括号」不要 "英文双引号"，避免转义陷阱。

### 1.3 长度

公众号最佳长度是 **3000-5000 中文字**。低于 2000 字读起来单薄，超过 6000 字 80% 的读者滚不到底。

---

## 阶段 2 — 生成配图（7 张）

### 2.1 推荐配图清单

| # | 类型 | 文件名 | 尺寸 | 文章位置 |
|---|------|--------|------|---------|
| 1 | 封面 | `00-cover.png` | 1200×675 (16:9) | 公众号封面图 + 标题之后 |
| 2 | 线上 hero | `04-main-page.png` | 1280×800 | 钩子段落配图 |
| 3 | 流水线/SOP | `02-pipeline.png` | 1200×600 | 方案展开前 |
| 4 | 核心架构图 | `03-parallel.png` | 1200×700 | 最关键的方案段落 |
| 5 | 产出截图 | `05-deliverable.png` | 1280×800 | 产出段落 |
| 6 | 数据可视化 | `06-stats.png` | 1200×600 | 数据段落（柱状/金字塔/对比） |
| 7 | 线上 second hero | `07-secondary.png` | 1280×800 | 文末 CTA 之前 |

### 2.2 用模板生成自定义插图

模板在 `templates/`：

| 模板 | 用途 |
|------|------|
| `cover-1200x675.html.tmpl` | 16:9 封面 — 大标题 + 副标题 + 底部 pill |
| `pipeline-1200x600.html.tmpl` | 多阶段流水线 — N 个卡片 + → 连接，有 CORE 徽章 |
| `parallel-1200x700.html.tmpl` | 并行/对比 — 左边树状结构 + 右边维度框架 |
| `pyramid-1200x600.html.tmpl` | 金字塔/柱状统计 — N 行加权 + 数值 |

工作流：

```bash
# 1. 拷模板到你的项目 + 改文案
cp ~/.claude/skills/wechat-article-publish/templates/cover-1200x675.html.tmpl \
   /tmp/cover-mine.html
# 编辑 /tmp/cover-mine.html，改标题 / 副标题 / 配色

# 2. Chrome headless 渲染成 @2x PNG
~/.claude/skills/wechat-article-publish/scripts/render-image.sh \
  /tmp/cover-mine.html  ./images/00-cover.png  1200 675
```

### 2.3 截线上页面

```bash
# 项目主页
render-image.sh "https://your-project.pages.dev/"        ./images/04-main-page.png 1280 800

# 任意子页面
render-image.sh "https://your-project.pages.dev/details" ./images/05-deliverable.png 1280 800
```

⚠️ 截图前确认页面 hero 区在 1280×800 内能装下，否则用 1280×1200 等更高的高度，再在公众号编辑器里裁剪。

---

## 阶段 3 — markdown → 公众号 inline-style HTML

### 3.1 为什么必须 inline 样式

公众号编辑器粘贴时 **剥掉所有 `<style>` 块和 `<link>` CSS**。任何外部 / 内嵌 CSS 都丢。
**只有写到每个元素的 `style=""` 属性里的样式才被保留**。

### 3.2 转换器

```bash
# 转换 + 输出到文件
python3 ~/.claude/skills/wechat-article-publish/scripts/md2wechat.py \
  docs/your-article.md  /tmp/wechat-article.html

# 同时把图片 ./images/xx.png 改写为公开 URL（CF Pages / S3 / 你的 CDN）
# 编辑 md2wechat.py 顶部的 CF_BASE 常量改成你的域名
```

`md2wechat.py` 干的事：
1. markdown → HTML（用 python-markdown，支持 tables/fenced_code/lists）
2. 给每个 `<h1>` `<h2>` `<p>` `<table>` `<blockquote>` 等加 inline `style=""`
3. 把 `![alt](./images/x.png)` 改写为 `<img src="https://YOUR-CDN/images/x.png">`
4. 保证 `<pre>` 里的 `<code>` 不被双层 background 污染

### 3.3 自定义样式

`md2wechat.py` 里有 `STYLES` 字典，可以改：
- 颜色（默认浅色背景 + 暖灰文字 + #5eead4 强调色）
- 字号（默认 16px 正文 / 22px H2 / 13px code）
- 行距（默认 1.85）
- 引用块背景（默认 `#fef3c7` 浅黄）

---

## 阶段 4 — 半自动贴进公众号编辑器（核心）

### 4.1 剪贴板必须用 «class HTML» 类型

```bash
# ❌ 错的做法
pbcopy < /tmp/wechat-article.html   # text/plain，会显示裸标签字符串

# ✅ 对的做法
~/.claude/skills/wechat-article-publish/scripts/set-clipboard-html.sh \
  /tmp/wechat-article.html

# 验证
osascript -e 'return (clipboard info)'
# 期望输出：«class HTML», <字节数>
```

### 4.2 主流程：日常 Chrome + osascript（推荐）

```bash
# 1. 在日常 Chrome 打开公众号后台（你已是登录态）
open "https://mp.weixin.qq.com/cgi-bin/home"

# 2. 在 Chrome 里：左上「新的创作」→「图文消息」→ 等编辑器加载
# 3. 鼠标点正文区任意位置（确保光标进入编辑器，而不是停在标题/摘要输入框）

# 4. 远程发 Cmd+V
~/.claude/skills/wechat-article-publish/scripts/send-cmd-v.sh "Google Chrome"
```

### 4.3 兜底：Playwright（用户没日常 Chrome 登录态时）

```bash
python3 ~/.claude/skills/wechat-article-publish/scripts/wechat_publish.py docs/your-article.md
```

`wechat_publish.py` 会：
- 自动跑 `md2wechat.py`
- **用 pbcopy** 设剪贴板（弱版本，可能 fallback to plain）
- Playwright 打开 Chromium，等扫码登录
- 尝试跳「新建图文」（多个候选 URL；失败就 90 秒等用户手动跳）
- 尝试 selector 填标题 / 作者 / 摘要 / 原文链接
- 停下提示用户 Cmd+V，浏览器挂机 15 分钟

⚠️ 已知 Playwright 路径的弱点（**已实测踩过坑**）：
- 用 `pbcopy` 不是 `«class HTML»`，所以首次 Cmd+V 会贴成字符串
- 解决：脚本里用 `subprocess.run(["osascript", "-e", "set the clipboard to (read POSIX file ... as «class HTML»)"])`

### 4.4 用户在编辑器手动完成

| # | 动作 | 提示 |
|---|------|------|
| 1 | 检查正文 7 张图全加载 | 公众号会异步把外链图镜像到 mmbiz.qpic.cn，~10 秒 |
| 2 | 填标题 / 作者 / 摘要 | 上限：标题 64 字、摘要 120 字 |
| 3 | 填原文链接 | 指向 GitHub 或部署主页，文末「阅读原文」按钮就有了 |
| 4 | 上传封面图 | 选 `00-cover.png`，比例 16:9 |
| 5 | **右上「保存为草稿」** | 这一步最关键，别再被关浏览器了 |
| 6 | 群发 | 见阶段 5 |

---

## 阶段 5 — 群发

**这一步 skill 永远不替你做。** 理由：

- 个人订阅号一天 1 次群发额度，**错发不可撤回**
- 群发触发粉丝实时推送，必须人工最终确认
- 微信对脚本式群发有风控

正确流程：

1. 公众号 App → 草稿箱
2. 找到刚保存的草稿，点「发送预览」
3. 选自己微信号，发预览到自己手机
4. 在手机上完整看一遍：标题、摘要、封面、7 张图、表格、引用块、链接、阅读原文
5. **没问题后**，回到草稿，点「群发」

群发后立刻把公众号 URL 加到项目 README + 部署网站，闭环关上。

---

## 验证清单（群发前）

- [ ] 标题 ≤ 64 字
- [ ] 摘要 ≤ 120 字
- [ ] 封面图 16:9
- [ ] 正文 7 张图全在（不是 X 占位）
- [ ] 抓 preview URL 看 `mmbiz.qpic.cn` 图数 = 7、CF/S3 外链残留 = 0
  ```bash
  curl -sL "<preview-url>" -H 'User-Agent: ... MicroMessenger/8.0 ...' \
    | grep -c 'mmbiz.qpic.cn'
  ```
- [ ] H2 / blockquote / table 数量符合预期
- [ ] 「阅读原文」 button 指向部署主页
- [ ] 摘要 / 标题没拼写错

---

## 反模式（不要这么干）

- ❌ 用 `pbcopy` 设剪贴板（公众号编辑器解析成纯文本）
- ❌ 用 Playwright Chromium 当主路径（临时 profile = 登录丢；selector 易碎）
- ❌ 写营销软文（"赋能、闭环、革命"等词出现 = 关注度 -50%）
- ❌ 跳过 preview 直接群发（错发不可撤回）
- ❌ 试图调 `draft/add` API（个人订阅号 401）
- ❌ 让脚本替用户点「群发」按钮
- ❌ 把推文版长度做到 8000+ 字（80% 读者滚不到底）
- ❌ 自动给文章加表情符号 / 弹幕（让 AI 写的最容易翻车的部分）

---

## 文件清单

```
skills/wechat-article-publish/
├── SKILL.md                              ← 本文件
├── README.md                             ← 给访客 / 用户的简介
├── templates/
│   ├── article.md.tmpl                   ← 五段结构文章框架
│   ├── cover-1200x675.html.tmpl          ← 封面图模板
│   ├── pipeline-1200x600.html.tmpl       ← 流水线插图模板
│   ├── parallel-1200x700.html.tmpl       ← 并行/对比图模板
│   └── pyramid-1200x600.html.tmpl        ← 金字塔/统计图模板
├── scripts/
│   ├── md2wechat.py                      ← markdown → inline-style HTML 转换器
│   ├── wechat_publish.py                 ← Playwright 半自动发文（兜底）
│   ├── render-image.sh                   ← Chrome headless 渲染 PNG @2x
│   ├── set-clipboard-html.sh             ← 设剪贴板为 «class HTML»
│   └── send-cmd-v.sh                     ← 远程发 Cmd+V 到指定浏览器
└── examples/
    └── demo-day-dossier-2026/            ← 首跑案例
        ├── article.md                    ← 实战记原文
        └── README.md                     ← 案例说明
```

---

## 首跑参考

本 skill 处理的第一篇文章是 **「56 个路演项目，一个人，一晚上」**（基于 demo-day-dossier 项目）：

- 字数：约 4200 中文字
- 配图：7 张（1 封面 + 3 自定义插图 + 3 线上截图）
- markdown 源：见 `examples/demo-day-dossier-2026/article.md`
- 公众号文章：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>（2026-06-08 发布）
- 网页版：<https://qiji-roadshow-2026.pages.dev/story>
- 整体耗时：约 3 小时（含一次踩坑 + 重贴），熟练后 1.5 小时

实测数据：
- 7 张外链图 100% 镜像到 mmbiz.qpic.cn（永久 CDN）
- 0 张 CF 外链残留
- 10 H2 + 5 table + 3 blockquote 结构完整保留
