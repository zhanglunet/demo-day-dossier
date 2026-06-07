#!/usr/bin/env python3
"""
由 dd_data.json + projects.json 构建 DD 的 markdown 报告。
之后用 pandoc 单独转为 .docx。

用法：
    python3 build_dd_report_md.py <workdir>

输出：
    output/dd_report.md
"""
import json
import sys
from collections import Counter
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    proj = json.load(open(workdir / "output" / "projects.json"))
    dd = json.load(open(workdir / "output" / "dd_data.json"))
    proj_map = {p["id"]: {**p, "zone": z["zone"]} for z in proj["zones"] for p in z["projects"]}
    meta = proj.get("meta", {})
    cohort = meta.get("cohort", meta.get("title", "Demo Day"))

    NL = "\n"
    md = []
    md.append("---")
    md.append(f'title: "{cohort} · 项目尽职调查报告 v1.0"')
    md.append('author: "DD by 7 路并行调研 agent · Lead 合成"')
    md.append(f'date: "{meta.get("date","")}"')
    md.append("---" + NL)
    md.append(f"# {cohort} · 项目尽职调查报告 v1.0" + NL)
    md.append("> **DD 方法论**：7 路并行调研 agent，按 8 维度评估：站点验证 / Repo 活跃度 / 团队评分 / 技术护城河 / 竞品 / TAM / 估值区间 / 推荐度" + NL)
    md.append("---" + NL)

    rec_dist = Counter(d.get("recommendation", 0) for d in dd)
    team_dist = Counter(d.get("team_score", 0) for d in dd)

    md.append("## 〇、执行摘要" + NL)
    md.append("### 推荐度分布" + NL)
    md.append("| 推荐度 | 含义 | 项目数 |")
    md.append("| --- | --- | --- |")
    labels = {5: "★★★★★ 强烈推荐", 4: "★★★★ 关注", 3: "★★★ 可观察", 2: "★★ 高风险", 1: "★ 信息不足"}
    for r in [5, 4, 3, 2, 1]:
        md.append(f"| {r} | {labels[r]} | {rec_dist.get(r, 0)} |")

    md.append(NL + "### 团队评分分布" + NL)
    md.append("| 团队分 | 项目数 |")
    md.append("| --- | --- |")
    for s in [5, 4, 3, 2, 1]:
        md.append(f"| {s} ●●●●● | {team_dist.get(s, 0)} |")

    md.append(NL + "### 强烈推荐 (rec=5)" + NL)
    md.append("| ID | 项目 | 创始人 | 估值区间 | 一句话判断 |")
    md.append("| --- | --- | --- | --- | --- |")
    top5 = sorted([d for d in dd if d.get("recommendation") == 5], key=lambda x: x["id"])
    for d in top5:
        p = proj_map.get(d["id"], {})
        founder = (p.get("founder") or "").split(" —")[0].split("(")[0].strip()
        val = d.get("valuation_range", "").replace("|", "/").split("（")[0].split("(")[0].strip()[:60]
        verdict = d.get("verdict", "").replace("|", "/").strip()[:80]
        md.append(f"| {d['id']} | **{d['name']}** | {founder} | {val} | {verdict} |")

    md.append(NL + "### 高风险预警 (rec=1-2)" + NL)
    md.append("| ID | 项目 | 推荐度 | 风险摘要 |")
    md.append("| --- | --- | --- | --- |")
    warn = sorted([d for d in dd if d.get("recommendation", 5) <= 2], key=lambda x: x["id"])
    for d in warn:
        risks = " / ".join(d.get("risks", [])[:2])[:100]
        md.append(f"| {d['id']} | **{d['name']}** | {'★'*d.get('recommendation',0)} | {risks} |")

    md.append(NL + "---" + NL)

    for zone in proj["zones"]:
        md.append(f"## {zone['zone']} · {zone['theme']}（{zone['count']} 个项目）" + NL)
        for p in zone["projects"]:
            d = next((x for x in dd if x["id"] == p["id"]), None)
            if not d:
                continue
            rec = d.get("recommendation", 0)
            rec_label = "★" * rec
            star = "⭐" if rec >= 4 else ""
            md.append(f"### {star} {p['id']} {p['name']} — 推荐 {rec_label} | 团队 {'●'*d.get('team_score',0)}" + NL)
            md.append(f"**一句话判断**：{d.get('verdict','')}" + NL)
            md.append("| 维度 | 评估 |")
            md.append("| --- | --- |")
            md.append(f"| 创始人 | {(p.get('founder') or '—')} |")
            md.append(f"| 一句话定位 | {p.get('tagline') or '—'} |")
            md.append(f"| 站点状态 | {d.get('website_status','—')} |")
            md.append(f"| Repo 状态 | {d.get('repo_status','—')} |")
            md.append(f"| 技术护城河 | {d.get('tech_moat','—')} |")
            md.append(f"| 市场 TAM | {d.get('market_tam','—')} |")
            md.append(f"| 估值区间 | **{d.get('valuation_range','—')}** |")
            md.append("")

            comps = d.get("competitors", [])
            if comps:
                md.append("**主要竞品**：")
                for c in comps[:5]:
                    if isinstance(c, dict):
                        name = c.get("name", "")
                        stage = c.get("stage", "")
                        note = c.get("note", "")
                        line = f"- **{name}**"
                        if stage:
                            line += f" ({stage})"
                        if note:
                            line += f" — {note}"
                        md.append(line)
                    else:
                        md.append(f"- {c}")
                md.append("")

            risks = d.get("risks", [])
            if risks:
                md.append("**风险**：")
                for r in risks[:3]:
                    md.append(f"- ⚠️ {r}")
                md.append("")

            strengths = d.get("strengths", [])
            if strengths:
                md.append("**优势**：")
                for s in strengths[:3]:
                    md.append(f"- ✅ {s}")
                md.append("")

            if p.get("site") or p.get("github"):
                md.append("**链接**：")
                if p.get("site"):
                    md.append(f"- 官网：{p['site']}")
                if p.get("github"):
                    md.append(f"- 仓库：{p['github']}")
                md.append("")
            md.append("")

    md.append("---" + NL)
    md.append("*报告版本 v1.0 · 不构成投资建议，仅作研究参考*" + NL)
    text = NL.join(md)
    out = workdir / "output" / "dd_report.md"
    out.write_text(text)
    print(f"✅ {out}  ({len(text)//1024} KB, {len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
