# 首跑案例 · I DD'd 56 startups in one night with Claude

本目录是 `x-publish` skill 第一次实跑产出的参考。基于 [`demo-day-dossier`](../../../demo-day-dossier/) 项目重写为英文 thread。

## 数据

| 项 | 值 |
|----|----|
| 源公众号长文 | 4200 中文字 |
| Thread 长度 | 10 条英文 tweet |
| 单条字数 | max 275 / 上限 280 |
| 配图 | 4 张 16:9（1200×675 @2x = 2400×1350） |
| 上图位置 | Tweet 1 / 5 / 8 / 10（hook / 方法 / 数据 / CTA） |
| URL 计数 | 仅 Tweet 10 含 2 个 URL（最后一条放，避免算法降权）|

## 上线 URL（发完回填）

- 🐦 Thread root URL：（发完回填）
- 📰 公众号原文：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>
- 📕 小红书版：<https://www.xiaohongshu.com/discovery/item/6a2601120000000022009de4>
- 🌐 项目主站：<https://qiji-roadshow-2026.pages.dev/story>
- 📦 项目仓库：<https://github.com/zhanglunet/demo-day-dossier>

## 文件

- [`thread.json`](./thread.json) —— 10 条英文 thread 数据
- [`images/`](./images/) —— 4 张 1200×675 @2x 配图

## Thread 结构

| # | 角色 | 含图 | 摘要 |
|---|------|------|------|
| 1 | Hook | ✅ cover | "I DD'd 56 startups in one night with Claude. Here's how 🧵" |
| 2 | Pain | — | 28 hours of work, VCs need 5 analysts |
| 3 | Insight | — | "It's actually a scheduling problem" + parallel intro |
| 4 | Setup | — | What I walked out with: 22 screenshots + 1 article |
| 5 | Method | ✅ pipeline | 5 phases overview |
| 6 | Detail-1 | — | 7-agent fan-out as one message |
| 7 | Detail-2 | — | Valuation injection pattern (counter-intuitive) |
| 8 | Result | ✅ stat | 11/20/18/4/1 pyramid + "fan letter" line |
| 9 | Implication | — | What this changes for solo founders / scouts / journalists |
| 10 | CTA | ✅ cta | GitHub + live URL |

## 改写思路（中文长文 → 英文 thread）

| 公众号 | X thread |
|------|---|
| 中文叙事 4200 字 | 英文 punchy 10 tweets |
| 「奇绩 2026 春」具体语境 | "an accelerator demo day"（更普世）|
| 5 个 H2 阶段 | Tweet 5 列出 5 phases，1 张图，不展开 |
| 8 维度 DD 表 | Tweet 5 配图列全部 8 维（截图传更多信息）|
| 「中文角括号」 | 英文 quote marks |
| "Claude Skill / 7 路 AI" | "Claude Code Skill / 7 parallel agents" |
| 文末完整 GitHub URL | 只在 Tweet 10 放（避免中间条 URL 降权）|

## 反爬避坑（已用）

- ✅ 中间 9 条都没 URL
- ✅ 没有 BREAKING / Just / 🚨 钓鱼开头
- ✅ 没有 "RT if you like" 求互动话术
- ✅ 没有 @ 任何账号（强求互动）
- ✅ 10 条 thread 在阅读耐心阈值内（≤ 12）
- ✅ 4 张图分散在 1/5/8/10，注意力不分散

## 实测踩坑（首跑）

| 现象 | 原因 | 解法 |
|------|------|------|
| Tweet 10 超 6 字符 | 末条含 2 个 URL（各算 23 字符）+ 详细描述 | 删 ", 8 dimensions each"（图 03-stat 已示） |
| `dict \| None` 类型语法报错 | 本机 Python 3.9，PEP 604 要 3.10+ | 去掉类型注解 |

## 发布方式

两条路径：

**API 路径（推荐）**：

```bash
SKILL=~/.claude/skills/x-publish
# 一次性配置 ~/.config/x-publish/credentials.json
python3 $SKILL/scripts/post_thread_api.py thread.json images/
# 8 秒发完 10 条
```

**浏览器路径（无凭证时）**：

```bash
python3 $SKILL/scripts/post_thread_browser.py thread.json images/
# 一条条引导用户 Cmd+V + 拖图 + 点 Tweet
```
