# 56 个路演项目，一个人，一晚上：我怎么用 Claude Skill + 7 路 AI 调研团跑完了一份投资级 DD

> 这是一份"AI 怎么把以前不可能的事变成日常"的实战记录。一张展厅墙、一篇微信文章、22 张项目卡截图，30 分钟后变成全景网页、可排序的 DD 表、89KB 的 Word 深度报告、和一份 Excel 表 —— 整套上线 Cloudflare。

---

## 一面墙 / 一篇文章 / 22 张截图

2026 年 6 月 7 日下午，奇绩创坛 2026 春季路演日。

展厅里一面巨大的墙，被切成四个色块：

- **A 区**：前沿科技，11 个项目 —— 核聚变、重力储能、EDA Agent、AI4Science 化学引擎
- **B 区**：具身智能与硬件，19 个 —— 机器人灵巧手、智能眼镜、群体机器人 OS
- **E 区**：Agent toB，12 个 —— 企业级 SaaS、出海销冠 Agent、工业 RaaS
- **F 区**：Agent toC，12 个 —— AI 心理陪伴、二次元硬件、AI 视频生产

每张卡片贴着项目名、创始人、一句话定位，还有一个小程序二维码。扫进去能看到完整的团队 bio、融资金额、出让股权。

走完一圈，我手机里有了：

- 22 张项目卡截图
- 1 张全景的展区墙照片
- 1 篇官方微信公众号长文（陆奇博士开场分享 + 56 个项目介绍）

然后问题来了：

**这 56 个项目，怎么一个个搞清楚？**

如果我是 VC，应该派 5 个分析师，每人花一周做 DD。如果我是一个手作研究的好奇之人，按一个项目 30 分钟算（看官网、查创始人、找竞品、估个估值），56 个项目大概 **28 小时**。

但我想做的是另一件事：

**把这 56 个项目，今晚就做完一份 DD。**

不是粗扫，是带 8 维度、有估值锚定、有竞品分析、有推荐度的、可发布的投资级别 DD。

听上去不可能。但 AI 让"不可能"变成了"30 分钟"。

---

## 这件事，本质上是一个调度问题

为什么一个人对 56 个项目无解？

因为人是**串行**的。你看一个项目、做完、再看下一个。28 小时是串行结构强加的下限。

但如果有 7 个分析师同时干呢？

56 ÷ 7 ≈ 8 个项目每人，每人 30 分钟做完，**总共还是 30 分钟**。

VC 派 5 个分析师就是这个道理。问题是我没有 5 个分析师。

但我有 Claude。

Claude Code 的一个关键特性：**你可以在一条消息里同时发起多个 sub-agent 调用，它们真的并发执行**。这意味着：

- 我可以一次性派 7 个 AI 调研员（subagents）出去
- 每个 AI 调研员都拿着同一份 SOP、同一份估值对标表、同一份 Prompt 模板
- 30 分钟后，7 份 JSON 同时回收
- 我作为 Lead，合并、互链、出报告

**等于在我的笔记本里塞了一个 7 人调研团。**

剩下的问题只有一个：**怎么把这套流程标准化，让它下次也能跑？**

答案叫 **Claude Code Skill**。

---

## Skill 不是 prompt 模板，是 AI 的 SOP

很多人对"提示词模板"很熟悉 —— 你写一段 prompt，下次复制粘贴改改参数。

**Skill 是给 AI 用的 SOP**。它打包了：

| 资产 | 角色 |
|------|------|
| `SKILL.md` | 流程定义 — 告诉 AI "这个任务分 5 个阶段，每个阶段做什么" |
| `templates/` | HTML 落地页模板、DD agent prompt、估值对标表、JSON Schema |
| `scripts/` | 构建 HTML、构建 CSV、构建 markdown 报告、部署 |
| `examples/` | 跑过一次的参考数据集，让 AI 知道目标长什么样 |
| 触发条件 | 写在 `SKILL.md` 顶部的 description —— Claude 自己识别"哎，用户这个需求该调我" |

我把这套流程封装成了一个叫 `demo-day-dossier` 的 Skill。

它的"职位描述"是：

> 给定一个工作目录，里面有项目卡截图、展区现场照、和/或官方文章 URL，自动产出全景式可交互 HTML 落地页、可排序 / 可筛选的 DD 表（由 7 路并行调研 agent 驱动）、Word 深度报告、CSV、并一键部署到 Cloudflare Pages。

**关键特性**：

