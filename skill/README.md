# demo-day-dossier · Claude Code Skill

把加速器 / Demo Day 素材（项目卡截图、展区照片、官方文章 URL）一次跑完，产出：

1. 全部项目的 **结构化 JSON 数据集**
2. **全景式可交互 HTML** 落地页
3. **可排序 / 可筛选的 DD 表**（7 路并行调研 agent 驱动）
4. **Word 深度报告**（全景 + DD 两本）
5. Excel / Numbers 可打开的 **CSV**
6. **一键部署** 到 Cloudflare Pages

首跑案例：**奇绩创坛 2026 春季路演日（56 个项目）** —— 见仓库根目录的 `examples/` 与 `output/`，
线上版：<https://qiji-roadshow-2026.pages.dev/>。

## 文件布局

```
skill/
├── SKILL.md                            ← Skill 入口（流水线 5 阶段定义）
├── README.md                           ← 当前文件
├── templates/
│   ├── index.html.tmpl                 ← 全景落地页模板
│   ├── dd.html.tmpl                    ← DD 表页面模板
│   ├── dd_agent_prompt.md              ← 每个 DD 调研 agent 的 Prompt 模板
│   ├── valuation_hints.md              ← 按行业的 Pre-money 估值对标表
│   └── projects.schema.json            ← 规范化数据集 JSON Schema
└── scripts/
    ├── build_panoramic.py              ← projects.json + 模板 → index.html
    ├── build_dd_html.py                ← projects.json + dd_data.json → dd.html
    ├── build_dd_csv.py                 ← dd_data.json → DD_table.csv
    ├── build_dd_report_md.py           ← dd_data.json → dd_report.md
    └── deploy_cloudflare.sh            ← 幂等部署 Cloudflare Pages
```

## 快速跑（手动执行版本）

```bash
# 阶段 2：构建全景落地页
python3 skill/scripts/build_panoramic.py /path/to/workdir

# 阶段 4（在 7 个 agent 回完之后）：构建 DD 页 + CSV + markdown 报告
python3 skill/scripts/build_dd_html.py      /path/to/workdir
python3 skill/scripts/build_dd_csv.py       /path/to/workdir
python3 skill/scripts/build_dd_report_md.py /path/to/workdir

# Word 报告（需先装 pandoc）
cd /path/to/workdir/output
pandoc report_v1.md  -o "路演项目全景调研报告_v1.0.docx" --standalone
pandoc dd_report.md  -o "路演项目尽职调查报告_v1.0.docx" --standalone

# 阶段 5：部署
skill/scripts/deploy_cloudflare.sh /path/to/workdir my-cohort-slug "v1.0 first publish"
```

但通常你不需要手动跑这些脚本 —— 用 Claude Code 直接调用本 skill，按 `SKILL.md` 的阶段流走就行。

## 安装为 Claude Code Skill

把 `skill/` 目录拷贝到 Claude Code 的 skills 目录：

```bash
cp -r skill ~/.claude/skills/demo-day-dossier
```

之后在 Claude Code 里就能用：

```
/demo-day-dossier ~/Downloads/yc-demo-day-w26 https://www.ycombinator.com/blog/yc-winter-2026-batch
```
