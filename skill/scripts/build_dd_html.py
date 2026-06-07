#!/usr/bin/env python3
"""
由 dd_data.json + projects.json 构建 DD 表页面（dd.html）。

用法：
    python3 build_dd_html.py <workdir>

要求 <workdir> 下存在：
    output/projects.json
    output/dd_data.json     — 7 个并行 DD agent 的合并输出

脚本会写出：
    output/dd.html
"""
import json
import os
import sys
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "dd.html.tmpl"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    proj_path = workdir / "output" / "projects.json"
    dd_path = workdir / "output" / "dd_data.json"
    if not proj_path.exists() or not dd_path.exists():
        print(f"ERROR: 需要 {workdir}/output/ 下同时存在 projects.json 与 dd_data.json")
        sys.exit(1)

    proj = json.load(open(proj_path))
    dd = json.load(open(dd_path))

    # 规范化 competitor 形状：有些 agent 会返回字符串而非 dict
    for d in dd:
        norm = []
        for c in d.get("competitors", []):
            if isinstance(c, dict):
                norm.append(c)
            elif isinstance(c, str):
                parts = [x.strip() for x in c.split("/")]
                if len(parts) >= 3:
                    norm.append({"name": parts[0], "stage": parts[1], "note": " / ".join(parts[2:])})
                elif len(parts) == 2:
                    norm.append({"name": parts[0], "stage": parts[1], "note": ""})
                else:
                    m = re.match(r"(.+?)\s*\(([^)]+)\)\s*(.*)", c)
                    if m:
                        norm.append({"name": m.group(1).strip(), "stage": m.group(2).strip(), "note": m.group(3).strip()})
                    else:
                        norm.append({"name": c, "stage": "", "note": ""})
        d["competitors"] = norm
    # 规范化后回写
    json.dump(dd, open(dd_path, "w"), ensure_ascii=False, indent=2)

    template = TEMPLATE.read_text()
    html = template.replace("/*__DD_PLACEHOLDER__*/[]", json.dumps(dd, ensure_ascii=False))
    html = html.replace("/*__PROJ_PLACEHOLDER__*/{}", json.dumps(proj, ensure_ascii=False))

    # cohort 元信息
    meta = proj.get("meta", {})
    title = meta.get("title", "Demo Day DD")
    cohort = meta.get("cohort", title)
    html = html.replace("<!-- DD_TITLE -->", f"{cohort} · 尽职调查表")
    html = html.replace("<!-- DD_H1 -->", f"{cohort} · 尽职调查表")
    html = html.replace("<!-- DD_BADGE -->", "DUE DILIGENCE v1.0")

    out = workdir / "output" / "dd.html"
    out.write_text(html)
    print(f"✅ {out}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