- 写一次，下次 YC 路演、红杉 demo day、经纬路演 —— 同一个命令搞定
- AI 自己理解流程，自己拆任务，自己调度 agent
- 输出一致：所有跑出来的项目卷宗结构都相同，可比对、可归档

下面是这个 skill 5 个阶段的展开。

---

## 阶段 0：盘点 —— 在素材堆里找路线图

每次跑 skill，第一步是清点你给了它什么。

skill 会找三类东西：

**① 展区墙照片** —— 这是骨架。一张宽角度照片，上面写着 A11、B19、E12、F12 字样的 ID 和粗略项目名。AI 用 Read 工具直接读图，把 ID-名映射抽出来，作为后续的"主索引"。

**② 官方文章** —— 通常是微信公众号 / Substack / 加速器博客的长文，里面有完整的团队介绍段。命名规范化时**以文章为准**，因为图片 OCR 有错。

**③ 项目卡截图** —— 加速器的小程序截图是金矿。每张卡片包含创始人姓名、学历、前雇主、融资意向、出让股权 —— 整齐的中文表单。

这里有个小坑值得说：**微信公众号 mp.weixin.qq.com 用默认 User-Agent 抓回来的是「环境异常」验证页**。需要伪装成 iPhone 微信浏览器才能拿到正文：

```bash
curl -sL "https://mp.weixin.qq.com/s/..." \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ... \
      MicroMessenger/8.0.49 ..."
```

skill 把这个常见陷阱写进了 SOP，下次跑 YC 的 Substack 文章时不会再栽。

---

## 阶段 1：抽取 —— 把图片堆变成一个 JSON

skill 把所有抽出来的项目数据合并成一个规范化 JSON：

```json
{
  "id": "A01",
  "name": "VibeChip",
  "tagline": "AI 让 EDA 像写代码一样简单",
  "founder": "李 X · 清华 EE / 前 Cadence 高级工程师",
  "company": "VibeChip 北京",
  "site": "https://vibechip.ai",
  "github": "https://github.com/...",
  "funding": "种子轮 150 万美元",
  "star": true
}
```

JSON Schema 跟着 skill 走，确保每次产出的字段一致。

**关键决策**：命名优先级。当三个来源（展区墙、项目卡、文章）冲突时，**永远以官方文章为准**。比如：

| OCR 识别 | 文章真名 | 选谁 |
|---------|----------|------|
| 田阳 | 田阳川 | 田阳川 |
| 摩泽分子 | 摩湃分子 MolplusAI | 摩湃分子 |
| 郜进飞 | 郜迪飞 | 郜迪飞 |
| 段泽泽 | 段西泽 | 段西泽 |

这听上去像小事，但 56 个项目里有 5-8 个会踩到名字错配。一次性写进 SOP 之后，下次再跑就不用再想。

---

## 阶段 2：全景页 + 首份 Word 报告

JSON 装好之后，灌进一个 950 行的 HTML 模板，生成全景落地页：

- 4 色分区 Tab（蓝 A / 绿 B / 橙 E / 紫 F）
- 创始人金色卡片框，TOP 推荐打星
- 顶部 sticky 导航 + 一键跳转 DD 表
- 移动端响应式

同时跑 `build_panoramic.py` → 输出 markdown → pandoc 转 Word，**首版报告 v1.0 生成完毕**。

到这里，已经超出了"普通展厅笔记"的 95%。但只是热身 —— 重头戏在下一步。

---

## 阶段 3：7 路 AI 调研团出发

这是整个 skill 最关键的一步。

### 调度

把 56 个项目按分区切成 7 批：

```
A:  A01-A11   (11 个)
B1: B01-B10   (10 个)
B2: B11-B19   (9 个)
E1: E01-E06   (6 个)
E2: E07-E12   (6 个)
F1: F01-F06   (6 个)
F2: F07-F12   (6 个)
```

每个 batch 的项目子集写到 `/tmp/dd_batch_<id>.json`，agent 通过 Read 读取。

### 发车

**一条消息里发 7 个 Agent 调用**。这是关键 —— 一条消息发 7 个，就是并发；7 条消息每条 1 个，就是串行。

每个 agent 都拿到同一份 prompt 模板，模板里告诉它：

- 你是 2026 年 xx 路演项目的 DD 研究员
- 本批负责以下 N 个项目（列表）
- 输入数据在 `/tmp/dd_batch_X.json`
- 输出请写到 `/tmp/dd_results_X.json`
- 8 维度框架（下一节展开）
- 预算：30 分钟、25 次 WebSearch、15 次 Bash（curl）
- 估值要参考下面这张对标表（注入 prompt）

