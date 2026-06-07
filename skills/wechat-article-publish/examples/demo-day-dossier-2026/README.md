# 首跑案例 · 56 个路演项目，一个人，一晚上

本目录是 `wechat-article-publish` skill 第一次实跑产出的参考。可用来：

- 看一个**真实落地**的五段式文章长什么样
- 对比自己写的文章长度 / 结构 / 节奏
- 直接拷出 markdown 改文案二次发布

## 数据

| 项 | 值 |
|----|----|
| 字数 | ~4200 中文字 |
| 配图 | 7 张（1 封面 + 3 自定义 + 3 线上截图） |
| H2 | 13 个 |
| 表格 | 5 张 |
| 引用块 | 3 个 |
| 整体耗时 | 3 小时（含 1 次踩坑 + 重贴；熟练后 1.5 小时） |

## 上线 URL

- 📰 公众号正式版：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>
- 🌐 网页版：<https://qiji-roadshow-2026.pages.dev/story>
- 📦 项目仓库：<https://github.com/zhanglunet/demo-day-dossier>

## 文件

- [`article.md`](./article.md) —— 完整 markdown 源（带 7 个 `![](images/...)` 引用）

配图本身在主项目仓库的 `output/images/` 目录（由 CF Pages 公开访问），见
<https://github.com/zhanglunet/demo-day-dossier/tree/main/output/images>。

## 实测踩坑记录

| 现象 | 原因 | 解法 |
|------|------|------|
| Cmd+V 后正文区显示 `<section><h1>...` 裸标签 | `pbcopy` 给的是 `text/plain` | 改用 `osascript ... as «class HTML»`（见 `scripts/set-clipboard-html.sh`） |
| Playwright Chromium 关掉后草稿丢 | 临时 profile 删除 = cookies 丢 | 用日常 Chrome 已登录态做主路径 |
| CF 外链图加载慢 | 公众号编辑器异步镜像，~10 秒 | 等等就好，不用手动重传 |
| 「新建图文」URL 自动跳转失败 | 公众号 UI 改版了 | 让用户手动点「新的创作 → 图文消息」90 秒兜底 |

## 五段结构对照

| 段 | 对应文章小节 |
|----|------|
| 钩子 | 「一面墙 / 一篇文章 / 22 张截图」 |
| 痛点 | 「这件事，本质上是一个调度问题」 |
| 方案 | 「Skill 不是 prompt 模板，是 AI 的 SOP」+ Phase 0-5 + DD 8 维度框架 |
| 意义 | 「这件事的意义」（4 个小标题） |
| CTA | 「下一次 demo day，你不必再蹲展区」 |

照这个结构改文案，下次写 YC W26 / 红杉 / 经纬路演的实战记会快很多。
