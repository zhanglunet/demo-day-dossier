# demo-day-dossier

[![deploy](https://img.shields.io/badge/Cloudflare%20Pages-auto--deploy%20on%20push-orange)](https://qiji-roadshow-2026.pages.dev/)

> 把加速器 / Demo Day 的素材一次跑完，产出一份可发布、可查询、达到投资级别的项目卷宗。

这是一个 Claude Code Skill + 首跑案例的合集仓库：
- 📦 [`skills/demo-day-dossier/`](./skills/demo-day-dossier/) —— 通用流水线（Claude Code Skill 形式，5 阶段端到端编排）
- 🎬 [`examples/`](./examples/) —— 标准数据集示例（首跑：奇绩 2026 春，56 个项目）
- 📊 [`output/`](./output/) —— 首跑案例真实产出（HTML / JSON / CSV / Word）

🌐 **首跑线上版**：
- 全景页：<https://qiji-roadshow-2026.pages.dev/>
- DD 表：<https://qiji-roadshow-2026.pages.dev/dd>
- 📝 实战记（怎么做的）：<https://qiji-roadshow-2026.pages.dev/story> · [markdown 原文](./docs/story.md)
- 📰 **微信公众号推文版**：<https://mp.weixin.qq.com/s/oqPryhI-V3VOOmmoo-hFYg>（2026-06-08 发布于「张路的碎碎念」）
- 📕 **小红书图文笔记版**：<https://www.xiaohongshu.com/discovery/item/6a2601120000000022009de4>（2026-06-08 发布于「林雷」，19 字标题 + 695 字正文 + 5 张 3:4 竖图）

---

## 它能做什么

给定一个工作目录（项目卡截图 + 展区现场照 + 一篇官方文章 URL），跑完 5 个阶段，自动产出：

| # | 资产 | 说明 |
|---|------|------|
| 1 | `projects.json` | 全部项目的规范化结构数据集 |
| 2 | `index.html` | 全景式可交互落地页（4 色分区 Tab、TOP 推荐徽章、创始人金框） |
| 3 | `dd_data.json` + `dd.html` | 7 路并行调研 agent 产出的 8 维度 DD 表（可排序 / 可筛选 / 抽屉详情） |
| 4 | `路演项目全景调研报告_vN.0.docx` | 全景 Word 深度报告 |
| 5 | `路演项目尽职调查报告_vN.0.docx` | DD Word 深度报告 |
| 6 | `DD_table.csv` | Excel / Numbers 可打开的扁平表 |
| 7 | Cloudflare Pages 部署 | 一键发布全景页 + DD 表 |

---

## 5 阶段流水线

```
[阶段 0] 盘点素材：找到展区墙 + 官方文章 + 按项目卡片
       ↓
[阶段 1] 抽取结构化数据：图片 → 项目 JSON（与官方文章交叉对照命名）
       ↓
[阶段 2] 全景落地页 + 首份 Word 报告
       ↓
[阶段 3] 启动 7 个并行 DD 调研 agent（8 维度框架，30 分钟内并行完成）
       ↓
[阶段 4] DD 表页面 + DD Word 报告 + CSV
       ↓
[阶段 5] 部署到 Cloudflare Pages
```

详细执行细节、Prompt 模板、估值参考表见 [`skills/demo-day-dossier/SKILL.md`](./skills/demo-day-dossier/SKILL.md)。

---

## 8 维度 DD 框架

每个 agent 对每个项目自动填写：

| # | 维度 | 验证方式 |
|---|------|---------|
| 1 | 站点状态 | `curl -sI -L --max-time 8 <url>` 拿 HTTP 码 + 重定向 |
| 2 | Repo 活跃度 | `curl https://api.github.com/repos/<owner>/<repo>` 拿 stars / pushed_at |
| 3 | 团队评分 (1-5) | 学历 + 前雇主 + 经验深度综合 |
| 4 | 技术护城河 | ≤40 字一句话 |
| 5 | 竞品 (3-5 个) | `[{name, stage, note}]`，WebSearch 核实融资轮次 |
| 6 | 市场 TAM | TAM + CAGR 一句话 |
| 7 | 估值区间 | Pre-money USD 区间 + 对标依据（参考 [`valuation_hints.md`](./skills/demo-day-dossier/templates/valuation_hints.md)） |
| 8 | 风险 / 优势 (各 3) + 推荐度 (1-5) + 一句话判断 | DD 结论 |

---

## 仓库结构

```
.
├── README.md                                ← 当前文件
├── LICENSE                                  ← MIT
├── skills/                                  ← 仓库自带的三个 Claude Code Skill
│   ├── demo-day-dossier/                   ← Skill 1：路演项目卷宗流水线
│   │   ├── SKILL.md                        ← 5 阶段流水线 SOP
│   │   ├── README.md
│   │   ├── templates/                      ← HTML 模板 + DD agent prompt + 估值对标
│   │   └── scripts/                        ← build_panoramic/dd_html/dd_csv/dd_report/deploy
│   ├── wechat-article-publish/             ← Skill 2：项目到公众号推文的半自动管道
│   │   ├── SKILL.md                        ← 5 阶段 SOP（写文 / 配图 / 转 HTML / 贴 / 发）
│   │   ├── README.md
│   │   ├── templates/                      ← article.md + 4 个插图 HTML 模板（16:9）
│   │   ├── scripts/                        ← md2wechat / wechat_publish / render-image
│   │   │                                     / set-clipboard-html / send-cmd-v
│   │   └── examples/demo-day-dossier-2026/ ← 首跑案例：实战记 4200 字
│   └── xiaohongshu-publish/                ← Skill 3：长文到小红书图文笔记的半自动管道
│       ├── SKILL.md                        ← 4 阶段 SOP（改写 / 5 张竖图 / 贴 / 人工发）
│       ├── README.md
│       ├── templates/                      ← post.md + 5 个 3:4 竖屏插图模板
│       ├── scripts/                        ← md2xhs / xhs_publish / set-clipboard-text
│       │                                     ＋ symlink 复用 wechat 的 render-image/send-cmd-v
│       └── examples/demo-day-dossier-2026/ ← 首跑案例：xhs 笔记 19 字标题 + 5 图
├── examples/                                ← demo-day-dossier 的参考数据集
│   ├── projects.qiji-2026.json
│   └── dd_data.qiji-2026.json
├── docs/                                    ← 项目文档
│   ├── story.md                            ← 公众号实战记 markdown 源
│   ├── wechat-images.md                    ← 配图清单 + 排版指南
│   ├── wechat-publish.md                   ← 发文流程速查
│   └── images/                             ← 7 张配图（CF Pages 公开访问）
└── output/                                  ← 首跑案例真实产出（CF Pages 部署根）
    ├── index.html                          ← 全景页
    ├── dd.html                             ← DD 表
    ├── story.html                          ← 实战记网页版
    ├── images/                             ← 镜像 7 张配图（被 wechat 编辑器拉走）
    ├── projects.json / dd_data.json / DD_table.csv
    └── docs/*.docx                         ← Word 深度报告
```

---

## 安装与使用

### 1. 当作 Claude Code Skill 使用（推荐）

本仓库自带 **三个** skill，分别拷贝到 Claude Code 的 skills 目录：

```bash
# 路演项目卷宗流水线
cp -r skills/demo-day-dossier ~/.claude/skills/demo-day-dossier

# 项目到公众号推文的半自动管道
cp -r skills/wechat-article-publish ~/.claude/skills/wechat-article-publish

# 长文到小红书图文笔记的半自动管道
cp -r skills/xiaohongshu-publish ~/.claude/skills/xiaohongshu-publish
```

之后在 Claude Code 里直接调用：

```
/demo-day-dossier ~/Downloads/yc-demo-day-w26 https://www.ycombinator.com/blog/yc-winter-2026-batch
/wechat-article-publish ~/dev/my-finished-project
/xiaohongshu-publish ~/dev/my-finished-project/docs/story.md
```

| Skill | 任务 |
|-------|------|
| [`demo-day-dossier`](./skills/demo-day-dossier/SKILL.md) | 路演素材 → 全景页 + DD 表 + Word 报告 + 部署（5 阶段） |
| [`wechat-article-publish`](./skills/wechat-article-publish/SKILL.md) | 项目 → 公众号长文 + 7 张 16:9 配图 + 半自动贴（5 阶段） |
| [`xiaohongshu-publish`](./skills/xiaohongshu-publish/SKILL.md) | 长文 → 小红书 3 段式 + 5 张 3:4 竖图 + 半自动贴（4 阶段） |

**一次写作，多平台分发** —— 第三个 skill 设计为消费第二个 skill 的产出（公众号 markdown），用更短的标题、emoji 化的正文、3:4 竖图、跳过外链。

### 2. 手动跑脚本

```bash
# 准备工作目录
mkdir -p ~/myrun/output
# 把 projects.json 放进 ~/myrun/output/

# 阶段 2：全景落地页
python3 skills/demo-day-dossier/scripts/build_panoramic.py ~/myrun

# 你需要自己启动 7 个 DD agent（或一个一个调），把它们的输出合并为 dd_data.json

# 阶段 4：DD 页 + CSV + markdown 报告
python3 skills/demo-day-dossier/scripts/build_dd_html.py      ~/myrun
python3 skills/demo-day-dossier/scripts/build_dd_csv.py       ~/myrun
python3 skills/demo-day-dossier/scripts/build_dd_report_md.py ~/myrun

# 阶段 5：Word（需 pandoc）
cd ~/myrun/output
pandoc report_v1.md  -o "路演项目全景调研报告_v1.0.docx" --standalone
pandoc dd_report.md  -o "路演项目尽职调查报告_v1.0.docx" --standalone

# 阶段 5：本地直推（仅作首跑实验，正式发布请走 GitHub → CF）
skills/demo-day-dossier/scripts/deploy_cloudflare.sh ~/myrun my-cohort-slug "v1.0 首发"
```

---

## 发布流程：先 GitHub，再 Cloudflare 自动部署

本仓库的标准发布次序固定为 **`git push` → Cloudflare Pages 自动触发部署**。不要再从本地直接 `wrangler pages deploy`。

### 一次性接线（Cloudflare Dashboard）

实际做法是 **直接在既有的 `qiji-roadshow-2026` Pages 项目上挂 Git 集成**，保持线上域名不变（`qiji-roadshow-2026.pages.dev`），首跑历史 deploy 与新 GitHub-source deploy 都在同一个 project 的部署列表里。

1. 打开 **Cloudflare Dashboard → Workers & Pages → `qiji-roadshow-2026` → Settings → Builds & deployments → Connect to Git**。
2. 选 GitHub 账号下的 `zhanglunet/demo-day-dossier` 仓库，授权 CF 读取。
3. 配置：
   - **Production branch**：`main`
   - **Build command**：留空（纯静态站点）
   - **Build output directory**：`output`
   - **Root directory**：留空
4. 保存。首次自动触发 deploy 后，每条 `main` 上的新 commit 都会自动跑一次部署。

> 如果是全新项目，也可以走 **Create → Pages → Connect to Git** 流程新建一个 `demo-day-dossier` project，URL 会是 `demo-day-dossier.pages.dev`。两种做法等价 —— 选哪种取决于你想不想保留旧 URL。

### 此后每次发布

```bash
# 本地编辑 → 推到 GitHub
git add -A
git commit -m "update v5.0: ..."
git push
# Cloudflare 监听到 main 分支 push 后自动 build & deploy（30-60 秒）
```

无需 GitHub Secret、无需 `wrangler login`、无需 GitHub Actions —— CF 原生 Git 集成全包。

### 部署验证（可选）

```bash
# 看最近 deployment 的 Source 是否匹配最新 commit SHA
npx wrangler pages deployment list --project-name=qiji-roadshow-2026 | head -8

# 直接 curl 看线上是否反映了改动
curl -s https://qiji-roadshow-2026.pages.dev/README.md | head -5
```

> `skills/demo-day-dossier/scripts/deploy_cloudflare.sh` 仅保留作离线 / 无 GitHub 环境下的应急直推。

---

## 首跑案例：奇绩创坛 2026 春季路演日

> 56 个项目 · 4 大分区 · 1 篇官方微信文章 · 22 张项目卡截图 · 7 个 DD agent 并行 25-45 分钟

| 分区 | 主题 | 项目数 |
|------|------|--------|
| A 区 | 前沿科技 | 11 |
| B 区 | 具身智能与硬件 | 19 |
| E 区 | Agent toB | 12 |
| F 区 | Agent toC | 12 |
| **合计** | | **56** |

**Cohort 画像**：录取率 1%、Researcher Founder 占比 45%、硕士及以上 62%、海外团队 43%。

**DD 推荐度分布**（54 个项目，2 个信息不足未入 DD）：

| 推荐度 | 含义 | 项目数 |
|--------|------|--------|
| ★★★★★ | 强烈推荐 | 11 |
| ★★★★ | 关注 | 20 |
| ★★★ | 可观察 | 18 |
| ★★ | 高风险 | 4 |
| ★ | 信息不足 | 1 |

线上访问：
- 全景页 <https://qiji-roadshow-2026.pages.dev/>
- DD 表 <https://qiji-roadshow-2026.pages.dev/dd>

---

## 设计原则

- **命名优先级**：官方文章 > 项目卡 > 展区墙 > 旧报告。
- **不编造**：证据不明时写「未公开」「待核实」。
- **诚实分布**：DD 推荐度要呈金字塔（rec=5 约 10-20%、rec=4 约 30-40%、其余 rec≤3），不要写成粉丝信。
- **并行才划算**：7 个 DD agent 一定要 **一条消息里一次性发** 才并发，不要串行。
- **公开 vs 私有分清**：默认只把 `index.html` 与 `dd.html` 推到 CDN；JSON / Word 报告留本地，需要分享时手动 gate。

---

## 依赖

- **Python 3.9+**（脚本只用标准库）
- **pandoc**（markdown → docx）
  ```bash
  brew install pandoc          # macOS
  apt install pandoc           # Debian/Ubuntu
  ```
- **wrangler**（部署，可选）
  ```bash
  npm i -g wrangler            # 或用 npx wrangler
  npx wrangler login
  ```
- **Claude Code**（当 skill 用时）

---

## 许可

MIT — 见 [LICENSE](./LICENSE)。

数据声明：`output/` 与 `examples/` 中的 DD 评估、估值区间、推荐度仅作研究参考，**不构成投资建议**。
