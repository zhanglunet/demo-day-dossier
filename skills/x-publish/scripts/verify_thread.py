#!/usr/bin/env python3
"""
拉取某条 root tweet 的 thread chain，打印每条 URL 用于回填 README。

用法：
    python3 verify_thread.py <root_tweet_id>
    python3 verify_thread.py https://twitter.com/u/status/<id>

需要凭证（跟 post_thread_api.py 共用 ~/.config/x-publish/credentials.json）。
"""
import json
import os
import re
import sys
from pathlib import Path


CREDS_FILE = Path.home() / ".config" / "x-publish" / "credentials.json"


def extract_id(arg: str) -> str:
    m = re.search(r"status/(\d+)", arg)
    return m.group(1) if m else arg.strip()


def load_credentials() -> dict:
    env_creds = {
        "consumer_key": os.environ.get("X_CONSUMER_KEY"),
        "consumer_secret": os.environ.get("X_CONSUMER_SECRET"),
        "access_token": os.environ.get("X_ACCESS_TOKEN"),
        "access_token_secret": os.environ.get("X_ACCESS_TOKEN_SECRET"),
    }
    if all(env_creds.values()):
        return env_creds
    if CREDS_FILE.exists():
        return json.loads(CREDS_FILE.read_text(encoding="utf-8"))
    sys.exit(f"❌ 找不到凭证（环境变量或 {CREDS_FILE}）")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    root_id = extract_id(sys.argv[1])
    print(f"🔍 root tweet id: {root_id}", file=sys.stderr)

    try:
        import tweepy
    except ImportError:
        sys.exit("❌ 缺 tweepy。运行：pip3 install --user tweepy")

    creds = load_credentials()
    client = tweepy.Client(
        consumer_key=creds["consumer_key"],
        consumer_secret=creds["consumer_secret"],
        access_token=creds["access_token"],
        access_token_secret=creds["access_token_secret"],
    )

    # 拿 root tweet 的作者
    root = client.get_tweet(root_id, tweet_fields=["author_id", "conversation_id"])
    if not root.data:
        sys.exit(f"❌ 找不到 tweet {root_id}")
    author_id = root.data.author_id

    user = client.get_user(id=author_id)
    handle = user.data.username
    print(f"👤 author: @{handle}", file=sys.stderr)

    # X 的 conversation API（v2）查同一会话所有 tweet
    convo_id = root.data.conversation_id or root_id
    query = f"conversation_id:{convo_id} from:{handle}"
    res = client.search_recent_tweets(
        query=query, max_results=100, tweet_fields=["created_at", "referenced_tweets"]
    )

    if not res.data:
        print(f"⚠️ 只有 root，没找到后续 reply", file=sys.stderr)
        thread = [{"i": 1, "id": root_id, "url": f"https://twitter.com/{handle}/status/{root_id}"}]
    else:
        # 按时间排序
        chain = sorted([root.data] + list(res.data), key=lambda t: t.created_at if hasattr(t, "created_at") and t.created_at else "")
        thread = [
            {
                "i": idx + 1,
                "id": t.id,
                "url": f"https://twitter.com/{handle}/status/{t.id}",
            }
            for idx, t in enumerate(chain)
        ]

    print(f"\n📊 {len(thread)} 条 thread：", file=sys.stderr)
    for t in thread:
        print(f"  {t['i']}/{len(thread)}  {t['url']}", file=sys.stderr)

    print(f"\n🔗 Root URL: {thread[0]['url']}", file=sys.stderr)
    sys.stdout.write(json.dumps({"root_url": thread[0]["url"], "tweets": thread}, indent=2))


if __name__ == "__main__":
    main()
