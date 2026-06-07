---
name: demo-day-dossier
description: |
  端到端的路演 / Demo Day 项目卷宗（Dossier）流水线。给定一组项目卡截图、展区墙照片、和/或官方文章 URL，自动产出：
  (1) 全部项目的结构化 JSON 数据集，(2) 全景式可交互 HTML 落地页，(3) 由 7 个并行调研 agent 驱动的可排序 / 可筛选 DD（尽职调查）表，(4) Word 深度报告，(5) 可在 Excel / Numbers 中打开的 CSV，(6) 一键部署到 Cloudflare Pages。

  适用场景：用户手上有加速器 / VC 基金 / Demo Day / 路演的素材（多张项目卡、现场展区照片、官方公告文章），希望"一次跑完"完成全景调研 + DD + 可发布的卷宗。

  显式触发：「把路演项目做成全景网页」「奇绩 / YC / 红杉 / 经纬路演 56 个项目梳理」「demo day projects 全部 DD 一遍」「做一个项目尽职调查表上线 Cloudflare」「analyze all roadshow projects and publish」。

  也适用于：用户手上有一目录的照片 + 微信 / Substack 文章 + 项目卡小程序截图，要求"全景页 + Word 报告 + DD 表 + 部署"一次到位。

  不适用于：单项目调研（请用 /research）、单公司 DD（直接 WebSearch + 聚焦 prompt）、对投资人会议的实时轮询（本 skill 无此能力）。
---

# /demo-day-dossier — 路演项目卷宗流水线

你的角色是 **Demo Day 调研 Lead**，负责编排一条 5 阶段流水线，把路演原始素材（项目卡截图 + 展区现场照 + 官方文章）转换为可发布、可查询、达到投资级别的项目卷宗。

本 skill 最早是为 **奇绩创坛 2026 春季路演日（56 个项目）** 搭建并加以泛化的。首次实跑产出：<https://qiji-roadshow-2026.pages.dev/> + DD 表 + 89KB 的 Word DD 报告 + CSV。

---

## 流水线阶段

```
[阶段 0] 盘点素材
        ↓
[阶段 1] 从图片 + 文章中抽取结构化项目数据
        ↓
[阶段 2] 构建全景落地页 (index.html) + 第一份 Word 报告 (vN.0)
        ↓
[阶段 3] 启动 7 路并行 DD 调研 agent（8 维度框架）
        ↓
[阶段 4] 构建 DD 表页面 (dd.html) + DD Word 报告 + CSV
        ↓
[阶段 5] 部署到 Cloudflare Pages
```

---

## 参数

- `$ARGUMENTS`：工作目录，包含项目卡图片、展区照片、和/或文章 URL。
  - 示例：`/demo-day-dossier ~/dev/Blog/260607奇绩路演`
  - 或：`/demo-day-dossier ~/Downloads/yc-demo-day-w26 https://www.ycombinator.com/blog/yc-winter-2026-batch`
- 可选 flag：
  - `--no-dd`：跳过阶段 3-4（只做素材入库 + 全景页 + 部署）
  - `--no-deploy`：跳过阶段 5
  - `--project-name=<slug>`：Cloudflare Pages 项目 slug（默认从工作目录文件夹名推导）
  - `--total=<N>`：来自官方源的项目总数（在展区墙不完整时使用）
  - `--cohort=<name>`：批次标签（如 "奇绩 2026 春季"、"YC W26"）

---

## 阶段 0 — 盘点素材

动手之前，先清点能用的东西：

```bash
# 在工作目录里
ls -la
# 常见模式：
#   *.jpg / *.png    — 项目卡截图、展区照片
#   *.docx           — 既有报告（可能是上一个版本）
#   subfolders/      — 按项目分组的图片目录
```

