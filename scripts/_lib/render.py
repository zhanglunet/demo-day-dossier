"""Render extracted JSON into static HTML wiki.

Usage:
    python3 scripts/render.py [--data data/extracted.json] [--out .]
                              [--site-title 'XX Wiki']
                              [--doc-label 文档]
                              [--anchor-name '']

Reads merged extracted.json and writes:
    index.html
    people/<slug>.html  +  people/index.html
    concepts/<slug>.html  +  concepts/index.html
    entities/<slug>.html  +  entities/index.html
    meetings/<slug>.html  +  meetings/index.html
    data/search-index.json     (for client-side search)

Note: the on-disk folder is always `meetings/` regardless of --doc-label
(the label only affects the UI text). This keeps merge.py / extracted.json
keys stable across runs.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


HEADER = """<!doctype html><html lang=zh-CN><head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel=stylesheet href="{base}assets/styles.css">
</head><body>
<header class=site>
  <a class=brand href="{base}index.html">{site_title}</a>
  <nav>
    <a href="{base}meetings/index.html">{doc_label}</a>
    <a href="{base}people/index.html">人物</a>
    <a href="{base}concepts/index.html">概念</a>
    <a href="{base}entities/index.html">实体</a>
  </nav>
  <div class=search>
    <input id=q placeholder="搜人物 / 概念 / 实体 / {doc_label}" autocomplete=off>
  </div>
