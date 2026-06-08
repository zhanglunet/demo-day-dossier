"""Merge sub-agent batch JSONs into a single extracted.json with dedup.

Usage:
    python3 scripts/merge.py [--raw data/raw] [--out data/extracted.json]

Dedup strategy:
  - people: merge by slug. Combine aliases. Take longest summary/role.
  - concepts: merge by slug.
  - entities: merge by slug. Take longest description.
  - meetings: keyed by slug (each meeting only appears in one batch).
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path


def longest(a: str | None, b: str | None) -> str | None:
    if not a: return b
    if not b: return a
    return a if len(a) >= len(b) else b


def merge_person(a: dict, b: dict) -> dict:
    out = {**a}
    aliases = set(a.get("aliases") or []) | set(b.get("aliases") or [])
    # Add the "other" name as alias too, in case slugs collide but names differ
    if a.get("name") and a["name"] != b.get("name"):
        aliases.add(b.get("name", ""))
    aliases.discard("")
    aliases.discard(out["name"])
    out["aliases"] = sorted(aliases)
    out["role"] = longest(a.get("role"), b.get("role"))
    out["department"] = longest(a.get("department"), b.get("department"))
    out["summary"] = longest(a.get("summary"), b.get("summary"))
    if a.get("first_seen_meeting") and b.get("first_seen_meeting"):
        out["first_seen_meeting"] = min(a["first_seen_meeting"], b["first_seen_meeting"])
    return out


def merge_concept(a: dict, b: dict) -> dict:
    out = {**a}
    out["category"] = longest(a.get("category"), b.get("category"))
    out["definition"] = longest(a.get("definition"), b.get("definition"))
    if a.get("first_meeting") and b.get("first_meeting"):
        out["first_meeting"] = min(a["first_meeting"], b["first_meeting"])
    return out


def merge_entity(a: dict, b: dict) -> dict:
    out = {**a}
    out["type"] = a.get("type") or b.get("type")
    out["description"] = longest(a.get("description"), b.get("description"))
    if a.get("first_meeting") and b.get("first_meeting"):
        out["first_meeting"] = min(a["first_meeting"], b["first_meeting"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--out", default="data/extracted.json")
    args = ap.parse_args()

    raw = Path(args.raw)
    batches = sorted(raw.glob("batch-*.json"))
    if not batches:
        raise SystemExit(f"No batches found in {raw}")

    people: dict[str, dict] = {}
    concepts: dict[str, dict] = {}
    entities: dict[str, dict] = {}
    meetings: dict[str, dict] = {}

    for bp in batches:
        b = json.loads(bp.read_text("utf-8"))
        print(f"  {bp.name}: {len(b.get('meetings', []))} meetings, "
              f"{len(b.get('people', []))} ppl, {len(b.get('concepts', []))} cpt, "
              f"{len(b.get('entities', []))} ent")
        for p in b.get("people") or []:
            slug = p["slug"]
            if slug in people:
                people[slug] = merge_person(people[slug], p)
            else:
                p.setdefault("aliases", [])
                people[slug] = p
        for c in b.get("concepts") or []:
            slug = c["slug"]
            if slug in concepts:
                concepts[slug] = merge_concept(concepts[slug], c)
            else:
                concepts[slug] = c
        for e in b.get("entities") or []:
            slug = e["slug"]
            if slug in entities:
                entities[slug] = merge_entity(entities[slug], e)
            else:
                entities[slug] = e
        for m in b.get("meetings") or []:
            slug = m["slug"]
            if slug in meetings:
                print(f"  WARN: duplicate meeting slug {slug} in {bp.name}, keeping first")
                continue
            meetings[slug] = m

    out = {
        "people": list(people.values()),
        "concepts": list(concepts.values()),
        "entities": list(entities.values()),
        "meetings": list(meetings.values()),
    }

    Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), "utf-8"
    )
    print(f"\nMerged → {args.out}")
    print(f"  {len(meetings)} meetings · {len(people)} people · "
          f"{len(concepts)} concepts · {len(entities)} entities")


if __name__ == "__main__":
    main()
