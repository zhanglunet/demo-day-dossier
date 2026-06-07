#!/usr/bin/env python3
"""
由 projects.json 数据集构建全景式落地页（index.html）。

用法：
    python3 build_panoramic.py <workdir>

要求 <workdir> 下存在：
    output/projects.json        — 规范化数据集

脚本会写出：
    output/index.html           — 全景式落地页
"""
import json
import os
import sys
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "index.html.tmpl"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    proj_path = workdir / "output" / "projects.json"
    if not proj_path.exists():
        print(f"ERROR: {proj_path} not found")
        sys.exit(1)
    data = json.load(open(proj_path))
    template = TEMPLATE.read_text()

    # 把 JSON 嵌入模板占位
    html = template.replace("/*__JSON_PLACEHOLDER__*/{}", json.dumps(data, ensure_ascii=False))

    # cohort 元信息
    meta = data.get("meta", {})
    title = meta.get("title", "Demo Day Panoramic")
    subtitle = meta.get("subtitle", "")
    cohort = meta.get("cohort", title)
    badge = meta.get("badge", "DEMO DAY DOSSIER")

    html = html.replace("<!-- COHORT_TITLE -->", title)
    html = html.replace("<!-- COHORT_H1 -->", cohort)
    html = html.replace("<!-- COHORT_BADGE -->", badge)

    # 可选 cohort 开场致辞（chairman / GP）
    keynote = meta.get("keynote") or meta.get("lu_qi_keynote") or ""
    keynote_speaker = meta.get("keynote_speaker", "开场分享")
    if keynote.strip():
        callout = (
            f'\n  <div style="max-width:980px;margin:36px auto 0;padding:22px 26px;'
            f'background:rgba(94,234,212,0.06);border:1px solid rgba(94,234,212,0.2);'
            f'border-left:4px solid var(--accent);border-radius:12px;text-align:left;">\n'
            f'    <div style="font-size:11px;letter-spacing:2px;color:var(--accent);'
            f'font-weight:600;margin-bottom:10px;">{keynote_speaker}</div>\n'
            f'    <div style="color:rgba(232,236,245,0.92);font-size:14px;line-height:1.85;">{keynote}</div>\n'
            f'  </div>'
        )
        html = html.replace(
            "<!-- KEYNOTE_CALLOUT: removed by template. Re-inserted by build_panoramic.py if meta.keynote present. -->",
            callout,
        )
    else:
        # 无 keynote 时把占位注释清理掉，保持页面干净
        html = html.replace(
            "<!-- KEYNOTE_CALLOUT: removed by template. Re-inserted by build_panoramic.py if meta.keynote present. -->",
            "",
        )

    out = workdir / "output" / "index.html"
    out.write_text(html)
    print(f"✅ {out}  ({len(html)//1024} KB，嵌入 {len(json.dumps(data))} 字符 JSON)")


if __name__ == "__main__":
    main()
