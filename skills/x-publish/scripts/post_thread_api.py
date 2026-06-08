#!/usr/bin/env python3
"""
全自动发整个 X thread（OAuth 1.0a + tweepy）。

依赖：
    pip3 install --user tweepy

凭证（从 ~/.config/x-publish/credentials.json 或环境变量加载）：
    consumer_key / consumer_secret / access_token / access_token_secret

用法：
    python3 post_thread_api.py thread.json images_dir/
    python3 post_thread_api.py thread.json images_dir/ --dry-run

dry-run 模式只打印每条 + 模拟 reply chain，不真发。
"""
import json
import os
import sys
import time
import argparse
from pathlib import Path


CREDS_FILE = Path.home() / ".config" / "x-publish" / "credentials.json"


def load_credentials() -> dict:
    """优先环境变量，其次 ~/.config/x-publish/credentials.json。"""
    env_creds = {
        "consumer_key": os.environ.get("X_CONSUMER_KEY"),
        "consumer_secret": os.environ.get("X_CONSUMER_SECRET"),
        "access_token": os.environ.get("X_ACCESS_TOKEN"),
        "access_token_secret": os.environ.get("X_ACCESS_TOKEN_SECRET"),
    }
    if all(env_creds.values()):
        print("✅ 从环境变量加载凭证", file=sys.stderr)
        return env_creds

    if CREDS_FILE.exists():
        print(f"✅ 从 {CREDS_FILE} 加载凭证", file=sys.stderr)
        return json.loads(CREDS_FILE.read_text(encoding="utf-8"))

    sys.exit(
        f"❌ 找不到凭证。请：\n"
        f"  1. 设置 X_CONSUMER_KEY / X_CONSUMER_SECRET / X_ACCESS_TOKEN / X_ACCESS_TOKEN_SECRET 环境变量\n"
        f"  2. 或者写入 {CREDS_FILE}（chmod 600）\n"
        f"  申请：https://developer.twitter.com/en/portal/dashboard"
    )


def init_clients(creds: dict):
    """OAuth 1.0a User Context — 同时初始化 v1.1 API（媒体上传）+ v2 Client（发推）"""
    try:
        import tweepy
    except ImportError:
        sys.exit("❌ 缺 tweepy。运行：pip3 install --user tweepy")

    auth = tweepy.OAuth1UserHandler(
        creds["consumer_key"],
        creds["consumer_secret"],
        creds["access_token"],
        creds["access_token_secret"],
    )
    api = tweepy.API(auth)  # v1.1 用于 media/upload
    client = tweepy.Client(
        consumer_key=creds["consumer_key"],
        consumer_secret=creds["consumer_secret"],
        access_token=creds["access_token"],
        access_token_secret=creds["access_token_secret"],
    )  # v2 用于发推
    return api, client


def me_handle(api):
    try:
        u = api.verify_credentials()
        return u.screen_name
    except Exception as e:
        print(f"⚠️ verify_credentials 失败: {e}", file=sys.stderr)
        return "u"


def upload_image(api, image_path: Path) -> int:
    """媒体上传：返回 media_id。"""
    print(f"   📎 uploading {image_path.name} ({image_path.stat().st_size // 1024} KB)...", file=sys.stderr)
    media = api.media_upload(filename=str(image_path))
    return media.media_id


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("thread_json", help="thread JSON file")
    parser.add_argument("images_dir", help="directory holding tweet images")
    parser.add_argument("--dry-run", action="store_true", help="don't actually post")
    parser.add_argument("--delay", type=float, default=0.8, help="seconds between tweets (default 0.8)")
    args = parser.parse_args()

    thread_path = Path(args.thread_json)
    images_dir = Path(args.images_dir)

    if not thread_path.exists():
        sys.exit(f"❌ {thread_path} 不存在")
    if not images_dir.is_dir():
        sys.exit(f"❌ {images_dir} 不是目录")

    thread = json.loads(thread_path.read_text(encoding="utf-8"))
    tweets = thread.get("tweets", [])
    print(f"📝 待发 {len(tweets)} 条 thread", file=sys.stderr)

    if args.dry_run:
        print("\n=== DRY RUN ===\n", file=sys.stderr)
        prev_id = None
        for t in tweets:
            i = t.get("i", "?")
            text = t["text"]
            img = t.get("image", "")
            reply_to = f" (reply to {prev_id})" if prev_id else ""
            attach = f" [+{img}]" if img else ""
            print(f"Tweet {i}{reply_to}{attach}:", file=sys.stderr)
            print(f"  {text}\n", file=sys.stderr)
            prev_id = f"<would-be-id-{i}>"
        print("✅ Dry run 完成。去掉 --dry-run 真发。", file=sys.stderr)
        return

    creds = load_credentials()
    api, client = init_clients(creds)
    handle = me_handle(api)
    print(f"👤 发推账号：@{handle}", file=sys.stderr)

    prev_tweet_id = None
    posted = []

    for t in tweets:
        i = t.get("i", len(posted) + 1)
        text = t["text"]
        img_name = t.get("image")

        print(f"\n📤 Tweet {i}/{len(tweets)}...", file=sys.stderr)

        media_ids = None
        if img_name:
            img_path = images_dir / img_name
            if not img_path.exists():
                print(f"   ⚠️ 找不到 {img_path}，跳过媒体", file=sys.stderr)
            else:
                media_id = upload_image(api, img_path)
                media_ids = [media_id]

        kwargs = {"text": text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        if prev_tweet_id:
            kwargs["in_reply_to_tweet_id"] = prev_tweet_id

        try:
            resp = client.create_tweet(**kwargs)
            tweet_id = resp.data["id"]
            url = f"https://twitter.com/{handle}/status/{tweet_id}"
            print(f"   ✅ {url}", file=sys.stderr)
            posted.append({"i": i, "id": tweet_id, "url": url})
            prev_tweet_id = tweet_id
        except Exception as e:
            print(f"   ❌ 失败：{e}", file=sys.stderr)
            print("\n📋 已成功发推列表：", file=sys.stderr)
            for p in posted:
                print(f"   {p['url']}", file=sys.stderr)
            print(
                "\n🔧 修复方式：手动续上失败那条之后的 thread\n"
                "  或：调整 thread.json 删掉已发的，重新跑（用 --reply-to <last_id>）",
                file=sys.stderr,
            )
            sys.exit(1)

        time.sleep(args.delay)

    if posted:
        root_url = posted[0]["url"]
        print(f"\n🎉 Thread 全部发送完毕。", file=sys.stderr)
        print(f"🔗 Root URL: {root_url}", file=sys.stderr)
        print(f"📊 {len(posted)} tweets posted", file=sys.stderr)

        # 输出 JSON 方便回填 README
        sys.stdout.write(json.dumps({"root_url": root_url, "tweets": posted}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
