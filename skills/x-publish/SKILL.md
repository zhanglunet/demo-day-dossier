---
name: x-publish
description: |
  把一篇已发布的长文（如公众号文章 / 博客）改写成 **X（Twitter）** 风格的 8-12 条英文 thread 并自动发布：
  (1) 长文 → thread JSON（hook + pain + approach + 4-6 步骤 + data + cta，每条 ≤280 字符），
  (2) 4 张 16:9 配图（cover + 流水线 + 数据 + cta），1200×675 @2x，
  (3) **双路径发布**：
      - 主路径：tweepy + OAuth 1.0a 全自动（X API Free Tier 每月 1500 条够用）
      - 兜底路径：osascript + 浏览器手动点 Tweet（没 dev 凭证时用）。

  适用场景：你已经在公众号 / 小红书 / 博客发了中文长文，想同步到 X 触达英文受众；或者你以英文受众为主，想要纯自动化的发文流程。

  显式触发：「同步到 X / Twitter」「发个 thread 推这件事」「把这篇推到 X 上」「the X / Twitter post」。

  不适用于：纯营销账号（X 也有低质量过滤）、视频推文（本 skill 只做图文）、Premium 长推文 25K 字（本 skill 走标准 280 字符 thread）、政治敏感内容。
---

# /x-publish — 长文到 X 英文 thread 的全自动管道

你的角色是 **X Thread Lead**，把一篇已发布的长文改写成英文 thread + 4 张 16:9 配图，**优先全自动通过 API 发布**。

本 skill 是 `wechat-article-publish` / `xiaohongshu-publish` 的姊妹 skill。三者的关系：

| | 公众号 | 小红书 | **X** |
|---|---|---|---|
| 字数 | 3000-5000 | ≤1000 | 单条 280 / thread 不限条数 |
| 风格 | 中文叙事 | 中文短句 + emoji | **英文 punchy thread** |
| 配图比例 | 16:9 横 | 3:4 竖 | 16:9 横 (1200×675) |
| 个人 API | ❌ | ❌ | **✅ Free 1500/月** |
| 半自动 | UI + 剪贴板 | UI + 剪贴板 | **全自动（API）** |
| 反爬 | 中 | 极严 | 弱（有 API 反爬轻） |

⚠️ **X 是这套 skill 里唯一能"按一下命令就发"的平台**。但前提是你完成一次性 OAuth 配置（5 分钟）。

---

## 流水线阶段

```
[阶段 0] 准备：长文 markdown + 部署 URL + X dev 凭证（一次性）
        ↓
[阶段 1] 长文 → thread JSON（8-12 条英文，每条 ≤280 字符）
        ↓
[阶段 2] 渲染 4 张 16:9 配图（cover + pipeline + stat + cta）
        ↓
[阶段 3] 发布（选一路）：
         主路径：post_thread_api.py（tweepy 全自动）
         兜底：post_thread_browser.py（osascript + 浏览器）
        ↓
[阶段 4] 自动验证：拉取已发推文 URL + 验证 thread 链式正确
```

---

## ⚠️ 关键前提

### 0. X API 凭证一次性配置（5 分钟）

1. 上 <https://developer.twitter.com/en/portal/dashboard> 申请 Free tier
2. 创建 Project → App
3. App 设置里开启 **User authentication settings**
   - App permissions：**Read and write**（必须 write 才能发推）
   - Type of App：Web App / Automated App or Bot
   - Callback URL：随便填一个（不会真用，比如 `http://localhost`）
4. **Keys and tokens** 页面拿 4 个值：
   - `API Key` (consumer_key)
   - `API Key Secret` (consumer_secret)
   - `Access Token` (access_token)
   - `Access Token Secret` (access_token_secret)
5. 存到 `~/.config/x-publish/credentials.json`：

```json
{
  "consumer_key": "xxx",
  "consumer_secret": "xxx",
  "access_token": "xxx-xxx",
  "access_token_secret": "xxx"
}
```

或者环境变量：