### 等待

harness 会在每个 agent 完成时主动通知 —— 我不需要轮询。等待期间我可以开始搭 DD 表的 HTML 骨架，结果一到就能填进去。

### 回收

当 7 份 JSON 都回来，merge 成一个 `dd_data.json`，进入阶段 4。

---

## DD 是怎么填出来的：8 维度框架

每个 agent 对每个项目要填这 8 个字段。每一项都有可验证的方法。

**1. 站点状态** —— `curl -sI -L --max-time 8 <url>`

查 HTTP 状态码和重定向链。结果像「200 OK / 站点活跃，标题 X」、「站点离线」、「无公开站点」。

**2. Repo 活跃度** —— `curl -s https://api.github.com/repos/<owner>/<repo>`

GitHub API 不需要 token（注意速率），拿到 stars / forks / pushed_at，判断代码是否活跃。

**3. 团队评分 1-5** —— 综合学历 + 前雇主 + 经验深度 + 角色覆盖度。

**4. 技术护城河 ≤40 字** —— 一句话：网络效应？数据壁垒？专利？客户合同？

**5. 竞品 3-5 个** —— 结构化 `[{name, stage, note}]`。stage 用 WebSearch 核实融资轮次。

**6. 市场 TAM** —— TAM + CAGR，一句话写完。

**7. 估值区间** —— pre-money USD 区间 + 类比 X 项目做依据。

**8. 风险 / 优势 / 推荐度 / 一句话判断** —— 风险 3 条、优势 3 条、推荐度 1-5、verdict ≤30 字。

### 最重要的小动作：估值不能让 agent 在真空里报价

所以 skill 把一张"按行业的 Pre-money 估值对标表"作为 prompt 的一部分注入：

| 赛道 | Seed Pre-money | 备注 |
|------|---------------|------|
| 早期 AI Agent SaaS | $10-50M | Coze / Dify 类 |
| 硬科技 / 前沿能源 | $20-100M | 核聚变 / 重力储能 |
| 具身硬件 / 灵巧手 | $20-200M | 关键部件 vs 本体 |
| AI4Science | $30-100M | 药物设计 / 分子力场 |
| EDA / 模拟芯片 Agent | $30-100M | Cadence 替代 |
| 智能眼镜 / 可穿戴 | $30-300M | Ray-Ban / Brilliant Labs |
| 实时语音 AI | $30-150M | Sesame / Sindarin |
| ... | ... | ... |

（一共 25 个赛道。）

Agent 报价时必须类比表里的某个邻居，不能凭空。这一个细节，把 hallucination 概率压低了一大半。

### 还有一条铁律

> 不要捏造创始人姓名、融资金额、客户证言。证据不明时写「未公开」「待核实」。

skill 把这条写进 `SKILL.md` 的"语气与文风约束"。Agent 出错的时候，宁可空着，不要瞎编。

---

## 阶段 4：合并 + DD 表 + Word + CSV

7 份 JSON 回到本地，merge 成一个 `dd_data.json`。

然后跑：

- `build_dd_html.py` → 生成 **DD 表页面**（8 列可排序 + 顶部搜索框 + 分区筛选 + 推荐度筛选 + 行点开右侧抽屉详情）
- `build_dd_csv.py` → 生成 **CSV**（21 列，Excel/Numbers 可打开）
- `build_dd_report_md.py` → 生成 **markdown 报告**（按分区分组、带执行摘要表、推荐度分布、TOP5、高风险预警）
- `pandoc` → markdown 转 docx，**89KB 的 DD Word 深度报告**

54 个项目（剩下 2 个信息不足未入 DD）的推荐度分布最终是：

| 推荐度 | 含义 | 项目数 |
|--------|------|--------|
| ★★★★★ | 强烈推荐 | 11 |
| ★★★★ | 关注 | 20 |
| ★★★ | 可观察 | 18 |
| ★★ | 高风险 | 4 |
| ★ | 信息不足 | 1 |

这是一个**健康的金字塔**：11 个强烈推荐 + 20 个关注 = 31 个上层意向，占比 57%。剩下 43% 落到可观察或更低 —— **不是粉丝信，是诚实的画像**。

如果 56 个项目全部 rec=5，那就不是 DD，是软文。

---

## 阶段 5：发布 —— 先 git push，再让 Cloudflare 自动接管

最初我用 wrangler 直接从本地推 Cloudflare Pages，部署很快。

但后来约定了一条新流程：**先推 GitHub → Cloudflare 自动监听 → 触发部署**。

