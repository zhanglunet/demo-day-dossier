# xiaohongshu-publish · Claude Code Skill

把一篇已发布的长文（如公众号文章）改写成 **小红书** 风格的图文笔记并半自动发布。

姊妹 skill：[`wechat-article-publish`](../wechat-article-publish/)。两者搭配可以做"一次写作，多平台分发"。

针对 **个人账号**（无创作 API）设计。所有流程基于浏览器 UI，最后「发布」按钮永远人工。

## 流水线 4 阶段

```
长文 → 三段式改写（标题 ≤20 字 / 正文 ≤1000 字 / hashtag）
    → 5 张 3:4 竖屏配图
    → 半自动贴文本 + 用户拖图
    → 用户加 hashtag + 发布
```

详细 SOP 见 [`SKILL.md`](./SKILL.md)。

## 文件布局

```
skills/xiaohongshu-publish/
├── SKILL.md                          ← Skill 入口（4 阶段 SOP）
├── README.md                         ← 当前文件
├── templates/
│   ├── post.md.tmpl                  ← 三段式文案框架
│   ├── cover-1080x1440.html.tmpl     ← 封面
│   ├── quote-1080x1440.html.tmpl     ← 痛点 / 引用
│   ├── pipeline-1080x1440.html.tmpl  ← 流水线
│   ├── stat-1080x1440.html.tmpl      ← 数据
│   └── cta-1080x1440.html.tmpl       ← 结尾 CTA
├── scripts/
│   ├── md2xhs.py                     ← 长文 → {title, body, hashtags} JSON
│   ├── xhs_publish.py                ← Playwright 兜底
│   ├── render-image.sh               ← Chrome headless @2x 截图
│   ├── set-clipboard-text.sh         ← osascript 设纯文本剪贴板
│   └── send-cmd-v.sh                 ← 远程发 Cmd+V
└── examples/
    └── demo-day-dossier-2026/        ← 首跑案例（17 字标题 + 720 字正文 + 5 图）
```

## 关键约束

| | 小红书 | 公众号 |
|---|---|---|
| 标题 | ≤ **20 字** | ≤ 64 字 |
| 正文 | ≤ **1000 字** | 不限 |
| 封面比例 | **3:4 竖屏** | 16:9 |
| 外链 | ❌ **不允许** | ✅ |
| 个人账号 API | ❌ | ❌ |
| 反爬 | **极严** | 中等 |

⚠️ **小红书反爬比公众号严。** 任何全自动发布方案都会被风控。本 skill 把自动化做到「文本自动贴 + 浏览器开窗」就停，剩下手动。

## 快速跑

```bash
SKILL=~/.claude/skills/xiaohongshu-publish

# 阶段 1：长文 → 三段式
python3 $SKILL/scripts/md2xhs.py docs/your-article.md /tmp/xhs.json

# 阶段 2：生成 5 张图
for n in 01-cover 02-pain 03-pipeline 04-stat 05-cta; do
  $SKILL/scripts/render-image.sh $SKILL/templates/$n.html  ./xhs/$n.png  1080 1440
done

# 阶段 3：打开 creator + 文件夹
open "https://creator.xiaohongshu.com/publish/publish"
open ./xhs/

# 阶段 4：用户扫码 → 拖 5 张图 → 点标题框 → 脚本贴标题 → 点正文框 → 脚本贴正文
$SKILL/scripts/set-clipboard-text.sh "$(jq -r .title /tmp/xhs.json)"
$SKILL/scripts/send-cmd-v.sh "Google Chrome"
# （用户切到正文框）
$SKILL/scripts/set-clipboard-text.sh "$(jq -r .body /tmp/xhs.json)"
$SKILL/scripts/send-cmd-v.sh "Google Chrome"

# hashtag 用户手动加（小红书 # 是交互输入）
# 用户点「发布」（永远人工）
```

## 安装为 Claude Code Skill

```bash
cp -r skills/xiaohongshu-publish ~/.claude/skills/xiaohongshu-publish
```

## 首跑案例

「一晚 DD 完 56 个 VC 项目 🤯」基于 demo-day-dossier 项目重写：

- 标题：17 字 | 正文：720 字 | 配图：5 张 3:4
- 源公众号长文：4200 字
- 源文件：[`examples/demo-day-dossier-2026/`](./examples/demo-day-dossier-2026/)