```bash
export X_CONSUMER_KEY=xxx
export X_CONSUMER_SECRET=xxx
export X_ACCESS_TOKEN=xxx
export X_ACCESS_TOKEN_SECRET=xxx
```

⚠️ Free tier 限制：
- 每月 1500 条 tweets（够发几十个 thread）
- 每个 thread 最长 100 条（实际很少需要超过 15）
- 媒体上传走 v1.1 endpoint，已包含

### 1. 内容差异：长文 → 英文 thread

| 公众号原文 | X thread 改写 |
|------|---|
| 4200 中文字 | 8-12 条英文 tweet，每条 ≤280 字符 |
| H2 小节 | 每个 tweet 独立成段 |
| 数据表格 | 数字直接写进 tweet：「11 strong-buy, 20 watch, 18 monitor」 |
| 中文金句 | 翻译 + 保留 punch |
| 代码块 | 一条 tweet 引用一段（用 ``` 标记） |
| 内链 / 外链 | 仅在最后一条放（避免算法降权） |

### 2. Thread 结构（8-12 条）

```
Tweet 1: hook + 1 attached image (cover)
         "I just X. Here's how. 🧵"

Tweet 2: pain — why this was hard
         specific numbers ("28 hours of work")

Tweet 3: insight — the unlock
         "It's actually a scheduling problem. ↓"

Tweet 4-8: phases (one per tweet)
         step by step, with one image attached at the most critical tweet

Tweet 9: data — the surprising result
         attach data image

Tweet 10: meta-reflection
         "What this changes about $domain"

Tweet 11 (final): CTA + link
         "Full source: github.com/..."
         "Read the long version: <url>"
         attach final image (cta)
```

### 3. 反规约要点

- 不要在每条都附图（dilutes attention）。**只在 1 (hook)、5 (most critical phase)、9 (data)、11 (cta) 这 4 条带图**
- 不要在中间条 tweet 放 URL（algo 会限流）
- 不要标记任何人（@somebody）—— 让 thread 靠内容自己流
- 不要用「BREAKING」「Just」开头（除非真的是新事件）

---

## 阶段 1 — 长文 → thread JSON

### 1.1 输出格式

`/tmp/x-thread.json`：

```json
{
  "tweets": [
    {"i": 1, "text": "...", "image": "01-cover.png"},
    {"i": 2, "text": "..."},
    {"i": 3, "text": "..."},
    {"i": 5, "text": "...", "image": "02-pipeline.png"},
    ...
    {"i": 9, "text": "...", "image": "03-stat.png"},
    {"i": 11, "text": "...", "image": "04-cta.png", "url": "https://..."}
  ]
}
```

### 1.2 校验

`md2thread.py` 会：
- 校验每条 ≤ 280 字符（含 URL 缩短长度 23 字符）
- 校验图片文件存在
- 警告超过 12 条（注意力衰减）
- 警告中间条带 URL（algo 风险）

---

## 阶段 2 — 渲染 4 张 16:9 配图

```bash
SKILL=~/.claude/skills/x-publish

# 4 张 16:9 1200×675 @2x = 2400×1350
for n in 01-cover 02-pipeline 03-stat 04-cta; do
  $SKILL/scripts/render-image.sh \
    $SKILL/templates/$n-1200x675.html.tmpl \
    ./images/$n.png  1200 675
done
```

### 模板设计要点

- **英文 first**：模板里的文案直接是英文
- **简洁标题 + 1 行 subtitle + 数字**
- **极高对比度**（X 在小屏 / dark mode 都常见）
- **品牌色一致**：cover / pipeline / stat / cta 用同一套配色

---

## 阶段 3 — 发布（API 优先）

### 3.1 主路径：tweepy API 全自动

```bash
SKILL=~/.claude/skills/x-publish

# 一次性：装 tweepy
pip3 install --user tweepy

# 一键发整个 thread
python3 $SKILL/scripts/post_thread_api.py /tmp/x-thread.json ./images/

