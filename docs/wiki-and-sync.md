# Wiki 知识库 + 同步工作流 (v6.0+)

> 本文档面向想把这套流水线复用到自己的 demo day / accelerator batch 的人。
> 描述 v6.0 新增的 **wiki 子站** 和 **projects.json ↔ wiki 自动同步机制**。

---

## 为什么要加 wiki?

5 阶段流水线产出的 `projects.json` + `index.html` 是**项目维度**的视图。但实际投资人/创业者关注的常常是**跨项目**的连接:

- 哪些项目的创始人来自同一所学校 / 前公司?
- 哪些项目在用同一类技术(EDA / 触觉传感器)?
- 哪些项目对标了相同的国际 benchmark?
- 哪个客户(比亚迪 / 中国移动)同时是多个项目的合作方?

wiki 子站把这些「人 / 概念 / 实体 / 文档」抽出来,**互相链接**,提供 4 个维度的导航视图 + 客户端全文检索。

---

## wiki 的 4 个维度

| 维度 | 在 wiki 里叫什么 | 来源 |
|---|---|---|
| 📄 文档 | `meetings/` | 5 份现场会议纪要(.md → entity 抽取) |
| 👤 人物 | `people/` | 演讲人 + 项目创始人 + 陆奇 + 6 明星校友(共 69) |
| 💡 概念 | `concepts/` | 「硅基生产力 / 研究型创业者 / Ghost UI / 奇绩投资条款」等 27 个 |
| 🏢 实体 | `entities/` | 54 项目 + 6 明星校友 + 客户 / 雇主 / 同盟方 共 84 个 |

每个页面都有自动生成的「在 N 个纪要中被提到 / 与 M 个其它实体共现」反向链接。

---

## 数据源拓扑

wiki 由 4 个 batch JSON 合并产生:

```
output/wiki/data/raw/
├── batch-1.json   ← 5 份会议纪要的 LLM 抽取(一次性,手工调优)
├── batch-2.json   ← 项目卡 + 路演照片 OCR(一次性,手工调优)
├── batch-3.json   ← 奇绩 + 陆奇 + 6 明星校友的 35 个一手来源调研(一次性,手工调优)
└── batch-4.json   ← 54 项目 entity + 创始人 person ★ 从 projects.json 自动派生
                     由 scripts/projects_to_batch4.py 生成
```

`merge.py` 把 4 个 batch dedupe + 合并 → `extracted.json` → `render.py` 渲染成最终 HTML。

**关键设计**:
- batch-1/2/3 是**一次性手工产出**,内容珍贵,`make sync` **不会动它们**
- batch-4 是**完全自动派生**,每次 sync 都会重新生成
- merge 时遇到同 slug 实体,**取最长 description**(所以你可以在 batch-3 写一段精雕的描述,batch-4 的程式化描述会因为更短而被覆盖)

---

## 同步工作流

### 单步操作

```bash
$EDITOR output/projects.json     # 1. 改数据(项目信息变更的唯一入口)
make sync                        # 2. 一键重生 wiki + 内嵌 JSON
git push                         # 3. CF Pages 自动部署
```

### `make sync` 内部 5 阶段

```
output/projects.json
        ↓ scripts/projects_to_batch4.py
output/wiki/data/raw/batch-4.json
        ↓ scripts/_lib/fix_json.py       (idempotent 修复)
        ↓ scripts/_lib/merge.py          (合 batch-1/2/3/4 → extracted.json)
        ↓ scripts/_lib/render.py         (渲染 5/69/27/84 HTML)
output/wiki/**/*.html  +  data/extracted.json  +  data/search-index.json
        ↓ 重新内嵌 projects.json 到 index.html / dd.html
done
```

### CI 守护

`.github/workflows/sync-check.yml` 在任何 PR 或 main push 时自动跑:
```bash
python3 scripts/sync-wiki.py
git status --porcelain output/     # 有任何 diff 就 fail
```

避免「改了 `projects.json` 但忘 `make sync`」这种低级错误,保证 GitHub main 上的 `projects.json` 永远与 wiki 一致。

---

## Slug 一致性

`scripts/projects_to_batch4.py` 维护两张映射表:

- **PROJECT_SLUG**: 项目 ID(A01/B02/...) → wiki entity slug
- **PERSON_SLUG**: 中文姓名 → wiki person slug

**为什么不让脚本自动 slug**?
- 中文姓名 → 拼音 slug 没有标准答案(王哲 = wang-zhe? wang-zhe-feika? 多人重名怎么办?)
- 项目名「数宇科技 vs 芯引力 vs 数宇」需要人为决定哪个是 canonical slug
- 一旦 slug 改了,所有反向链接都断,所以 slug 必须稳定

这两张表用人工维护,新项目接入时:
1. 编辑 `scripts/projects_to_batch4.py`,在 `PROJECT_SLUG` 加新的 ID → slug
2. 在 `PERSON_SLUG` 加新创始人姓名 → slug
3. `make sync` 验证

未在表里的项目 / 人物会被脚本警告 + 跳过 (`⚠ no slug for ...`)。

---

## 渲染特性

`scripts/_lib/render.py` 在原版 `notes-wiki` 渲染器基础上加了:

1. **多段 markdown**: entity / person / concept 的 `summary` / `description` / `definition` 按 `\n\n` 切多个 `<p>`。例如陆奇 5 段(当前职位 / 职业履历 / 个人背景 / 2026 演讲 / 投资哲学)
2. **内联粗体**: `**section**` → `<strong>section</strong>`(用于段首小标题)

如果想把 wiki 模板复用到其它项目,只需复制 `scripts/` 目录 + 改两张 slug 映射表。

---

## 飞书链接清理

会议纪要 .md 文件原本头部有 `> 智能纪要: [...](https://...feishu.cn/docx/...)` 一行。我们做了两件事:
1. 把这 5 个 .md 文件复制到 `output/wiki/sources/<slug>.md`,**剥掉飞书引用行**
2. wiki 渲染时,每份纪要页头部「原始文档链接」从飞书 URL 改为 `../sources/<slug>.md`

整个 `output/` 目录 grep "feishu" **零命中**。读者点链接看到的是仓库内同站的 markdown(CF Pages 默认 text/plain 渲染)。

---

## 接入自己的 demo day

如果你想复用这套 wiki 系统到自己的 demo day:

1. 跑通 `demo-day-dossier` 主流水线,产出 `projects.json`
2. 复制 `scripts/` 目录到你的项目根
3. 创建 `output/wiki/data/raw/batch-1.json`(可选,会议纪要抽取) — 用 `/notes-wiki` skill 跑
4. 编辑 `scripts/projects_to_batch4.py` 的 `PROJECT_SLUG` + `PERSON_SLUG` 映射
5. 跑 `python3 scripts/sync-wiki.py`
6. 浏览 `output/wiki/index.html`

只跑 batch-4(无 batch-1/2/3)也能用 —— 会得到一个纯项目 + 创始人的极简知识库,后续慢慢扩充。