然后：
1. **找到展区墙 / 目录照片** — 通常是宽角度拍摄、列出所有分区（A 区 / B 区 / E 区 / F 区 或按赛道）的大照片。这张图是项目 ID → 项目名的索引图。用 Read 工具读取并抽 ID + 名。
2. **找到官方文章** — 通常是微信 / Substack / 加速器博客的长文，列出全部项目并附团队 bio。
   - **微信小贴士**：mp.weixin.qq.com 在用默认 UA 抓取时会返回"环境异常"验证页。要这样抓：
     ```bash
     curl -sL "https://mp.weixin.qq.com/s/..." \
       -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x1800313a) NetType/WIFI Language/zh_CN" \
       -o /tmp/wxarticle.html
     ```
     然后抽出 `id="js_content"` 节点，去标签，读纯文本。
3. **找出按项目的卡片图** — 加速器小程序截图是金矿。它们包含创始人 bio、融资金额、出让股权、公司主体、联系 QR，整齐的中文表单。

---

## 阶段 1 — 抽取结构化项目数据

构建一份规范化的 JSON。Schema 见 `templates/projects.schema.json`。每个项目的关键字段：

```jsonc
{
  "id": "A01",                  // 展区墙的「区号 + 编号」
  "name": "项目名",
  "tagline": "一句话定位",
  "direction": "产品方向",
  "founder": "主创始人 + 角色（UI 中高亮金框）",
  "team": "完整团队介绍段（创始人 + 关键成员）",
  "company": "公司主体名",
  "site": "https://...",        // 阶段 3 用 curl 核实
  "github": "https://github.com/...",
  "funding": "轮次 + 金额（如：种子轮 150 万美元）",
  "benchmarks": "对标产品",
  "highlight": "亮点 PR 时刻 / 证据",
  "star": true,                 // ⭐ 项目
  "double_star": false          // ⭐⭐ TOP1
}
```

**抽取建议：**

1. **读展区墙图** 枚举所有项目 ID 与粗略项目名。这是骨架。
2. **逐张读项目卡图**（`Read` 工具天然支持 JPG）。每张卡通常给出创始人姓名、学历、前雇主、融资意向、出让股权。
3. **与官方文章交叉对照** — 微信 / 博客正文通常有最完整的团队段和产品描述。**命名规范化时以文章为准**（创始人姓名、项目名罗马字拼写），不要相信 OCR。
4. **合并为规范化 JSON** 写到 `<workdir>/output/projects.json`。结构参考 `examples/projects.qiji-2026.json`。

**注意命名纠错** — 第一遍图片 OCR 通常有错。常见模式：
- 田阳川 vs 田阳（以文章为准）
- 摩泽分子 vs 摩湃分子 MolplusAI（以文章为准）
- 郜进飞 vs 郜迪飞（以文章为准）
- Chak Sun vs 孙长昊（以官方文章中的具名创始人为准——重名项目在不同 cohort 可能对应不同团队）
- 段泽泽 vs 段西泽（以文章为准）

构建完 JSON 后，打印一段统计：项目总数、有官网 URL 的、有 GitHub URL 的、有具名创始人的。

---

## 阶段 2 — 全景落地页 + 首份报告

### 2.1 生成 `index.html`

使用 `templates/index.html.tmpl` 模板。模板有两个占位：
- `/*__JSON_PLACEHOLDER__*/{}` — 替换为 projects.json 内容
- `<!-- TITLE -->` 等 — 替换为 cohort 标题

```bash
# 把 JSON 嵌入到 HTML
python3 -c "
import json, re
data = open('output/projects.json').read()
html = open('templates/index.html.tmpl').read()
html = html.replace('/*__JSON_PLACEHOLDER__*/{}', data)
open('output/index.html','w').write(html)
"
```

验收生成的页面：
- 4 个分区 Tab（彩色编码：A 蓝 / B 绿 / E 橙 / F 紫）
- 顶部 sticky 导航
- 每张卡片金色创始人框
- TOP 项目的星标 / 双星徽章
- 「🔍 DD 尽职调查表 →」链接指向 dd.html

### 2.2 生成 Word 报告 v1

