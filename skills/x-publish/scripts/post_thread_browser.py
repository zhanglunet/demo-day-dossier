#!/usr/bin/env python3
"""
浏览器兜底：没 X API 凭证时，引导用户一条一条手动发。

流程：
  1. 打开 x.com/compose/tweet
  2. 用户登录
  3. 对每条 tweet：
     - 设剪贴板为该条 text
     - 提示用户：Cmd+V → 拖图（如有）→ 点 Tweet
     - 等用户确认后继续下一条
     - 第 2 条起，用户要点"+"或"Add another Tweet"扩展 thread

用法：
    python3 post_thread_browser.py thread.json images_dir/

慢但安全。每条人工 review，适合还没拿到 X dev 凭证的场景。
"""
import json
import subprocess
import sys
import time
from pathlib import Path


COMPOSE_URL = "https://x.com/compose/tweet"


def banner(msg: str):
    bar = "─" * 60
    print(f"\n{bar}\n{msg}\n{bar}", flush=True)


def set_clipboard(text: str):
    """用 pbcopy 设纯文本剪贴板（含换行）。"""
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.communicate(text.encode("utf-8"))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    thread_path = Path(sys.argv[1])
    images_dir = Path(sys.argv[2])

    if not thread_path.exists():
        sys.exit(f"❌ {thread_path} 不存在")
    if not images_dir.is_dir():
        sys.exit(f"❌ {images_dir} 不是目录")

    thread = json.loads(thread_path.read_text(encoding="utf-8"))
    tweets = thread.get("tweets", [])

    print(f"📝 准备发 {len(tweets)} 条 thread", file=sys.stderr)

    # 1. 打开浏览器 + Finder
    print("🌐 打开 X compose...", file=sys.stderr)
    subprocess.Popen(["open", "-a", "Google Chrome", COMPOSE_URL])

    print("🗂  打开 Finder 到图片目录...", file=sys.stderr)
    subprocess.Popen(["open", str(images_dir.resolve())])
    time.sleep(2)

    banner(
        "📌 第一步（手动）：\n"
        "  1. 如未登录，登录 X\n"
        "  2. compose 框已经打开，光标已在第 1 条 tweet 输入区\n\n"
        "完成后按回车继续："
    )
    try:
        input()
    except EOFError:
        time.sleep(45)

    # 2. 逐条
    for idx, t in enumerate(tweets):
        i = t.get("i", idx + 1)
        text = t["text"]
        img = t.get("image")

        is_last = idx == len(tweets) - 1
        is_first = idx == 0

        banner(
            f"📤 Tweet {i}/{len(tweets)}"
            f"{' (last)' if is_last else ''}"
            f"{' (first)' if is_first else ''}\n\n"
            f"内容（{len(text)} chars）：\n"
            f"  {text}\n\n"
            + (f"📎 附图：{img}（从 Finder 拖进来）\n" if img else "")
            + "\n下一步：\n"
            + ("  1. 鼠标点这一条 tweet 的输入框\n"
               if not is_first else "  1. 光标已在第 1 条输入框\n")
            + "  2. 按 Cmd+V（剪贴板里就是上面文字）\n"
            + (f"  3. 从 Finder 拖 {img} 到这条 tweet\n" if img else "")
            + ("  3. 点「Add post」加下一条\n" if not is_last else "  3. 全部检查完，点「Post all」\n")
            + "\n做完按回车继续："
        )

        set_clipboard(text)
        print(f"✅ 剪贴板已设：{text[:50]}{'...' if len(text) > 50 else ''}", file=sys.stderr)

        try:
            input()
        except EOFError:
            time.sleep(30)

    print("\n🎉 全部 thread 已经引导完成。", file=sys.stderr)
    print("⚠️ 最后那个「Post all」按钮永远人工点。", file=sys.stderr)


if __name__ == "__main__":
    main()
