# x-publish · Claude Code Skill

把一篇已发布的长文（公众号 / 博客 / markdown）改写成 **X（Twitter）** 风格的 **英文 8-12 条 thread** 并自动发布。

姊妹 skill 之于 [`wechat-article-publish`](../wechat-article-publish/) / [`xiaohongshu-publish`](../xiaohongshu-publish/)。

**这是四个发布 skill 里唯一能纯自动发的**，因为 X 给个人免费 API。

## 流水线 4 阶段

```
长文 → 英文 thread JSON（8-12 条，每条 ≤280 字符）
    → 4 张 16:9 配图（cover / pipeline / stat / cta）
    → API 全自动发布（tweepy + OAuth 1.0a）
    → 自动验证 + 返回 root tweet URL
```

详细 SOP 见 [`SKILL.md`](./SKILL.md)。

## 一次性准备（5 分钟）

```bash
# 1. 装 tweepy
pip3 install --user tweepy

# 2. 到 developer.twitter.com 申请 Free tier + Web App + Read and write 权限
#    拿 4 个值：consumer_key / consumer_secret / access_token / access_token_secret

# 3. 存到本机
mkdir -p ~/.config/x-publish
cat > ~/.config/x-publish/credentials.json <<EOF
{
  "consumer_key": "xxx",
  "consumer_secret": "xxx",
  "access_token": "xxx-xxx",
  "access_token_secret": "xxx"
}
EOF
chmod 600 ~/.config/x-publish/credentials.json
```

或者用环境变量：

```bash
export X_CONSUMER_KEY=xxx
export X_CONSUMER_SECRET=xxx
export X_ACCESS_TOKEN=xxx
export X_ACCESS_TOKEN_SECRET=xxx
```

## 一键发整个 thread

```bash
SKILL=~/.claude/skills/x-publish

# 1. 长文 → thread JSON（Claude 自己写，校验字符数 + 图片存在）
python3 $SKILL/scripts/md2thread.py thread.json /tmp/thread-validated.json

# 2. 渲染 4 张图
for n in 01-cover 02-pipeline 03-stat 04-cta; do
  $SKILL/scripts/render-image.sh $SKILL/templates/$n-1200x675.html.tmpl \
    ./images/$n.png  1200 675
done

# 3. 全自动发
python3 $SKILL/scripts/post_thread_api.py /tmp/thread-validated.json ./images/

# 输出：
# ✅ Tweet 1/10 → https://twitter.com/u/status/...
# ✅ Tweet 2/10 → https://twitter.com/u/status/...
# 🎉 Root URL: https://twitter.com/u/status/<root_id>
```

## 没 API 凭证时的兜底

```bash
python3 $SKILL/scripts/post_thread_browser.py /tmp/thread-validated.json ./images/

# 流程：
#   1. 打开 x.com/compose/tweet
#   2. 用户登录
#   3. 一条一条提示 Cmd+V + 拖图 + 点 Tweet
```

慢，但不需要 dev 凭证。

## 关键约束

| | X | 公众号 | 小红书 |
|---|---|---|---|
| API 个人可用 | **✅ Free 1500/月** | ❌ | ❌ |
| 单条字数 | 280 字符 | 不限 | ≤1000 |
| Thread 上限 | 100 条 | n/a | n/a |
| 媒体每条 | 4 图 | 任意 | 9 图 |
| 媒体比例 | 16:9 | 16:9 | 3:4 |
| 中间条带 URL | ⚠️ 限流 | ✅ | ❌禁 |

## 安装为 Claude Code Skill

```bash
cp -r skills/x-publish ~/.claude/skills/x-publish
```

之后在 Claude Code 里：

```
/x-publish ~/dev/my-project/docs/story.md
```

## 首跑案例

「I just DD'd 56 startups in one night with Claude. Here's how 🧵」基于 demo-day-dossier：

- 10 条 thread
- 4 张 16:9 配图
- API 发布耗时 8 秒
- 源文件：[`examples/demo-day-dossier-2026/`](./examples/demo-day-dossier-2026/)