跑 `scripts/build_panoramic.py`，由 `projects.json` 生成 markdown，然后用 pandoc 转 docx：

```bash
pandoc output/report_v1.md -o "output/路演项目全景调研报告_v1.0.docx" --standalone
```

用 python-docx 做一个简单的健全性检查：
```python
from docx import Document
d = Document(path)
assert len(d.paragraphs) > 100
```

---

## 阶段 3 — 7 路并行 DD 调研 Agent

这是本 skill 的核心。把 N 个项目分成 7 个 batch（每批约 8 个），然后并行启动 7 个后台 agent，每个负责一个 batch。

### 3.1 分批策略

对一个 56 项目 cohort（按 A11 + B19 + E12 + F12 分布）：

```python
batches = {
  'A':  A01-A11   (11),
  'B1': B01-B10   (10),
  'B2': B11-B19   (9),
  'E1': E01-E06   (6),
  'E2': E07-E12   (6),
  'F1': F01-F06   (6),
  'F2': F07-F12   (6),
}
```

把每个 batch 的项目子集写到 `/tmp/dd_batch_<id>.json`，agent 通过 `Read` 读取。

### 3.2 启动 7 个并行 agent

**一条消息里发 7 个 Agent tool 调用**（并行）。`subagent_type` 用 `general-purpose`。每个 agent 的 prompt 模板见 `templates/dd_agent_prompt.md`。每批要填的变量：
- `BATCH_ID`：A / B1 / B2 / E1 / E2 / F1 / F2
- `PROJECT_LIST`：人读的 ID + 项目名列表
- `INPUT_PATH`：`/tmp/dd_batch_<id>.json`
- `OUTPUT_PATH`：`/tmp/dd_results_<id>.json`
- `VALUATION_HINTS`：按分区的对标估值表（见模板）

使用 `run_in_background: true`。每个 agent 的预算：30 分钟内、≤25 次 WebSearch、≤15 次 Bash（curl）。

### 3.3 8 维度 DD 框架

每个 agent 对每个项目填写：

| # | 维度 | 怎么验证 |
|---|-----|---------|
| 1 | `website_status` | `curl -sI -L --max-time 8 <url>` → HTTP 码 + 重定向路径 |
| 2 | `repo_status` | `curl -s https://api.github.com/repos/<owner>/<repo>` → stars / forks / pushed_at |
| 3 | `team_score` (1-5) | 学历 + 前雇主 + 经验深度 + 角色覆盖度的综合评分 |
| 4 | `tech_moat` (≤40 字) | 网络效应 / 数据 / 专利 / 客户合同 |
| 5 | `competitors` (3-5 个) | `[{name, stage, note}]`；用 WebSearch 核实融资轮次 |
| 6 | `market_tam` | TAM + CAGR，一句话 |
| 7 | `valuation_range` | Pre-money USD 区间 + 对标依据 |
| 8 | `risks` / `strengths` 各 3 条 + `recommendation` (1-5) + `verdict` (≤30 字) |

按行业的估值参考表在 `templates/valuation_hints.md`。

### 3.4 等所有 7 个 agent 结束

**不要轮询**。harness 会在每个后台 agent 完成时通知你。等待期间可以预先搭好 DD HTML 骨架（阶段 4.1），结果一到就能填入。

当 7 个结果文件都到位（`ls /tmp/dd_results_*.json | wc -l` == 7），进入阶段 4。

---

## 阶段 4 — DD 表页面 + DD 报告

### 4.1 合并 + 规范化

