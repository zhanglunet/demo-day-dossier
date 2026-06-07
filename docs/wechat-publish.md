# 发公众号操作指南（个人订阅号 · 半自动）

> 个人订阅号没有 API 权限，所以这套流程是**浏览器 UI 半自动**：脚本帮你做掉
> 90% 的机械步骤（打开后台、扫码登录、跳新建图文、填标题/作者/摘要/原文链接、
> 粘贴 HTML 到剪贴板），剩下 10% 是你手动 Cmd+V + 检查 + 点保存草稿。

---

## 一次性准备

```bash
# 1. Playwright + Chromium（如果没装）
pip3 install --user playwright
python3 -m playwright install chromium

# 2. 确认 docs/story.md 和 docs/images/ 已是最新
git pull
```

依赖检查：

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
python3 -c "import markdown; print('OK')"
which pbcopy  # macOS 自带
```

---

## 一条命令搞定

```bash
cd /path/to/demo-day-dossier
python3 skills/wechat-article-publish/scripts/wechat_publish.py
```

它会做这些：

| 步骤 | 谁做 | 备注 |
|------|------|------|
| 把 `docs/story.md` 转成公众号内联样式 HTML | 脚本 | 输出到 `/tmp/wechat-article.html` |
| 把 HTML 拷到剪贴板 | 脚本 | macOS `pbcopy` |
| 启动 Playwright Chromium 打开公众号后台 | 脚本 | 非 headless，你能看见 |
| 等你扫码登录 | **你** | 公众号 App「我」→ 设置 → 扫一扫 |
| 跳到「新建图文」 | 脚本 | 多个候选 URL 兜底 |
| 填标题 / 作者 / 摘要 / 原文链接 | 脚本 | UI 可能改版，失败会提示 |
| 你在正文区按 Cmd+V 粘贴 | **你** | 剪贴板里就是 |
| 等编辑器自动拉外链图 | 自动 | 7 张 CF Pages 上的 PNG |
| 检查 + 保存草稿 | **你** | 右上「保存为草稿」 |
| 公众号 App 群发 | **你** | 草稿箱 → 发送预览 → 群发 |

---

## 配图怎么进文章

`docs/story.md` 里已经嵌好 7 张图：

```
![封面](images/00-cover.png)               ← 文首
![全景页](images/04-panoramic.png)         ← "一面墙 / 22 张截图" 段
![5 阶段流水线](images/02-pipeline.png)    ← Skill 是 SOP 之后
![7 路并行调研架构](images/03-parallel.png) ← Phase 3 开头
![DD 表](images/05-dd.png)                 ← Phase 4 段
![推荐度金字塔](images/06-pyramid.png)     ← 推荐度表格之后
![实战记网页版](images/07-story.png)       ← 文末 CTA 之前
```

转换时 `md2wechat.py` 把这些路径改写为：

```
<img src="https://qiji-roadshow-2026.pages.dev/images/00-cover.png">
```

外链图。公众号编辑器在粘贴时会**自动**把这些图镜像到微信自己的 CDN（你不需要
手动一张张上传）。

**如果外链图加载失败**（CF Pages 域名信誉、或编辑器版本问题）：

1. 打开 Finder，定位到 `docs/images/`
2. 在公众号编辑器里把外链图占位删除
3. 把图从 Finder 拖到编辑器对应位置

7 张图通常 < 5 分钟就拖完。

---

## 调试 selector（脚本说"填写失败"时）

公众号后台 UI 一年改 2-3 次，下面是 2026-06 时段的有效选择器：

| 字段 | 选择器（任选其一） |
|------|-------------------|
| 标题 | `input[name='title']` / `#title` / `textarea[name='title']` |
| 作者 | `input[name='author']` / `#author` |
| 摘要 | `textarea[name='digest']` / `#digest` / `textarea.js_digest` |
| 原文链接 | `input[name='content_source_url']` / `#js_content_source` |
| 正文编辑器 | iframe，复杂；脚本不自动操作，让你手动粘贴 |

如果脚本提示某字段"填写失败"，按这步排查：

```bash
# 让 Playwright 在 inspector 模式下跑，可在浏览器里实时看 selector
PWDEBUG=1 python3 skills/wechat-article-publish/scripts/wechat_publish.py
```

或者直接用 Chrome DevTools 打开公众号后台，右键标题输入框 → Inspect →
看 `name` 或 `id` 属性是否变了，对应改 `skills/wechat-article-publish/scripts/wechat_publish.py` 顶部
的元数据常量上方的 selector 列表。

---

## 纯人工备选（脚本完全跑不通时）

只用 `md2wechat.py` 拿到 HTML，剩下全手动：

```bash
# 转 HTML + 进剪贴板
python3 skills/wechat-article-publish/scripts/md2wechat.py docs/story.md | pbcopy
# 也可以输出到文件预览
python3 skills/wechat-article-publish/scripts/md2wechat.py docs/story.md > /tmp/preview.html
open /tmp/preview.html  # 在浏览器里看效果
```

然后手动：

1. 浏览器开 https://mp.weixin.qq.com 扫码登录
2. 新的创作 → 图文消息
3. 标题：`56 个路演项目，一个人，一晚上：我怎么用 Claude Skill + 7 路 AI 调研团跑完了一份投资级 DD`
4. 摘要：`一张展厅墙、一篇微信文章、22 张项目卡截图...`（见脚本里的 `ARTICLE_DIGEST`）
5. 原文链接：`https://qiji-roadshow-2026.pages.dev/story`
6. 正文区点光标进去 → Cmd+V（剪贴板里就是 HTML）
7. 等图加载 → 检查 → 保存草稿

---

## 群发前的最后检查

- [ ] 标题字数 ≤ 64（公众号限制）
- [ ] 摘要 ≤ 120 字
- [ ] 封面图比例 16:9（用 `00-cover.png`）
- [ ] 正文 7 张图全部加载成功（不能有 X 占位）
- [ ] 文末「阅读原文」链接 = `https://qiji-roadshow-2026.pages.dev/story`
- [ ] 在「发送预览」里给自己发一遍，手机上看完整效果
- [ ] 没问题后再点「群发」

---

## 关于自动「群发」

⚠️ **脚本不替你点群发按钮**。

理由：

1. 个人订阅号一天 1 次群发额度，错发不可撤回
2. 群发会触发粉丝实时推送，应该人工最终确认
3. 微信偶尔对脚本式的群发做风控

所以脚本最远只做到「保存草稿」。最后那一步「群发」永远是你自己在公众号 App
（或后台）点。

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `skills/wechat-article-publish/scripts/md2wechat.py` | markdown → 公众号 inline-style HTML 转换器 |
| `skills/wechat-article-publish/scripts/wechat_publish.py` | Playwright 半自动浏览器流程 |
| `docs/story.md` | 文章源（已内嵌 7 张图引用） |
| `docs/images/` + `output/images/` | 7 张配图（CF Pages 公开访问） |
| `docs/wechat-images.md` | 一图一位的对应说明（手动贴图时参考） |
| `docs/wechat-publish.md` | 当前文件 |
