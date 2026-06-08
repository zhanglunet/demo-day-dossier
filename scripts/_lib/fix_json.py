"""Fix sub-agent JSON output: replace stray ASCII double-quotes inside string values with 「 」.

Why: agents often emit Chinese summaries that contain inline ASCII " to quote a phrase
(e.g. "联信事业部"), which breaks the enclosing JSON string. A character-level pass
detects whether a `"` is the end of the current JSON string or an internal quote,
and rewrites internals to half-width corner brackets.

Usage:
    python3 scripts/fix_json.py data/raw/           # fix all *.json in dir
    python3 scripts/fix_json.py data/raw/batch-3.json   # fix one file

Behavior:
- Files that already json.load() cleanly are skipped.
- Files that fail to parse get the rewrite; on success the file is written back.
- If rewriting still doesn't parse, prints location and aborts that file
  (so you can hand-fix or re-dispatch the sub-agent).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path


def repair(src: str) -> str:
    """Single pass through `src`. State machine tracks whether we're inside a JSON
    string. When we see `"` inside a string, look ahead: if the next non-space char
    is `,` or `}` or `]` or `\n` (typical string terminators in JSON), treat as
    end-of-string. Otherwise it's an embedded quote — replace with corner bracket.
    Tracks open/close pairs to alternate 「 vs 」."""
    out = []
    in_str = False
    escape = False
    # Track number of internal quotes seen in current string to alternate corner bracket
    open_count = 0
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if not in_str:
            out.append(c)
            if c == '"':
                in_str = True
                escape = False
                open_count = 0
            i += 1
            continue

        # inside string
        if escape:
            out.append(c)
            escape = False
            i += 1
            continue
        if c == "\\":
            out.append(c)
            escape = True
            i += 1
            continue
        if c == '"':
            # look ahead to next non-space
            j = i + 1
            while j < n and src[j] in " \t":
                j += 1
            nxt = src[j] if j < n else ""
            if nxt in (",", "}", "]", ":", "\n", "\r", ""):
                # treat as end of string
                out.append(c)
                in_str = False
                i += 1
                continue
            # internal quote — replace
            out.append("「" if open_count % 2 == 0 else "」")
            open_count += 1
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def process(path: Path) -> bool:
    raw = path.read_text("utf-8")
    try:
        json.loads(raw)
        return True  # already valid
    except json.JSONDecodeError as e:
        print(f"  {path.name}: broken at line {e.lineno} col {e.colno} — repairing")

    fixed = repair(raw)
    try:
        json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"  {path.name}: STILL BROKEN after repair (line {e.lineno} col {e.colno}). Not overwriting.")
        return False

    path.write_text(fixed, "utf-8")
    print(f"  {path.name}: repaired ✓")
    return True


def main():
    if len(sys.argv) != 2:
        print("usage: python3 fix_json.py <dir-or-file>", file=sys.stderr)
        sys.exit(2)
    target = Path(sys.argv[1])
    if target.is_dir():
        files = sorted(target.glob("*.json"))
    elif target.is_file():
        files = [target]
    else:
        print(f"not found: {target}", file=sys.stderr)
        sys.exit(2)

    if not files:
        print(f"no JSON files in {target}")
        return

    ok = 0
    for f in files:
        if process(f):
            ok += 1
    print(f"\n{ok}/{len(files)} files clean")


if __name__ == "__main__":
    main()
