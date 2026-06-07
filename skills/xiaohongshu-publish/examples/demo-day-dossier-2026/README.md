# 首跑案例 · 一晚 DD 完 56 个 VC 项目

本目录是 `xiaohongshu-publish` skill 第一次实跑产出的参考。基于 [`demo-day-dossier`](../../../demo-day-dossier/) 项目改写。

## 数据

| 项 | 值 |
|----|----|
| 源公众号长文 | 4200 字（[story.md](../../../../docs/story.md)） |
| xhs 标题 | 19 字（限 20） |
| xhs 正文 | 695 字（限 1000） |
| hashtag | 6 个 |
| 配图 | 5 张 1080×1440 @2x = 2160×2880 |
| 整体耗时 | 约 90 分钟（首跑，含模板调色 + 校对） |

## 上线 URL（发完回填）

- 📰 小红书笔记：（发完回填）
- 📰 公众号原文：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>
- 🌐 项目主站：<https://qiji-roadshow-2026.pages.dev/story>
- 📦 项目仓库：<https://github.com/zhanglunet/demo-day-dossier>

## 文件

- [`post.json`](./post.json) —— 三段式文案（title / body / hashtags）
- [`images/`](./images/) —— 5 张 3:4 竖屏配图
  - `01-cover.png` —— 封面
  - `02-pain.png` —— 痛点（28h vs 30min）
  - `03-pipeline.png` —— 5 阶段流水线
  - `04-stat.png` —— 推荐度金字塔
  - `05-cta.png` —— 结尾 CTA

## 改写思路（公众号 → 小红书）

| 公众号原文 | 小红书改写 |
|------|---|
| 标题 38 字「我怎么用 Claude Skill + 7 路 AI 跑完了一份投资级 DD」 | 标题 19 字「AI 一晚 DD 完 56 个项目 🤯」 |
| 13 个 H2 小节 | 5 段（钩子 / 痛点 / 方案 / 数据 / CTA） |
| 详细 Phase 0-5 展开 | 1️⃣2️⃣3️⃣4️⃣5️⃣ 五行流水线 |
| 8 维度 DD 框架表 | 删（信息密度太高） |
| Python 代码块 | 删（小红书 UI 无等宽字体） |
| 估值对标表 | 删（细节太深） |
| 文末完整 GitHub URL | 「搜 demo-day-dossier」（小红书禁外链） |
| 「下一次 demo day 不必再蹲展区」金句 | 保留作为正文金句 |

## 视觉设计统一

5 张图共用：
- 深色 `#0a0f1e` 背景 + 暖色 `#fbbf24` accent
- 第一屏字号超大（70px+），3 屏深入信息密度
- `SLIDE NN / 05` 页脚（让读者知道还有几张）
- 一致的「数字加粗 + 金色」处理

## 反爬避坑（已用）

- ✅ 正文 0 外链
- ✅ 标题不含「震惊 / 揭秘 / 必看」
- ✅ 文末引导互动（评论区 / 收藏 / 关注），不提「私信」「加微信」
- ✅ hashtag 全部带 `#` 前缀
- ✅ 5 张图全部首发（未跨平台同步前发）

## 实测踩坑（首跑）

| 现象 | 原因 | 解法 |
|------|------|------|
| 标题 22 字超 2 字 | 「我用 + emoji」太重 | 去掉「我用」 |
| `.tmpl` 文件 Chrome headless 当文本渲染 | 文件扩展名不被识别为 HTML | 修 render-image.sh：非 `.html` 后缀的复制到 /tmp 强制 `.html` 后缀（commit `xxx`） |
