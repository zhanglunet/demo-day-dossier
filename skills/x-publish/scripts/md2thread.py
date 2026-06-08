#!/usr/bin/env python3
"""
读取 thread.json（含 tweets 数组），校验 + 标准化输出。

跟其他 platform 一样，本脚本**不替你写文案**。X 的语感非常依赖
现场判断（什么人在 timeline 上 / 当下热点），LLM 单次生成容易踩雷。

工作流：
  1. Claude（你 / 编排者）按 templates/thread.md.tmpl 的 8-12 条结构
     手写 examples/<project>/thread.json：
     {
       "tweets": [
         {"i": 1, "text": "...", "image": "01-cover.png"},
         {"i": 2, "text": "..."},
         ...
       ]
     }

  2. 跑本脚本：
     - 校验每条 ≤ 280 字符（URL 一律算 23 字符）
     - 校验图片文件存在
     - 警告超过 12 条
     - 警告中间条带 URL（algo 限流）
     - 警告开头有 "BREAKING" / 钓鱼词

用法：
    python3 md2thread.py thread.json [images_dir] [out.json]
"""
import json
import re
import sys
from pathlib import Path

MAX_CHARS = 280
URL_LEN = 23  # X 把任何 URL 缩到 23 字符算
SAFE_MARGIN = 5
TOP_N_WARN = 12

URL_RE = re.compile(r"https?://\S+")

FISHING_WORDS = ["BREAKING", "JUST IN", "🚨", "must read", "must-read"]
SOFT_RT_WORDS = ["like this thread", "retweet if", "RT if you", "follow for more"]


def x_visible_chars(text: str) -> int:
    """X 计算字符数时，每个 URL 一律按 23 字符算。"""
    # 替换所有 URL 为占位（长度 URL_LEN）
    def _replace(m):
        return "X" * URL_LEN
    stripped = URL_RE.sub(_replace, text)
    return len(stripped)


def validate_tweet(t: dict, images_dir) -> list:
    warnings = []
    i = t.get("i", "?")
    text = t.get("text", "")

    if not text:
        warnings.append(f"❌ Tweet {i}: 缺 text")
        return warnings

    vc = x_visible_chars(text)
    if vc > MAX_CHARS:
        warnings.append(f"❌ Tweet {i}: {vc}/{MAX_CHARS} 字符超限")
    elif vc > MAX_CHARS - SAFE_MARGIN:
        warnings.append(f"⚠️ Tweet {i}: {vc}/{MAX_CHARS} 字符接近上限")

    # 图片检查
    if t.get("image"):
        if images_dir:
            img_path = images_dir / t["image"]
            if not img_path.exists():
                warnings.append(f"❌ Tweet {i}: 找不到图片 {img_path}")
            else:
                size_kb = img_path.stat().st_size // 1024
                if size_kb > 5000:
                    warnings.append(f"⚠️ Tweet {i}: 图 {size_kb}KB > 5MB，X 会压缩")

    # 钓鱼开头
    for fw in FISHING_WORDS:
        if text.lstrip().lower().startswith(fw.lower()):
            warnings.append(f"⚠️ Tweet {i}: 开头有「{fw}」钓鱼词，X 算法可能降权")

    # 求互动话术
    for sw in SOFT_RT_WORDS:
        if sw.lower() in text.lower():
            warnings.append(f"⚠️ Tweet {i}: 含「{sw}」求互动话术，X 算法可能降权")

    # 中间条带 URL（不算最后一条）
    return warnings


def validate(thread: dict, images_dir) -> list:
    warnings = []
    tweets = thread.get("tweets", [])

    if not tweets:
        warnings.append("❌ 缺 tweets")
        return warnings

    n = len(tweets)
    if n > TOP_N_WARN:
        warnings.append(f"⚠️ {n} 条 thread 偏长，70% 读者滚不到底；建议 ≤ {TOP_N_WARN}")

    # 校验每条
    for idx, t in enumerate(tweets):
        warnings.extend(validate_tweet(t, images_dir))

    # 中间条带 URL 检查（仅最后一条允许 URL，避免算法降权）
    for idx, t in enumerate(tweets[:-1]):
        text = t.get("text", "")
        if URL_RE.search(text):
            i = t.get("i", idx + 1)
            warnings.append(
                f"⚠️ Tweet {i}（非末条）含 URL，X 算法对中间条 URL 降权"
            )

    return warnings


def normalize(thread: dict) -> dict:
    """裁剪 + 修整 + 顺序检查。"""
    tweets = thread.get("tweets", [])
    out = []
    for idx, t in enumerate(tweets):
        text = (t.get("text") or "").strip()
        vc = x_visible_chars(text)
        if vc > MAX_CHARS:
            # 强行截断（保守 5 字符余量）
            text = text[: MAX_CHARS - 5] + "…"
        out.append({
            "i": t.get("i", idx + 1),
            "text": text,
            **({"image": t["image"]} if t.get("image") else {}),
        })
    return {"tweets": out}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    images_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
    out_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else None

    if not src.exists():
        sys.exit(f"❌ 找不到 {src}")

    raw = json.loads(src.read_text(encoding="utf-8"))

    warnings = validate(raw, images_dir)
    for w in warnings:
        print(w, file=sys.stderr)

    out = normalize(raw)

    # 字数报告
    print(
        f"✅ {len(out['tweets'])} tweets · "
        f"max {max(x_visible_chars(t['text']) for t in out['tweets'])}/{MAX_CHARS} chars · "
        f"{sum(1 for t in out['tweets'] if t.get('image'))} attached images",
        file=sys.stderr,
    )

    if out_path:
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 已写入 {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
