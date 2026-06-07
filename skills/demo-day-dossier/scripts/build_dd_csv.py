#!/usr/bin/env python3
"""
由 dd_data.json + projects.json 构建 Excel / Numbers 可打开的 CSV。

用法：
    python3 build_dd_csv.py <workdir>

输出：
    output/DD_table.csv
"""
import json
import sys
import csv
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    proj = json.load(open(workdir / "output" / "projects.json"))
    dd = json.load(open(workdir / "output" / "dd_data.json"))
    proj_map = {p["id"]: {**p, "zone": z["zone"]} for z in proj["zones"] for p in z["projects"]}

    out = workdir / "output" / "DD_table.csv"
    dd_sorted = sorted(dd, key=lambda x: x["id"])
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "ID", "分区", "项目名", "一句话定位", "创始人", "站点状态", "Repo状态",
            "团队评分", "技术护城河", "TAM", "估值区间", "推荐度", "一句话判断",
            "风险1", "风险2", "风险3", "优势1", "优势2", "优势3",
            "竞品(top3)", "官网", "GitHub",
        ])
        for d in dd_sorted:
            p = proj_map.get(d["id"], {})
            risks = list(d.get("risks", [])) + ["", "", ""]
            strs = list(d.get("strengths", [])) + ["", "", ""]
            comps = d.get("competitors", [])
            comp_str = " / ".join(
                f"{c.get('name','')} ({c.get('stage','')})" if isinstance(c, dict) else str(c)
                for c in comps[:3]
            )
            w.writerow([
                d["id"], d["id"][0], d.get("name", ""),
                p.get("tagline", ""),
                (p.get("founder") or "").split(" —")[0][:40],
                d.get("website_status", "")[:80],
                d.get("repo_status", "")[:80],
                d.get("team_score", ""),
                d.get("tech_moat", ""),
                d.get("market_tam", ""),
                d.get("valuation_range", ""),
                d.get("recommendation", ""),
                d.get("verdict", ""),
                risks[0], risks[1], risks[2],
                strs[0], strs[1], strs[2],
                comp_str,
                p.get("site", ""),
                p.get("github", ""),
            ])
    print(f"✅ {out}  ({out.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