</header>
<main{wide_attr}>
"""

FOOTER = """</main>
<footer class=site>
本地知识库 · 从 {n_meetings} 份{doc_label}抽取
</footer>
<script src="{base}assets/search.js" defer></script>
</body></html>"""


# Globals filled in main() from CLI args
SITE_TITLE = "知识库"
DOC_LABEL = "文档"
ANCHOR_NAME = ""  # empty => anchor blocks not rendered


def esc(s: str | None) -> str:
    return html.escape(s, quote=True) if s else ""


def shell(*, title: str, base: str, wide: bool = False) -> tuple[str, str]:
    n = shell.n_meetings  # type: ignore[attr-defined]
    hdr = HEADER.format(
        title=esc(title), base=base,
        site_title=esc(SITE_TITLE), doc_label=esc(DOC_LABEL),
        wide_attr=" class=wide" if wide else "",
    )
    ftr = FOOTER.format(base=base, n_meetings=n, doc_label=esc(DOC_LABEL))
    return hdr, ftr


def slug_url(kind: str, slug: str, depth: int = 1) -> str:
    up = "../" * depth
    return f"{up}{kind}/{slug}.html"


def render_tag_row(label: str, items: list[dict], kind: str, depth: int) -> str:
    if not items:
        return ""
    parts = [f'<div class=tag-row><span class=label>{label}</span>']
    for it in items:
        url = slug_url(kind, it["slug"], depth)
        cls = {"people": "person", "concepts": "concept", "entities": "entity"}.get(kind, "")
        parts.append(f'<a class="tag {cls}" href="{esc(url)}">{esc(it["name"])}</a>')
    parts.append("</div>")
    return "".join(parts)


def render_topic(t: dict, lookup) -> str:
    out = ['<div class=topic>']
    title = esc(t.get("name") or "议题")
    presenters = "、".join(t.get("presenters") or [])
    presenter_html = f' <span class=presenter>主讲：{esc(presenters)}</span>' if presenters else ""
    out.append(f'<h3>{title}{presenter_html}</h3>')
    summary = t.get("summary") or ""
    if summary:
        paras = re.split(r"\n\s*\n+", summary.strip())
        if len(paras) == 1:
            paras = [p.strip() for p in summary.strip().split("\n") if p.strip()]
        for p in paras:
            out.append(f'<p>{esc(p)}</p>')
    if ANCHOR_NAME:
        quotes = t.get("anchor_quotes") or []
        for q in quotes:
            out.append(
                f'<blockquote class=anchor>'
                f'<span class=anchor-name>{esc(ANCHOR_NAME)} —</span> {esc(q)}'
                f'</blockquote>'
            )
    actions = t.get("actions") or []
    if actions:
        out.append("<p style='margin-top:10px;color:var(--ink-soft);font-size:13px'><strong>跟进事项</strong></p>")
        out.append("<ul class=action-list>")
        for a in actions:
            assignee = esc(a.get("assignee") or "")
            task = esc(a.get("task") or "")
            out.append(f'<li><strong>{assignee}</strong>　{task}</li>')
        out.append("</ul>")
    docs = t.get("documents") or []
    if docs:
        out.append("<p style='margin-top:10px;font-size:13px'>")
        out.append("文档：")
        for i, d in enumerate(docs):
            if i: out.append("　·　")
            out.append(f'<a href="{esc(d.get("url",""))}" target=_blank rel=noopener>{esc(d.get("title","(链接)"))}</a>')
        out.append("</p>")
    out.append("</div>")
    return "".join(out)


def lookup_from(data) -> dict:
    return {
        "people": {p["slug"]: p for p in data["people"]},
        "concepts": {c["slug"]: c for c in data["concepts"]},
        "entities": {e["slug"]: e for e in data["entities"]},
        "meetings": {m["slug"]: m for m in data["meetings"]},
    }


def resolve_refs(names: list[str], registry: dict, name_to_slug: dict) -> list[dict]:
    seen = set()
    out = []
    for n in names or []:
        slug = name_to_slug.get(n)
        if slug and slug in registry and slug not in seen:
            seen.add(slug)
            out.append({"slug": slug, "name": registry[slug]["name"]})
    return out


def render_meeting(m: dict, lookup, name_maps) -> str:
    base = "../"
    hdr, ftr = shell(title=m["title"], base=base)
    out = [hdr]
    out.append(f'<h1>{esc(m["title"])}</h1>')
    meta_parts = []
    if m.get("date"): meta_parts.append(f'<span><strong>日期</strong>　{esc(m["date"])}</span>')
    if m.get("type"): meta_parts.append(f'<span><strong>类型</strong>　{esc(m["type"])}</span>')
    if m.get("host"): meta_parts.append(f'<span><strong>主持</strong>　{esc(m["host"])}</span>')
    if m.get("source_file"): meta_parts.append(f'<span><strong>源</strong>　{esc(m["source_file"])}</span>')
    out.append(f'<div class=meta>{"".join(meta_parts)}</div>')

    # source_url (renamed from feishu_doc_url for generality; accept both)
    src_url = m.get("source_url") or m.get("feishu_doc_url")
    if src_url:
        out.append(f'<p><a href="{esc(src_url)}" target=_blank>原始文档链接</a></p>')

    people_refs = resolve_refs(m.get("people_mentioned"), lookup["people"], name_maps["people"])
    concepts_refs = resolve_refs(m.get("concepts_mentioned"), lookup["concepts"], name_maps["concepts"])
    entities_refs = resolve_refs(m.get("entities_mentioned"), lookup["entities"], name_maps["entities"])

    out.append(render_tag_row("人物", people_refs, "people", 1))
    out.append(render_tag_row("概念", concepts_refs, "concepts", 1))
    out.append(render_tag_row("实体", entities_refs, "entities", 1))

    out.append("<h2>议题</h2>")
    for t in m.get("topics") or []:
        out.append(render_topic(t, lookup))

    out.append(ftr)
    return "".join(out)


def render_entity_like(e: dict, kind: str, mentions: list[dict], extra_meta: list[str]) -> str:
    base = "../"
    hdr, ftr = shell(title=e["name"], base=base)
    out = [hdr]
    out.append(f'<h1>{esc(e["name"])}</h1>')
    aliases = e.get("aliases") or []
    if aliases:
        out.append(f'<div class=subtitle>别名：{esc("、".join(aliases))}</div>')
    out.append(f'<div class=meta>')
    for m in extra_meta:
        out.append(m)
    out.append(f'<span><strong>出现次数</strong>　{len(mentions)}</span>')
    out.append("</div>")
    if e.get("summary") or e.get("definition") or e.get("description"):
        body = e.get("summary") or e.get("definition") or e.get("description")
        paras = re.split(r"\n\s*\n+", body.strip())
        if len(paras) == 1:
            paras = [p.strip() for p in body.strip().split("\n") if p.strip()]
        for para in paras:
            escaped = esc(para)
            # render **bold** → <strong>bold</strong>
            escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            out.append(f'<p>{escaped}</p>')

    if mentions:
        out.append(f'<h2>{esc(DOC_LABEL)}中提到</h2>')
        out.append('<ul class=mention-list>')
        for m in mentions:
            mtg = m["meeting"]
            out.append('<li>')
            out.append(f'<span class=when>{esc(mtg.get("date") or "")}</span>')
            out.append(f'<a href="../meetings/{esc(mtg["slug"])}.html">{esc(mtg["title"])}</a>')
            if m.get("context"):
                out.append(f'<span class=ctx>{esc(m["context"])}</span>')
            out.append('</li>')
        out.append('</ul>')

    out.append(ftr)
    return "".join(out)


def build_mention_map(data, name_maps):
    people_mentions = defaultdict(list)
    concepts_mentions = defaultdict(list)
    entities_mentions = defaultdict(list)

    for m in sorted(data["meetings"], key=lambda x: x.get("date") or "0000"):
        for n in m.get("people_mentioned") or []:
            slug = name_maps["people"].get(n)
            if not slug: continue
            ctx = first_topic_context(m, n)
            people_mentions[slug].append({"meeting": m, "context": ctx})
        for n in m.get("concepts_mentioned") or []:
            slug = name_maps["concepts"].get(n)
            if not slug: continue
            ctx = first_topic_context(m, n)
            concepts_mentions[slug].append({"meeting": m, "context": ctx})
        for n in m.get("entities_mentioned") or []:
            slug = name_maps["entities"].get(n)
            if not slug: continue
            ctx = first_topic_context(m, n)
            entities_mentions[slug].append({"meeting": m, "context": ctx})

    return people_mentions, concepts_mentions, entities_mentions


def first_topic_context(meeting: dict, name: str) -> str:
    """Find a 1-line snippet from meeting where `name` appears."""
    for t in meeting.get("topics") or []:
        summary = t.get("summary") or ""
        if name in summary:
            for sent in re.split(r"[。；\n]", summary):
                if name in sent:
                    s = sent.strip()
                    return (t.get("name") or "") + "：" + (s[:120] + "…" if len(s) > 120 else s)
        for q in t.get("anchor_quotes") or []:
            if name in q:
                prefix = f"{ANCHOR_NAME}：" if ANCHOR_NAME else ""
                return prefix + (q[:120] + "…" if len(q) > 120 else q)
    return ""


def render_people_index(data, mentions_map) -> str:
    hdr, ftr = shell(title="人物索引", base="../")
    people = sorted(data["people"], key=lambda p: -len(mentions_map.get(p["slug"], [])))
    out = [hdr, "<h1>人物</h1>"]
    out.append(f'<div class=subtitle>共 {len(people)} 位 · 按提及次数排序</div>')
    out.append('<div class=filter-bar><input id=f placeholder="过滤人物名"><span class=count id=cnt></span></div>')
    out.append('<div class=grid id=list>')
    for p in people:
        n = len(mentions_map.get(p["slug"], []))
        role = esc(p.get("role") or "")
        summary = esc(p.get("summary") or "")
        aliases = "、".join(p.get("aliases") or [])
        alias_html = f" ({esc(aliases)})" if aliases else ""
        out.append(
            f'<div class=card data-name="{esc(p["name"])}{esc(aliases)}">'
            f'<a class=title href="{esc(p["slug"])}.html">{esc(p["name"])}{alias_html}</a>'
            f'<div class=meta><span>{role}</span><span>出现 {n} 次</span></div>'
            f'<p class=summary>{summary}</p>'
            f'</div>'
        )
    out.append('</div>')
    out.append(GRID_FILTER_JS)
    out.append(ftr)
    return "".join(out)


def render_concepts_index(data, mentions_map) -> str:
    hdr, ftr = shell(title="概念索引", base="../")
    items = sorted(data["concepts"], key=lambda c: -len(mentions_map.get(c["slug"], [])))
    out = [hdr, "<h1>概念</h1>"]
    out.append(f'<div class=subtitle>共 {len(items)} 个 · 按提及次数排序</div>')
    out.append('<div class=filter-bar><input id=f placeholder="过滤概念名"><span class=count id=cnt></span></div>')
    out.append('<div class=grid id=list>')
    for c in items:
        n = len(mentions_map.get(c["slug"], []))
        cat = esc(c.get("category") or "")
        defn = esc(c.get("definition") or "")
        out.append(
            f'<div class=card data-name="{esc(c["name"])}">'
            f'<a class=title href="{esc(c["slug"])}.html">{esc(c["name"])}</a>'
            f'<div class=meta><span>{cat}</span><span>出现 {n} 次</span></div>'
            f'<p class=summary>{defn}</p>'
            f'</div>'
        )
    out.append('</div>')
    out.append(GRID_FILTER_JS)
    out.append(ftr)
    return "".join(out)


def render_entities_index(data, mentions_map) -> str:
    hdr, ftr = shell(title="实体索引", base="../")
    items = sorted(data["entities"], key=lambda e: (e.get("type", ""), -len(mentions_map.get(e["slug"], []))))
    out = [hdr, "<h1>实体</h1>"]
    out.append(f'<div class=subtitle>共 {len(items)} 个</div>')
    out.append('<div class=filter-bar>')
    out.append('<input id=f placeholder="过滤实体名">')
    out.append('<select id=ftype>')
    out.append('<option value="">全部类型</option>')
    # Collect types actually present in data — robust to corpora that don't use the suggested enum
    types_present = sorted({e.get("type", "") for e in items if e.get("type")})
    for t in types_present:
        out.append(f'<option value="{esc(t)}">{esc(t)}</option>')
    out.append('</select>')
    out.append('<span class=count id=cnt></span>')
    out.append('</div>')
    out.append('<div class=grid id=list>')
    for e in items:
        n = len(mentions_map.get(e["slug"], []))
        t = esc(e.get("type") or "")
        desc = esc(e.get("description") or "")
        out.append(
            f'<div class=card data-name="{esc(e["name"])}" data-type="{t}">'
            f'<a class=title href="{esc(e["slug"])}.html">{esc(e["name"])}</a>'
            f'<div class=meta><span>{t}</span><span>出现 {n} 次</span></div>'
            f'<p class=summary>{desc}</p>'
            f'</div>'
        )
    out.append('</div>')
    out.append(ENTITY_FILTER_JS)
    out.append(ftr)
    return "".join(out)


def _badge_for(type_str: str) -> tuple[str, str]:
    """(css_class, display_text). Heuristic based on common substrings."""
    t = type_str or ""
    if "ST" in t: return ("st", "ST")
    if "EMT" in t: return ("emt", "EMT")
    if "专题" in t or "汇报" in t: return ("zhuanti", "专题")
    # fallback: take first 2-4 chars as the badge text
    short = t[:4] if t else "—"
    return ("zhuanti", short)


def render_meetings_index(data) -> str:
    hdr, ftr = shell(title=f"{DOC_LABEL}索引", base="../")
    out = [hdr, f"<h1>{esc(DOC_LABEL)}</h1>"]
    out.append(f'<div class=subtitle>共 {len(data["meetings"])} 份 · 按年份倒序</div>')

    by_year = defaultdict(list)
    for m in data["meetings"]:
        y = (m.get("date") or "0000")[:4]
        by_year[y].append(m)

    for year in sorted(by_year, reverse=True):
        if year == "0000": continue
        ms = sorted(by_year[year], key=lambda x: x.get("date") or "0000", reverse=True)
        out.append(f'<div class=year-group><h2>{year}</h2><ul>')
        for m in ms:
            badge_cls, badge_text = _badge_for(m.get("type", ""))
            out.append(
                f'<li><span class=date>{esc(m.get("date") or "")}</span>'
                f'<span class="badge {badge_cls}">{esc(badge_text)}</span>'
                f'<a href="{esc(m["slug"])}.html">{esc(m["title"])}</a></li>'
            )
        out.append("</ul></div>")

    if by_year.get("0000"):
        out.append('<div class=year-group><h2>未标日期</h2><ul>')
        for m in by_year["0000"]:
            out.append(f'<li><a href="{esc(m["slug"])}.html">{esc(m["title"])}</a></li>')
        out.append("</ul></div>")

    out.append(ftr)
    return "".join(out)


def render_home(data, mentions_map_p, mentions_map_c, mentions_map_e) -> str:
    hdr, ftr = shell(title=f"{SITE_TITLE} · 首页", base="", wide=True)
    out = [hdr]
    out.append(f'<h1>{esc(SITE_TITLE)}</h1>')
    out.append(f'<div class=subtitle>从 {len(data["meetings"])} 份{esc(DOC_LABEL)}中抽取 · '
               f'{len(data["people"])} 人 / {len(data["concepts"])} 概念 / {len(data["entities"])} 实体</div>')

    out.append(f'<h2>近期{esc(DOC_LABEL)}</h2>')
    recent = sorted([m for m in data["meetings"] if m.get("date")], key=lambda x: x["date"], reverse=True)[:8]
    out.append('<div class=grid>')
    for m in recent:
        out.append(
            f'<div class=card>'
            f'<a class=title href="meetings/{esc(m["slug"])}.html">{esc(m["title"])}</a>'
            f'<div class=meta><span>{esc(m.get("date") or "")}</span><span>{esc(m.get("type") or "")}</span></div>'
            f'</div>'
        )
    out.append('</div>')

    out.append("<h2>高频人物</h2>")
    top_people = sorted(data["people"], key=lambda p: -len(mentions_map_p.get(p["slug"], [])))[:12]
    out.append('<div class=grid>')
    for p in top_people:
        n = len(mentions_map_p.get(p["slug"], []))
        out.append(
            f'<div class=card>'
            f'<a class=title href="people/{esc(p["slug"])}.html">{esc(p["name"])}</a>'
            f'<div class=meta><span>{esc(p.get("role") or "")}</span><span>{n} 次</span></div>'
            f'</div>'
        )
    out.append('</div>')

    out.append("<h2>高频概念</h2>")
    top_concepts = sorted(data["concepts"], key=lambda c: -len(mentions_map_c.get(c["slug"], [])))[:12]
    out.append('<div class=grid>')
    for c in top_concepts:
        n = len(mentions_map_c.get(c["slug"], []))
        out.append(
            f'<div class=card>'
            f'<a class=title href="concepts/{esc(c["slug"])}.html">{esc(c["name"])}</a>'
            f'<div class=meta><span>{esc(c.get("category") or "")}</span><span>{n} 次</span></div>'
            f'</div>'
        )
    out.append('</div>')

    out.append("<h2>高频实体</h2>")
    top_entities = sorted(data["entities"], key=lambda e: -len(mentions_map_e.get(e["slug"], [])))[:12]
    out.append('<div class=grid>')
    for e in top_entities:
        n = len(mentions_map_e.get(e["slug"], []))
        out.append(
            f'<div class=card>'
            f'<a class=title href="entities/{esc(e["slug"])}.html">{esc(e["name"])}</a>'
            f'<div class=meta><span>{esc(e.get("type") or "")}</span><span>{n} 次</span></div>'
            f'</div>'
        )
    out.append('</div>')

    out.append(ftr)
    return "".join(out)


GRID_FILTER_JS = """<script>
(() => {
  const f = document.getElementById('f');
  const list = document.getElementById('list');
  const cnt = document.getElementById('cnt');
  const cards = [...list.children];
  function apply(){
    const q = (f.value || '').toLowerCase().trim();
    let n = 0;
    for (const c of cards){
      const name = (c.dataset.name || '').toLowerCase();
      const show = !q || name.includes(q);
      c.style.display = show ? '' : 'none';
      if (show) n++;
    }
    cnt.textContent = n + ' 项';
  }
  f.addEventListener('input', apply); apply();
})();
</script>"""


ENTITY_FILTER_JS = """<script>
(() => {
  const f = document.getElementById('f');
  const ft = document.getElementById('ftype');
  const list = document.getElementById('list');
  const cnt = document.getElementById('cnt');
  const cards = [...list.children];
  function apply(){
    const q = (f.value || '').toLowerCase().trim();
    const t = ft.value;
    let n = 0;
    for (const c of cards){
      const name = (c.dataset.name || '').toLowerCase();
      const type = c.dataset.type || '';
      const show = (!q || name.includes(q)) && (!t || type === t);
      c.style.display = show ? '' : 'none';
      if (show) n++;
    }
    cnt.textContent = n + ' 项';
  }
  f.addEventListener('input', apply);
  ft.addEventListener('change', apply);
  apply();
})();
</script>"""


def build_search_index(data) -> list[dict]:
    out = []
    for p in data["people"]:
        out.append({"k": "people", "s": p["slug"], "n": p["name"]})
        for a in p.get("aliases") or []:
            out.append({"k": "people", "s": p["slug"], "n": a})
    for c in data["concepts"]:
        out.append({"k": "concepts", "s": c["slug"], "n": c["name"]})
    for e in data["entities"]:
        out.append({"k": "entities", "s": e["slug"], "n": e["name"]})
    for m in data["meetings"]:
        out.append({"k": "meetings", "s": m["slug"], "n": m["title"]})
    return out


def main():
    global SITE_TITLE, DOC_LABEL, ANCHOR_NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "extracted.json"))
    ap.add_argument("--out", default=str(ROOT))
    ap.add_argument("--site-title", default="知识库",
                    help="Brand label shown in header and home title")
    ap.add_argument("--doc-label", default="文档",
                    help="What to call individual documents in the UI (e.g. 纪要, 论文, 笔记)")
    ap.add_argument("--anchor-name", default="",
                    help="If set, render anchor_quotes blocks attributed to this person")
    args = ap.parse_args()

    SITE_TITLE = args.site_title
    DOC_LABEL = args.doc_label
    ANCHOR_NAME = args.anchor_name

    data = json.loads(Path(args.data).read_text("utf-8"))
    out_dir = Path(args.out)
    for sub in ("meetings", "people", "concepts", "entities", "data", "assets"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    shell.n_meetings = len(data["meetings"])  # type: ignore[attr-defined]

    lookup = lookup_from(data)
    name_maps = {
        "people": {**{p["name"]: p["slug"] for p in data["people"]},
                    **{a: p["slug"] for p in data["people"] for a in p.get("aliases") or []},
                    **{p["slug"]: p["slug"] for p in data["people"]}},
        "concepts": {**{c["name"]: c["slug"] for c in data["concepts"]},
                     **{c["slug"]: c["slug"] for c in data["concepts"]}},
        "entities": {**{e["name"]: e["slug"] for e in data["entities"]},
                     **{e["slug"]: e["slug"] for e in data["entities"]}},
    }

    people_mentions, concepts_mentions, entities_mentions = build_mention_map(data, name_maps)

    for m in data["meetings"]:
        html_out = render_meeting(m, lookup, name_maps)
        (out_dir / "meetings" / f'{m["slug"]}.html').write_text(html_out, "utf-8")

    for p in data["people"]:
        ms = people_mentions.get(p["slug"], [])
        extra = []
        if p.get("role"): extra.append(f'<span><strong>角色</strong>　{esc(p["role"])}</span>')
        if p.get("department"): extra.append(f'<span><strong>部门</strong>　{esc(p["department"])}</span>')
        html_out = render_entity_like(p, "people", ms, extra)
        (out_dir / "people" / f'{p["slug"]}.html').write_text(html_out, "utf-8")

    for c in data["concepts"]:
        ms = concepts_mentions.get(c["slug"], [])
        extra = []
        if c.get("category"): extra.append(f'<span><strong>分类</strong>　{esc(c["category"])}</span>')
        if c.get("first_meeting"): extra.append(f'<span><strong>首次</strong>　{esc(c["first_meeting"])}</span>')
        html_out = render_entity_like(c, "concepts", ms, extra)
        (out_dir / "concepts" / f'{c["slug"]}.html').write_text(html_out, "utf-8")

    for e in data["entities"]:
        ms = entities_mentions.get(e["slug"], [])
        extra = []
        if e.get("type"): extra.append(f'<span><strong>类型</strong>　{esc(e["type"])}</span>')
        html_out = render_entity_like(e, "entities", ms, extra)
        (out_dir / "entities" / f'{e["slug"]}.html').write_text(html_out, "utf-8")

    (out_dir / "meetings" / "index.html").write_text(render_meetings_index(data), "utf-8")
    (out_dir / "people" / "index.html").write_text(render_people_index(data, people_mentions), "utf-8")
    (out_dir / "concepts" / "index.html").write_text(render_concepts_index(data, concepts_mentions), "utf-8")
    (out_dir / "entities" / "index.html").write_text(render_entities_index(data, entities_mentions), "utf-8")

    (out_dir / "index.html").write_text(
        render_home(data, people_mentions, concepts_mentions, entities_mentions), "utf-8"
    )

    (out_dir / "data" / "search-index.json").write_text(
        json.dumps(build_search_index(data), ensure_ascii=False, separators=(",", ":")), "utf-8"
    )

    print(f"Rendered '{SITE_TITLE}':")
    print(f"  {len(data['meetings'])} {DOC_LABEL}")
    print(f"  {len(data['people'])} people")
    print(f"  {len(data['concepts'])} concepts")
    print(f"  {len(data['entities'])} entities")
    print(f"Output → {out_dir}")


if __name__ == "__main__":
    main()