```python
all_dd = []
for batch in ['A','B1','B2','E1','E2','F1','F2']:
    all_dd.extend(json.load(open(f'/tmp/dd_results_{batch}.json')))

# 规范化 competitor 形状（有些 agent 返回字符串而非 dict）
for d in all_dd:
    norm = []
    for c in d.get('competitors', []):
        if isinstance(c, dict):
            norm.append(c)
        elif isinstance(c, str):
            parts = [x.strip() for x in c.split('/')]
            if len(parts) >= 3:
                norm.append({'name': parts[0], 'stage': parts[1], 'note': ' / '.join(parts[2:])})
            elif len(parts) == 2:
                norm.append({'name': parts[0], 'stage': parts[1], 'note': ''})
            else:
                m = re.match(r'(.+?)\s*\(([^)]+)\)\s*(.*)', c)
                norm.append({'name': m.group(1), 'stage': m.group(2), 'note': m.group(3)} if m else {'name': c, 'stage': '', 'note': ''})
    d['competitors'] = norm

json.dump(all_dd, open('output/dd_data.json','w'), ensure_ascii=False, indent=2)
```

### 4.2 应用 DD 过程中发现的修正

Agent 经常会在调研中暴露数据错误。把这些修正回灌到 `projects.json`：
- 站点 URL 错 → 清空
- 创始人姓名错 → 更新
- 「pivot 到 Y」 → 更新 direction / tagline + 加一条 note

### 4.3 生成 `dd.html`

使用 `templates/dd.html.tmpl` 模板。两个占位：
- `/*__DD_PLACEHOLDER__*/[]` → 合并后的 DD JSON
- `/*__PROJ_PLACEHOLDER__*/{}` → projects.json

模板已自带的功能：
- 可排序的 8 列表格（点列头排序）
- 顶部 sticky 搜索框 + 分区筛选 + 推荐度筛选
- 点行打开右侧抽屉，显示完整 DD 详情（创始人块、风险、优势、竞品、链接）
- 4 色分区 pill（A 蓝 / B 绿 / E 橙 / F 紫）
- 响应式（小屏隐藏次要列）

### 4.4 生成 DD Word 报告 + CSV

跑 `scripts/build_dd_report_md.py` 生成按分区分组、带执行摘要表的 markdown DD 报告，然后 pandoc 转 docx：

```bash
pandoc output/dd_report.md -o "output/路演项目尽职调查报告_v1.0.docx" --standalone
```

再加一份 Excel / Numbers 可打开的 CSV：

```python
# 见 scripts/build_dd_csv.py
# 列：ID, 分区, 项目名, 一句话, 创始人, 站点状态, Repo 状态, 团队评分,
#     护城河, TAM, 估值区间, 推荐度, 一句话判断, 风险×3, 优势×3, 竞品×3, 官网, GitHub
```

### 4.5 互链

确保：
- `index.html` 顶部有「🔍 DD 尽职调查表 →」导航链接，指向 `dd.html`
- `dd.html` 顶部有「← 回到全景主页」回链，指向 `./`

---

## 阶段 5 — 部署到 Cloudflare Pages

### 5.1 鉴权检查

```bash
npx wrangler whoami
```

如未登录，提示用户在自己终端里输入 `! npx wrangler login` 走 OAuth 浏览器回调。

### 5.2 创建 Pages 项目（幂等）

```bash
npx wrangler pages project create <project-name> --production-branch=main 2>&1 || true
```

### 5.3 准备部署目录

只放对外公开的文件（不要把 .json 数据、.md 源、.docx 这类用户可能想 gate 的资产推上去）：

```bash
mkdir -p output/_deploy
cp output/index.html output/dd.html output/_deploy/
```

### 5.4 部署

```bash
npx wrangler pages deploy output/_deploy \
  --project-name=<project-name> \
  --branch=main \
  --commit-message="<版本号 + 变更摘要>"
```

### 5.5 验收线上 URL

```bash
curl -s -o /dev/null -w "Home  %{http_code}  %{size_download}B\n" https://<project-name>.pages.dev/
curl -s -o /dev/null -w "DD    %{http_code}  %{size_download}B\n" -L https://<project-name>.pages.dev/dd
```

两个都应该返回 200。Cloudflare 自动剥 `.html` 后缀，所以 `/dd.html` 会重定向到 `/dd`。

---

## 幂等性与版本号

