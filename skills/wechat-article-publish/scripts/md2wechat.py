#!/usr/bin/env python3
"""
把 markdown 转成公众号编辑器友好的 inline-style HTML。

公众号编辑器会剥掉 <style> 标签，所以所有视觉样式必须 inline 到每个元素的
style 属性上。同时把本地图片 ./images/xxx.png 改写为 CF Pages 公开 URL，
公众号粘贴时会自动把外链图镜像到微信 CDN。

用法：
    python3 scripts/md2wechat.py docs/story.md > /tmp/wechat-article.html
    pbcopy < /tmp/wechat-article.html
    # 然后在公众号编辑器里 Cmd+V

被 wechat_publish.py 自动调用，无需手动跑。
"""
import sys
import re
from pathlib import Path
import markdown as md_lib

CF_BASE = "https://qiji-roadshow-2026.pages.dev"

# 公众号编辑器在很多机型上字号会被锁，但 inline style 在 PC 端 + 多数手机正常保留。
# 颜色采用浅色背景上可读的暖灰 / 强调蓝，避免暗色主题（公众号默认白底）。
STYLES = {
    "h1": "font-size:24px;line-height:1.4;font-weight:700;margin:32px 0 16px;color:#222;",
    "h2": "font-size:22px;line-height:1.4;font-weight:700;margin:36px 0 14px;padding:0 0 8px;border-bottom:2px solid #5eead4;color:#222;",
    "h3": "font-size:18px;line-height:1.5;font-weight:700;margin:24px 0 10px;color:#0d9488;",
    "p":  "font-size:16px;line-height:1.85;color:#3f3f46;margin:0 0 18px;letter-spacing:0.3px;",
    "ul": "padding-left:1.5em;margin:0 0 18px;",
    "ol": "padding-left:1.5em;margin:0 0 18px;",
    "li": "font-size:16px;line-height:1.85;color:#3f3f46;margin-bottom:6px;",
    "strong": "color:#111;font-weight:700;",
    "em": "color:#b45309;font-style:normal;font-weight:600;",
    "code": "font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;background:#f4f4f5;color:#0f766e;padding:2px 6px;border-radius:4px;",
    "pre": "background:#0f172a;color:#e2e8f0;padding:16px 18px;border-radius:8px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;line-height:1.6;overflow-x:auto;margin:0 0 22px;",
    "pre_code": "background:transparent;color:inherit;padding:0;font-size:13px;",
    "blockquote": "margin:22px 0;padding:12px 18px;background:#fef3c7;border-left:4px solid #fbbf24;color:#78350f;border-radius:4px;font-size:15px;line-height:1.8;",
    "blockquote_p": "margin:0 0 8px;color:#78350f;font-size:15px;line-height:1.8;",
    "blockquote_p_last": "margin:0;color:#78350f;font-size:15px;line-height:1.8;",
    "table": "width:100%;border-collapse:collapse;margin:0 0 22px;font-size:14px;",
    "th": "padding:10px 12px;background:#f1f5f9;border:1px solid #e2e8f0;color:#0f766e;font-weight:700;text-align:left;font-size:13px;",
    "td": "padding:10px 12px;border:1px solid #e2e8f0;color:#3f3f46;line-height:1.7;",
    "a": "color:#0d9488;text-decoration:underline;",
    "hr": "border:none;border-top:1px solid #e5e7eb;margin:40px auto;max-width:240px;",
    "img": "max-width:100%;height:auto;display:block;margin:24px auto;border-radius:6px;",
}


def add_inline_style(html: str, tag: str, style: str) -> str:
    """For every opening <tag> without a style attr, inject style=."""
    # 已经有 style 的不动；只给裸标签加
    pat = re.compile(rf"<{tag}(?!\w)(\s[^>]*?)?>", re.IGNORECASE)

    def _sub(m):
        attrs = m.group(1) or ""
        if "style=" in attrs.lower():
            return m.group(0)
        return f"<{tag}{attrs} style=\"{style}\">"

    return pat.sub(_sub, html)


def rewrite_image_urls(html: str) -> str:
    """把 ./images/xxx.png 或 images/xxx.png 改成 CF 公开 URL。"""
    def _sub(m):
        path = m.group(1).lstrip("./").lstrip("/")
        if path.startswith("images/"):
            return f'src="{CF_BASE}/{path}"'
        return m.group(0)
    return re.sub(r'src="([^"]+)"', _sub, html)


def style_pre_code(html: str) -> str:
    """pre 里的 code 不要二次背景。"""
    return re.sub(
        r"<pre([^>]*)><code([^>]*?)>",
        lambda m: f'<pre{m.group(1)}><code{m.group(2)} style="{STYLES["pre_code"]}">',
        html,
    )


def style_last_p_in_blockquote(html: str) -> str:
    """blockquote 最后一个 p 去掉底 margin（视觉更紧凑）。"""
    # 简化处理：所有 blockquote 内的 p 用统一样式
    return re.sub(
        r"(<blockquote[^>]*>)(.*?)(</blockquote>)",
        lambda m: m.group(1) + add_inline_style(m.group(2), "p", STYLES["blockquote_p"]) + m.group(3),
        html,
        flags=re.DOTALL,
    )


def convert(md_path: Path) -> str:
    md_text = md_path.read_text(encoding="utf-8")

    # markdown → HTML
    extensions = ["tables", "fenced_code", "sane_lists"]
    html = md_lib.markdown(md_text, extensions=extensions, output_format="html5")

    # 1) 重写图片 URL
    html = rewrite_image_urls(html)

    # 2) inline 样式（顺序很重要：先 pre→code，再统一加 style）
    html = style_pre_code(html)
    html = style_last_p_in_blockquote(html)

    for tag in ["h1", "h2", "h3", "p", "ul", "ol", "li", "blockquote",
                "table", "th", "td", "a", "hr", "img", "pre"]:
        html = add_inline_style(html, tag, STYLES[tag])

    # strong / em / code 是行内，单独处理（避免 pre 内的 code 也被加 inline 样式 —— 已有 pre_code 兜底）
    html = add_inline_style(html, "strong", STYLES["strong"])
    html = add_inline_style(html, "em", STYLES["em"])
    # code 注意 pre 内的 code 已经有 style 了，re.sub 的 add_inline_style 会跳过
    html = add_inline_style(html, "code", STYLES["code"])

    # 顶部加一个 article 容器（便于一次性 Ctrl+A 粘贴）
    wrapped = (
        '<section style="font-family:-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif;'
        'max-width:677px;margin:0 auto;color:#3f3f46;">\n'
        + html
        + "\n</section>"
    )
    return wrapped


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"ERROR: 找不到 {md_path}", file=sys.stderr)
        sys.exit(1)

    html = convert(md_path)
    # 默认输出到 stdout；也可以指定第二个参数作为文件输出
    if len(sys.argv) >= 3:
        out = Path(sys.argv[2])
        out.write_text(html, encoding="utf-8")
        print(f"✅ 已写入 {out}  ({len(html)//1024} KB, {html.count('<img')} 图)", file=sys.stderr)
    else:
        sys.stdout.write(html)


if __name__ == "__main__":
    main()
