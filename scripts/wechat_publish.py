#!/usr/bin/env python3
"""
半自动发公众号文章 —— 个人订阅号专用（无 API 权限）。

流程：
  1. 跑 md2wechat.py 把 docs/story.md 转成 inline-style HTML
  2. 把 HTML 拷到系统剪贴板（pbcopy）
  3. 用 Playwright 打开 mp.weixin.qq.com
  4. 等你扫码登录（最多 3 分钟）
  5. 自动跳「新建图文」并填好标题 / 作者 / 摘要 / 原文链接
  6. 把光标定位到正文区，等你按 Cmd+V 粘贴（脚本会停下提示你）
  7. 你在浏览器里检查、点「保存为草稿」、再去公众号 App 群发

⚠️ 个人订阅号没有 API 权限，**所有自动化都基于浏览器 UI 操作**。微信
后台 UI 经常微调，选择器（selector）可能需要按当时实际 HTML 微调。脚本
设计为"能自动的尽量自动，不能自动的明确提示你手动"。

用法：
    python3 scripts/wechat_publish.py
    # 或显式传 markdown 路径
    python3 scripts/wechat_publish.py docs/story.md
"""
import sys
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ───── 文章元数据 ─────
ARTICLE_TITLE = "56 个路演项目，一个人，一晚上：我怎么用 Claude Skill + 7 路 AI 调研团跑完了一份投资级 DD"
ARTICLE_AUTHOR = ""  # 留空就用账号默认作者名；填则覆盖
ARTICLE_DIGEST = (
    "一张展厅墙、一篇微信文章、22 张项目卡截图，30 分钟后变成全景网页、"
    "可排序的 DD 表、89KB 的 Word 深度报告、和一份 Excel 表 —— 整套上线 Cloudflare。"
)
ARTICLE_SRC_URL = "https://qiji-roadshow-2026.pages.dev/story"

# ───── 路径 ─────
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MD = ROOT / "docs" / "story.md"
HTML_OUT = Path("/tmp/wechat-article.html")
SCRIPT_MD2W = ROOT / "scripts" / "md2wechat.py"


def run_md2wechat(md_path: Path) -> str:
    """跑 md2wechat.py 拿 inline-style HTML。"""
    print(f"📝 转换 markdown → 公众号 HTML：{md_path}")
    subprocess.run(
        ["python3", str(SCRIPT_MD2W), str(md_path), str(HTML_OUT)],
        check=True,
    )
    html = HTML_OUT.read_text(encoding="utf-8")
    print(f"   ✅ {len(html)//1024} KB · {html.count('<img')} 图")
    return html


def copy_to_clipboard(text: str):
    """macOS pbcopy。"""
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.communicate(text.encode("utf-8"))
    print("📋 HTML 已拷到系统剪贴板")


def banner(msg: str):
    """打印一个醒目的提示框，不阻塞。"""
    bar = "─" * 60
    print(f"\n{bar}\n⏸  {msg}\n{bar}\n", flush=True)


