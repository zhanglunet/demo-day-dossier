#!/usr/bin/env python3
"""
半自动发小红书图文笔记 —— 个人账号专用（无创作 API）。

流程：
  1. 跑 md2xhs.py 校验 post.json
  2. 打开本机 Finder 到图片目录（方便用户拖图）
  3. 打开日常 Chrome 到小红书创作中心
  4. 提示用户：扫码登录 → 选「图文」→ 拖 N 张图（按编号顺序）
  5. 用户告诉脚本「光标在标题框」→ 脚本设标题剪贴板 + 发 Cmd+V
  6. 用户告诉脚本「光标在正文框」→ 脚本设正文剪贴板 + 发 Cmd+V
  7. 用户手动加 hashtag（# 是交互输入，脚本贴不进去）
  8. 用户人工点「发布」

⚠️ 小红书反爬比微信严。所有自动化都基于浏览器 UI 操作，并且**最后发布按钮永远人工**。

用法：
    python3 xhs_publish.py post.json images/

    post.json 必须含字段：title / body / hashtags
    images/   是装 5 张 1080×1440 PNG 的目录（命名按 01-05 顺序）
"""
import json
import sys
import subprocess
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_DIR / "scripts"

CREATOR_URL = "https://creator.xiaohongshu.com/publish/publish"


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def banner(msg: str):
    bar = "─" * 60
    print(f"\n{bar}\n⏸  {msg}\n{bar}\n", flush=True)


def set_clipboard_text(text: str):
    """直接用 osascript，比 shell 转义更安全。"""
    # 转义引号 + 反斜杠
    esc = text.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(["osascript", "-e", f'set the clipboard to "{esc}"'], check=True)


def send_cmd_v(app: str = "Google Chrome"):
    """激活窗口 + 发 Cmd+V。"""
    script = (
        f'tell application "{app}" to activate\n'
        f"delay 0.6\n"
        f'tell application "System Events" to keystroke "v" using {{command down}}'
    )
    subprocess.run(["osascript", "-e", script], check=True)
    print(f"✅ Cmd+V 已发送到「{app}」")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    post_path = Path(sys.argv[1])
    images_dir = Path(sys.argv[2])

    if not post_path.exists():
        sys.exit(f"❌ 找不到 {post_path}")
    if not images_dir.is_dir():
        sys.exit(f"❌ {images_dir} 不是目录")

    # 1. 校验 + 标准化
    print("📝 校验 post.json...")
    tmp = Path("/tmp/xhs-post.json")
    run(
        ["python3", str(SCRIPTS / "md2xhs.py"), str(post_path), str(tmp)],
    )
    post = json.loads(tmp.read_text(encoding="utf-8"))

    images = sorted(images_dir.glob("*.png"))
    if not images:
        sys.exit(f"❌ {images_dir} 里没找到 PNG")
    print(f"📸 找到 {len(images)} 张图：{[p.name for p in images]}")

    # 2. 打开 Finder（让用户拖图）
    print("🗂  打开 Finder 到图片目录...")
    subprocess.Popen(["open", str(images_dir.resolve())])
    time.sleep(0.5)

    # 3. 打开 creator 创作中心
    print("🌐 打开日常 Chrome 到小红书创作中心...")
    subprocess.Popen(["open", "-a", "Google Chrome", CREATOR_URL])

    # 4. 等用户登录 + 拖图
    banner(
        "请在小红书创作中心里完成以下手动步骤：\n"
        "  1. 如果未登录，扫码登录（手机小红书 App「我」→ 设置 → 扫一扫）\n"
        "  2. 选「图文笔记」\n"
        f"  3. 从 Finder 把 {len(images)} 张图按顺序拖进来\n"
        "  4. 等图全部上传完毕\n"
        "  5. 鼠标点 **标题** 输入框（光标进去）\n"
        "完成上面 5 步之后，回到这个终端按回车继续：\n"
    )
    try:
        input()
    except EOFError:
        print("⏰ 没有 stdin，挂机 90 秒后继续")
        time.sleep(90)

    # 5. 贴标题
    print(f'🏷  设标题剪贴板：「{post["title"]}」')
    set_clipboard_text(post["title"])
    send_cmd_v("Google Chrome")
    time.sleep(1)

    banner(
        "刚才标题已贴。下一步：\n"
        "  1. 鼠标点 **正文** 输入框（光标进去）\n"
        "  2. 回到终端按回车"
    )
    try:
        input()
    except EOFError:
        time.sleep(15)

    # 6. 贴正文
    print(f'📝 设正文剪贴板：{len(post["body"])} 字')
    set_clipboard_text(post["body"])
    send_cmd_v("Google Chrome")
    time.sleep(1)

    # 7. 提示 hashtag + 发布
    hashtags_str = "\n  ".join(post["hashtags"])
    banner(
        "正文已贴。剩下手动做：\n\n"
        "  1. 把光标移到正文末尾，空一行\n"
        "  2. 一个一个手动敲下面这些话题，等下拉提示出现选第一个：\n"
        f"     {hashtags_str}\n\n"
        "  3. 检查正文 ≤ 1000 字、标题 ≤ 20 字、5 张图顺序正确\n"
        "  4. 检查正文里没有 http / https 链接（会限流）\n"
        "  5. **人工点页面右下「发布」按钮**\n\n"
        "  ⚠️ 脚本永远不替你点「发布」，因为：\n"
        "     - 小红书风控很严，自动发布会封号\n"
        "     - 错发不可撤回\n"
        "     - 多 0.5 秒人工确认，避免后悔"
    )
    print("✅ 脚本流程结束。祝你这条爆 🔥")


if __name__ == "__main__":
    main()