# 输出：
# ✅ Tweet 1/11 posted: https://twitter.com/u/status/123...
# ✅ Tweet 2/11 posted: https://twitter.com/u/status/124...
# ...
# 🎉 Thread complete. Root URL: https://twitter.com/u/status/123...
```

脚本干的事：
1. 加载凭证（从 `~/.config/x-publish/credentials.json` 或环境变量）
2. 用 OAuth 1.0a 初始化 tweepy.Client + tweepy.API
3. 对每条带图的 tweet：先调用 v1.1 `media/upload` 上传图，拿 media_id
4. 调用 v2 `tweets` endpoint 发推：
   - 第 1 条：`text` + 可选 `media.media_ids`
   - 第 N 条（N>1）：上面 + `reply.in_reply_to_tweet_id = 上一条的 id`
5. 每条之间 sleep 0.5s（避免 rate limit）
6. 任一条失败：报告状态 + 给出已发的 thread 起点 URL，不重发

### 3.2 兜底路径：浏览器手动

如果没 API 凭证 / 想人工 review 每条：

```bash
python3 $SKILL/scripts/post_thread_browser.py /tmp/x-thread.json ./images/

# 流程：
# 1. 打开 x.com/compose/tweet
# 2. 让用户登录
# 3. 一条一条提示：
#    "Tweet 1/11: 文本已在剪贴板（Cmd+V）+ 拖图 01-cover.png + 点 Tweet"
#    "Tweet 2/11: 文本剪贴板已切 + 点回复 + Cmd+V + Tweet"
#    ...
```

慢但安全 —— 每条用户人工 review。

---

## 阶段 4 — 自动验证

发完后跑：

```bash
python3 $SKILL/scripts/verify_thread.py <root_tweet_id>
```

会拉取 thread 链，验证：
- 所有条都成功
- reply chain 正确
- 媒体附件都在
- 输出每条的 URL 列表方便回填 README

---

## 反模式

- ❌ 把中文 thread 直接发到 X（英文受众读不下去 = 互动 0）
- ❌ 每条都带图（注意力分散）
- ❌ 中间条带 URL（算法降权）
- ❌ 用 BREAKING / JUST / 🚨 开头（钓鱼标签）
- ❌ thread 超过 15 条（70% 用户滚不到底）
- ❌ 在 hook 里写完所有信息（thread 没 cliffhanger 不会有人继续看）
- ❌ 把 4 张图全塞第 1 条（X 单条最多 4 图，但视觉密度太高）
- ❌ 凭证 commit 到 repo（用 `~/.config/` 或环境变量）

---

## 文件清单

```
skills/x-publish/
├── SKILL.md                              ← 本文件
├── README.md
├── templates/
│   ├── thread.md.tmpl                    ← thread 结构模板
│   ├── cover-1200x675.html.tmpl          ← cover 图
│   ├── pipeline-1200x675.html.tmpl       ← 5 阶段流水线
│   ├── stat-1200x675.html.tmpl           ← 数据/金字塔
│   └── cta-1200x675.html.tmpl            ← CTA / GitHub 二维码风
├── scripts/
│   ├── md2thread.py                      ← 长文 → thread JSON 校验器
│   ├── post_thread_api.py                ← tweepy 全自动主路径
│   ├── post_thread_browser.py            ← osascript 兜底
│   ├── verify_thread.py                  ← 拉 thread 验证
│   ├── render-image.sh                   ← symlink wechat 同款
│   ├── set-clipboard-text.sh             ← symlink xhs 同款
│   └── send-cmd-v.sh                     ← symlink wechat 同款
└── examples/
    └── demo-day-dossier-2026/            ← 首跑案例
        ├── thread.json                   ← 10 条英文 thread
        ├── images/                       ← 4 张 1200×675 @2x PNG
        └── README.md
```

---

## 首跑参考

「I just DD'd 56 startups in one night with Claude. Here's how 🧵」基于 demo-day-dossier：

- 10 条 thread，每条 200-275 字符
- 4 张 16:9 配图（cover / pipeline / stat / cta）
- 最后一条带 GitHub URL + 主页 URL
- API 发布耗时：~8 秒（10 条 × 0.8s 每条）
- 浏览器兜底耗时：~5 分钟（含登录 + 10 次人工点 Tweet）
