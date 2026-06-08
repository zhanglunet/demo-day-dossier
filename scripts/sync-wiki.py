#!/usr/bin/env python3
"""Sync wiki HTML + index.html / dd.html embedded JSON from output/projects.json.

Run from anywhere. Idempotent. After this script:
- output/wiki/data/raw/batch-4.json is regenerated from projects.json
- output/wiki/data/extracted.json is re-merged from all 4 batches
- output/wiki/**/*.html are re-rendered
- output/index.html and output/dd.html have fresh projects.json embedded

Usage: python3 scripts/sync-wiki.py
       or: make sync
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / 'scripts'
LIB = SCRIPTS / '_lib'
WIKI = REPO_ROOT / 'output' / 'wiki'
PROJECTS = REPO_ROOT / 'output' / 'projects.json'


def step(msg):
    print(f'━━━ {msg}', flush=True)


def run(cmd, **kw):
    print(f'  $ {" ".join(str(c) for c in cmd)}')
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        sys.exit(r.returncode)
    if r.stdout.strip():
        for line in r.stdout.strip().split('\n'):
            print(f'    {line}')


def replace_json_block(html_text, marker):
    """Replace JS const block `marker = {...}` with brace-counting parse."""
    start = html_text.find(marker)
    if start < 0:
        return None
    brace = html_text.find('{', start)
    depth = 0
    in_str = False
    esc = False
    i = brace
    while i < len(html_text):
        c = html_text[i]
        if esc:
            esc = False
        elif c == '\\' and in_str:
            esc = True
        elif c == '"':
            in_str = not in_str
        elif not in_str:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return brace, i + 1
        i += 1
    return None


def embed_projects_into_html():
    data = json.loads(PROJECTS.read_text(encoding='utf-8'))
    payload = json.dumps(data, ensure_ascii=False, indent=2)

    for html_path, marker in [
        (REPO_ROOT / 'output' / 'index.html', 'const DATA = '),
        (REPO_ROOT / 'output' / 'dd.html', 'const PROJECT_DATA = '),
    ]:
        if not html_path.exists():
            print(f'  ⚠ skip (missing): {html_path}')
            continue
        text = html_path.read_text(encoding='utf-8')
        res = replace_json_block(text, marker)
        if not res:
            print(f'  ⚠ marker not found in {html_path.name}: {marker!r}')
            continue
        brace, end = res
        new_text = text[:brace] + payload + text[end:]
        if new_text != text:
            html_path.write_text(new_text, encoding='utf-8')
            print(f'  ✓ embedded into {html_path.relative_to(REPO_ROOT)}')
        else:
            print(f'  = unchanged: {html_path.relative_to(REPO_ROOT)}')


def main():
    step('1/5  validate paths')
    for p in [PROJECTS, WIKI / 'data' / 'raw', LIB / 'merge.py', LIB / 'render.py',
              LIB / 'fix_json.py', SCRIPTS / 'projects_to_batch4.py']:
        if not p.exists():
            print(f'  ✗ MISSING {p}')
            sys.exit(1)
        print(f'  ✓ {p.relative_to(REPO_ROOT)}')

    step('2/5  projects.json → batch-4.json')
    run([sys.executable, str(SCRIPTS / 'projects_to_batch4.py')])

    step('3/5  fix_json (idempotent JSON repair)')
    run([sys.executable, str(LIB / 'fix_json.py'), str(WIKI / 'data' / 'raw')])

    step('4/5  merge all batches → extracted.json')
    run([
        sys.executable, str(LIB / 'merge.py'),
        '--raw', str(WIKI / 'data' / 'raw'),
        '--out', str(WIKI / 'data' / 'extracted.json'),
    ])

    step('5/5  render wiki HTML + embed projects.json into index/dd')
    run([
        sys.executable, str(LIB / 'render.py'),
        '--data', str(WIKI / 'data' / 'extracted.json'),
        '--out', str(WIKI),
        '--site-title', '奇绩创坛 2026 春季路演日 · Wiki',
        '--doc-label', '纪要',
    ])
    embed_projects_into_html()

    # Final summary
    n_meet = len(list((WIKI / 'meetings').glob('*.html')))
    n_per = len(list((WIKI / 'people').glob('*.html')))
    n_con = len(list((WIKI / 'concepts').glob('*.html')))
    n_ent = len(list((WIKI / 'entities').glob('*.html')))
    print()
    print(f'━━━ done · 纪要 {n_meet} · 人物 {n_per} · 概念 {n_con} · 实体 {n_ent}')
    print('━━━ run `git status` to see changes, `git diff` to review, then commit + push')


if __name__ == '__main__':
    main()