理由很简单 —— `git commit` 是 source of truth，每个上线版本都对应一个 commit SHA。本地直推没有审计点，协作者推 PR 也不能预览。

接线只需要一次：

1. CF Dashboard 进 `qiji-roadshow-2026` 项目 → Settings → Builds & deployments → Connect to Git
2. 选 GitHub 仓库 `zhanglunet/demo-day-dossier`
3. **Build output directory 填 `output`**（注意：默认是 repo 根，必须改成 `output`）

之后 `git push` 就直接触发自动 build & deploy，30-60 秒内上线，连 GitHub Actions 都不需要。

要让这个设置自动化，我直接把 `wrangler.toml` 提交到 repo 里：

```toml
name = "qiji-roadshow-2026"
pages_build_output_dir = "output"
compatibility_date = "2026-06-07"
```

之后任何人 fork 这个 repo，连上 CF Pages，配置自动生效，不用再点 Dashboard 选选项。

---

## 最终产出清单

跑完一整套流水线，落地的东西：

| 资产 | 用途 |
|------|------|
| `projects.json` | 56 项目的规范化结构数据集 |
| `index.html` | 全景式可交互落地页 |
| `dd_data.json` | 54 项目的 8 维度 DD 数据 |
| `dd.html` | DD 表页面（可排序 + 抽屉详情） |
| `DD_table.csv` | Excel / Numbers 可打开 |
| `奇绩路演项目全景深度调研报告_v4.0.docx` | 全景 Word 深度报告 |
| `奇绩路演项目尽职调查报告_v1.0.docx` | DD Word 深度报告（89KB） |
| Cloudflare Pages 部署 | 全景页 + DD 表线上版 |

线上地址：

- 🌐 全景页：<https://qiji-roadshow-2026.pages.dev/>
- 🔍 DD 表：<https://qiji-roadshow-2026.pages.dev/dd>
- 📦 GitHub 仓库：<https://github.com/zhanglunet/demo-day-dossier>

---

## 这件事的意义

### 1. 让一个人具备一个调研团的产能

这套流程之前需要：

- 1 个 PM 负责盘点
- 5 个分析师做 DD
- 1 个总编排报告
- 1 周

现在需要：

- 1 个人 + Claude Code
- 30 分钟

不是减员增效那种话术。是**让以前不可能的事变成日常**。

### 2. 把「项目选择」从凭感觉变成凭数据

如果你是一个想关注早期 AI 创业的人，传统做法是：
- 看朋友圈推荐
- 看 PR 稿
- 凭印象

新做法是：
- 跑一遍 demo-day-dossier
- 看推荐度排序的 TOP10
- 翻每一个 verdict 一句话
- 决定要不要深聊

### 3. 模板化的 DD 可复用

这套 skill 不只是为奇绩准备的。下一次 YC W26 demo day、红杉 Pioneer Day、经纬创享会 —— 拿到项目卡和官方文章，命令一行：

```
/demo-day-dossier ~/Downloads/yc-w26 https://www.ycombinator.com/blog/yc-winter-2026
```

skill 自己跑完五个阶段。

### 4. 开源 = 共建

仓库已经在 GitHub 公开：<https://github.com/zhanglunet/demo-day-dossier>

里面包括：

- 完整 skill（`SKILL.md`、`templates/`、`scripts/`）
- 奇绩 2026 春的首跑参考数据（`projects.json` + `dd_data.json`）
- 真实产出（HTML、CSV、Word 报告）

clone 下来，拷贝到 `~/.claude/skills/demo-day-dossier`，就能用在自己的 demo day 上。

---

## 下一次 demo day，你不必再蹲展区

把项目卡照片扔进 skill。

30 分钟后，所有项目都摆在你面前 —— 一句话定位、创始人简介、估值区间、推荐度、风险摘要、官网状态、GitHub 活跃度，都在一个表里。

**你只需要做一件事**：看完 TOP10 的 verdict，决定下周想约谁喝咖啡。

这是 AI 真正改变工作方式的方式 —— 不是替你思考，是把"思考前必须先做的脏活"全部接走。

---

## 🔗 链接

- GitHub 源码：<https://github.com/zhanglunet/demo-day-dossier>
- 全景页：<https://qiji-roadshow-2026.pages.dev/>
- DD 表：<https://qiji-roadshow-2026.pages.dev/dd>
- 本文网页版：<https://qiji-roadshow-2026.pages.dev/story>

---

*仅供学习研究参考。DD 中的估值 / 推荐度是基于公开信息的二手分析，不构成投资建议。*