def main():
    md_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    if not md_path.exists():
        sys.exit(f"❌ 找不到 markdown 文件：{md_path}")

    html_body = run_md2wechat(md_path)
    copy_to_clipboard(html_body)

    print("\n🌐 启动浏览器（非 headless）。你会看到一个 Chromium 窗口。")
    print("   ⚠️ 不要关，所有自动化在这里跑。\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=120)
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="zh-CN",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()

        # 1. 打开公众号后台首页
        print("➡️  打开 https://mp.weixin.qq.com")
        page.goto("https://mp.weixin.qq.com/", wait_until="domcontentloaded")

        print("\n📱 请用「微信」App 扫码登录（3 分钟内）...")
        # 登录成功后会跳到 /cgi-bin/home?t=home
        try:
            page.wait_for_url("**/cgi-bin/home**", timeout=180_000)
            print("   ✅ 登录成功")
        except PlaywrightTimeoutError:
            sys.exit("❌ 超时没等到登录，请重试")

        # 2. 跳到「新建图文」
        # 公众号后台「图文消息」入口 URL（多年来稳定）：
        #   https://mp.weixin.qq.com/cgi-bin/appmsg?action=edit&type=77（"77" = 图文消息）
        # 但新版后台路径有所变化，下面给个 fallback chain。
        candidate_urls = [
            "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=77",
            "https://mp.weixin.qq.com/cgi-bin/appmsgpublish?action=create&type=77",
        ]
        ok = False
        for url in candidate_urls:
            print(f"➡️  尝试新建图文：{url}")
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            # 检查页面是否包含「标题」「正文」编辑器特征
            if page.locator("textarea[name='title'], #title, input[name='title']").count() > 0:
                ok = True
                break
            if page.locator(".weui-desktop-editor__wrp, #js_editor_insertimage").count() > 0:
                ok = True
                break

        if not ok:
            banner(
                "自动跳转新建图文失败，可能微信后台改版了。\n"
                "  → 请在浏览器里手动点「新的创作 → 图文消息」\n"
                "  → 脚本会等 90 秒，等你到达编辑器页面再继续填表"
            )
            page.wait_for_timeout(90_000)
            print("⏰ 等待 90 秒已过，继续尝试填表（如果还没到编辑器，下面可能填不上）")

        # 3. 填表单 —— 这部分依赖当前 UI，可能要按实际选择器调
        print("\n📝 自动填写元数据...")
        try:
            # 标题
            sel_title = ["input[name='title']", "#title", "textarea[name='title']"]
            for sel in sel_title:
                if page.locator(sel).count() > 0:
                    page.locator(sel).first.fill(ARTICLE_TITLE)
                    print(f"   ✅ 标题：{ARTICLE_TITLE[:30]}...")
                    break
        except Exception as e:
            print(f"   ⚠️  标题填写失败：{e}")

        try:
            # 作者
            if ARTICLE_AUTHOR:
                sel_author = ["input[name='author']", "#author"]
                for sel in sel_author:
                    if page.locator(sel).count() > 0:
                        page.locator(sel).first.fill(ARTICLE_AUTHOR)
                        print(f"   ✅ 作者：{ARTICLE_AUTHOR}")
                        break
        except Exception as e:
            print(f"   ⚠️  作者填写失败：{e}")

        try:
            # 摘要
            sel_digest = ["textarea[name='digest']", "#digest", "textarea.js_digest"]
            for sel in sel_digest:
                if page.locator(sel).count() > 0:
                    page.locator(sel).first.fill(ARTICLE_DIGEST)
                    print(f"   ✅ 摘要：{ARTICLE_DIGEST[:30]}...")
                    break
        except Exception as e:
            print(f"   ⚠️  摘要填写失败：{e}")

        try:
            # 原文链接（需要点开「设置原文链接」入口才有 input）
            # 大多数情况下需要手动开，所以这里先尝试，不行就让用户手动
            sel_src = ["input[name='content_source_url']", "#js_content_source"]
            for sel in sel_src:
                if page.locator(sel).count() > 0:
                    page.locator(sel).first.fill(ARTICLE_SRC_URL)
                    print(f"   ✅ 原文链接：{ARTICLE_SRC_URL}")
                    break
        except Exception as e:
            print(f"   ⚠️  原文链接填写失败：{e}")

        # 4. 提示用户粘贴正文，浏览器保持打开 15 分钟
        banner(
            "📋 HTML 正文已在剪贴板。\n"
            "  下一步在浏览器里手动操作：\n"
            "    1. 点正文编辑区（让光标进去）\n"
            "    2. 按 Cmd+V 粘贴（剪贴板里就是 HTML）\n"
            "    3. 等编辑器自动拉取 7 张外链图\n"
            "    4. 检查格式 / 标题 / 摘要\n"
            "    5. 点右上「保存为草稿」\n"
            "    6. 之后去公众号 App → 草稿箱 → 群发\n"
            "  浏览器会挂着 15 分钟，给你充裕时间做。"
        )
        # 15 分钟挂机，让用户充裕时间完成手动步骤
        try:
            page.wait_for_timeout(900_000)
        except Exception:
            pass

        browser.close()
        print("\n✅ 浏览器自动关闭。如果你已经保存草稿，剩下的群发步骤在公众号 App 里完成。")
        print("   如果还没保存，重新跑：python3 scripts/wechat_publish.py")


if __name__ == "__main__":
    main()
