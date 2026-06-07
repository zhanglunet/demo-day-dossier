#!/usr/bin/env python3
"""
读取一篇长文 markdown + 一个已写好的 post.json（含 title/body/hashtags），
输出统一格式的 JSON 给 xhs_publish.py 用。

这个脚本**不替你写文案**。小红书写作高度依赖语感和实时热点，
LLM 一次性生成的容易踩中风控雷区。所以工作流是：

  1. 由 Claude（你 / 编排者）按 templates/post.md.tmpl 的格式
     手写 examples/<project>/post.json：
     {
       "title": "≤20 字标题",
       "body": "≤1000 字正文",
       "hashtags": ["#话题1", "#话题2", ...]
     }

  2. 跑本脚本做验证 + 字数校对 + 标准化输出。

用法：
    python3 md2xhs.py post.json [out.json]

- 如果第二个参数不传，结果打印到 stdout。
- 字数超限会报警告（不阻塞，但提示你裁剪）。
"""
import json
import sys
import re
from pathlib import Path

# 小红书硬限
MAX_TITLE = 20
MAX_BODY = 1000
MAX_HASHTAGS = 10


def visible_chars(s: str) -> int:
    """小红书的字数计算大致按 Unicode codepoint 数，但 emoji 算 1。"""
    # 简化：直接 len()，emoji 计 1。
    return len(s)


def validate(post: dict) -> list:
    warnings = []
    title = post.get("title", "")
    body = post.get("body", "")
    tags = post.get("hashtags", [])

    if not title:
        warnings.append("❌ 缺 title")
    elif visible_chars(title) > MAX_TITLE:
        warnings.append(
            f"⚠️ title 长度 {visible_chars(title)} > {MAX_TITLE} 上限，会被截断。"
            f"\n   原文：{title}"
        )

    if not body:
        warnings.append("❌ 缺 body")
    elif visible_chars(body) > MAX_BODY:
        warnings.append(
            f"⚠️ body 长度 {visible_chars(body)} > {MAX_BODY} 上限。"
        )

    if not tags:
        warnings.append("⚠️ 没 hashtag，发现率会低很多")
    elif len(tags) > MAX_HASHTAGS:
        warnings.append(f"⚠️ hashtag 数 {len(tags)} > {MAX_HASHTAGS}，建议 3-5 个")

    # 反爬检查
    for line in body.split("\n"):
        if re.search(r"https?://", line):
            warnings.append(f"⚠️ 正文含外链 URL（会限流）：{line.strip()[:60]}")
        if re.search(r"加我微信|私信我|加好友", line):
            warnings.append(f"⚠️ 正文含引导加私信关键词（会降权）：{line.strip()[:40]}")

    for word in ["震惊", "揭秘", "必看", "重磅", "全网首发"]:
        if word in title:
            warnings.append(f"⚠️ 标题含「{word}」是标题党触发词，建议替换")

    # tag 格式检查
    for t in tags:
        if not t.startswith("#"):
            warnings.append(f"⚠️ hashtag「{t}」缺 # 前缀")

    return warnings


def normalize(post: dict) -> dict:
    """裁剪到 hard limit + 修整格式。"""
    out = {
        "title": post.get("title", "").strip()[:MAX_TITLE],
        "body": post.get("body", "").strip()[:MAX_BODY],
        "hashtags": [
            t if t.startswith("#") else f"#{t}"
            for t in post.get("hashtags", [])[:MAX_HASHTAGS]
        ],
    }
    # body 末尾去掉多余换行
    out["body"] = re.sub(r"\n{3,}", "\n\n", out["body"])
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"❌ 找不到 {src}")

    raw = json.loads(src.read_text(encoding="utf-8"))

    warnings = validate(raw)
    for w in warnings:
        print(w, file=sys.stderr)

    out = normalize(raw)

    # 字数报告
    print(
        f"✅ title: {visible_chars(out['title'])}/{MAX_TITLE} | "
        f"body: {visible_chars(out['body'])}/{MAX_BODY} | "
        f"hashtags: {len(out['hashtags'])}",
        file=sys.stderr,
    )

    if len(sys.argv) >= 3:
        dst = Path(sys.argv[2])
        dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 已写入 {dst}", file=sys.stderr)
    else:
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