- 本 skill 是 **可版本化的**：每次跑都升报告版号（`v1.0` → `v2.0` → `v3.0` ...）。需要手动覆盖时传 `--version=<vN.0>`。
- 若 `output/projects.json` 已存在，按 **增量更新** 处理：只 ingest 新素材（新图片、新文章 URL），diff 后合并。
- Cloudflare Pages 自带每次部署的 preview URL。生产 URL `https://<slug>.pages.dev/` 永远指向 `main` 的最新部署。

---

## 语气与文风约束

- 不要捏造创始人姓名、融资金额、客户证言。证据不明时写 `"未公开"` 或 `"待核实"`。
- 命名优先级：**官方文章 > 项目卡 > 展区墙 > 旧报告**。
- DD 的每个 `verdict` 字段必须是一句话有结论的判断 —— 不要写没有 punch line 的 hedging。
- DD 的推荐度分布要诚实，不要写成粉丝信。一个健康的 56 项目 cohort 通常 rec=5 占 10-20%、rec=4 占 30-40%、其余 rec≤3。
- 中文字符串里用「中文角括号」而非 "英文双引号"，避免 JSON / Python 转义陷阱。

---

## 一次成功跑完后的文件布局

```
<workdir>/output/
├── projects.json              ← 规范化结构数据集
├── dd_data.json               ← 7 个 agent 合并后的 DD 输出
├── index.html                 ← 全景落地页
├── dd.html                    ← DD 表页面
├── report_v1.md               ← 全景 Word 源
├── dd_report_v1.md            ← DD Word 源
├── DD_table.csv               ← Excel 可打开
├── 路演项目全景调研报告_v1.0.docx
├── 路演项目尽职调查报告_v1.0.docx
└── _deploy/                   ← Cloudflare 部署 staging（只放 .html）
    ├── index.html
    └── dd.html
```

---

## 本 skill 提供的可复用资产

| 路径 | 用途 |
|------|------|
| `templates/index.html.tmpl` | 全景落地页（卡片、分区 tab、创始人金框、TOP 推荐） |
| `templates/dd.html.tmpl` | DD 表页面（可排序表 + 抽屉） |
| `templates/dd_agent_prompt.md` | 7 个 DD agent 的系统 prompt 模板 |
| `templates/valuation_hints.md` | 按行业的 pre-money 对标估值参考 |
| `templates/projects.schema.json` | 规范化项目数据集的 JSON Schema |
| `scripts/build_panoramic.py` | projects.json → markdown 报告 |
| `scripts/build_dd_report_md.py` | dd_data.json + projects.json → DD markdown 报告 |
| `scripts/build_dd_csv.py` | dd_data.json → DD_table.csv |
| `scripts/deploy_cloudflare.sh` | 幂等的 Cloudflare Pages 部署 |
| `examples/projects.qiji-2026.json` | 参考结构化数据集（56 个项目） |

---

## 反模式（不要这么干）

- ❌ 不要每次跑都重 OCR 图片。缓存抽取结果。
- ❌ 不要把按项目卡的图片放到 `_deploy/`。它们通常含团队联系 QR，不该公开。
- ❌ 不要省略「与官方文章交叉对照」这一步。文章揭示了项目卡难以消歧的创始人姓名。
- ❌ 不要让 DD agent 串行。并行才是关键。
- ❌ 不要自动发布 Word DD 报告。先给用户看 —— DD 是用户可能想 gate 的资产。

---

## 首跑参考

本 skill 处理的第一个 cohort 是 **奇绩创坛 2026 春季路演日**：
- 4 个分区共 56 个项目
- 22 张细节项目卡截图
- 1 篇官方微信文章（mp.weixin.qq.com/s/03QbrGJc1zmpe94_51EQmA）
- 7 个 DD agent 总耗时 25-45 分钟
- 线上 URL：<https://qiji-roadshow-2026.pages.dev/> 与 `/dd`

参考输出结构见 `examples/projects.qiji-2026.json` 与 `examples/dd_data.qiji-2026.json`。
