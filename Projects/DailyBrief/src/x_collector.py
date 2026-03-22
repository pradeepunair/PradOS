"""
x_collector.py — Fetches top X posts using twikit (cookie-based, no API key).

Requires Python 3.11+. Run with: python3.11 x_collector.py

Auth: Cookie-based via twikit's load_cookies().
Cookie file is generated on first login and reused on subsequent runs.

.env vars:
  X_USERNAME, X_EMAIL, X_PASSWORD, X_AUTH_TOKEN, X_CT0
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
import twikit

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

X_USERNAME   = os.getenv("X_USERNAME", "")
X_EMAIL      = os.getenv("X_EMAIL", "")
X_PASSWORD   = os.getenv("X_PASSWORD", "")
X_AUTH_TOKEN = os.getenv("X_AUTH_TOKEN", "")
X_CT0        = os.getenv("X_CT0", "")

MAX_POSTS    = 5
LOOKBACK_HRS = 24

COOKIES_FILE = Path(__file__).parent.parent / ".x_cookies.json"

# Search queries — top posts across both domains
X_QUERIES = [
    "payments fintech BNPL lang:en min_faves:10",
    "AI LLM OpenAI Anthropic Claude lang:en min_faves:10",
]


async def _fetch_posts() -> list[dict]:
    client = twikit.Client(language="en-US")

    # Prefer saved cookie file; fall back to env cookies; fall back to login
    if COOKIES_FILE.exists():
        client.load_cookies(str(COOKIES_FILE))
        logger.info("[x_collector] Loaded cookies from file")
    elif X_AUTH_TOKEN and X_CT0:
        # Write in twikit-compatible format (list of cookie dicts)
        cookies = [
            {"name": "auth_token", "value": X_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0",        "value": X_CT0,        "domain": ".x.com", "path": "/"},
        ]
        COOKIES_FILE.write_text(json.dumps(cookies))
        client.load_cookies(str(COOKIES_FILE))
        logger.info("[x_collector] Loaded cookies from env vars")
    else:
        logger.info("[x_collector] Logging in with username/password")
        await client.login(
            auth_info_1=X_USERNAME,
            auth_info_2=X_EMAIL,
            password=X_PASSWORD,
        )
        client.save_cookies(str(COOKIES_FILE))
        logger.info(f"[x_collector] Cookies saved to {COOKIES_FILE}")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HRS)
    posts  = []
    seen   = set()

    for query in X_QUERIES:
        try:
            results = await client.search_tweet(query, product="Latest", count=20)
            for tweet in results:
                if tweet.id in seen:
                    continue
                # Parse tweet date
                try:
                    tweet_date = datetime.strptime(
                        tweet.created_at, "%a %b %d %H:%M:%S +0000 %Y"
                    ).replace(tzinfo=timezone.utc)
                except Exception:
                    tweet_date = datetime.now(timezone.utc)

                # Soft date filter — warn but don't skip (avoids 0 results from clock drift)
                if tweet_date < cutoff:
                    logger.debug(f"[x_collector] Skipping old tweet: {tweet_date}")

                seen.add(tweet.id)
                likes    = tweet.favorite_count or 0
                retweets = tweet.retweet_count or 0
                posts.append({
                    "id":        tweet.id,
                    "author":    tweet.user.screen_name if tweet.user else "unknown",
                    "text":      tweet.full_text or tweet.text or "",
                    "url":       f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}" if tweet.user else "",
                    "published": tweet_date.strftime("%Y-%m-%d %H:%M UTC"),
                    "likes":     likes,
                    "retweets":  retweets,
                    "score":     likes + (retweets * 2),
                })
        except Exception as e:
            logger.warning(f"[x_collector] Search failed for '{query}': {e}")

    posts.sort(key=lambda p: p["score"], reverse=True)
    return posts[:MAX_POSTS]


def fetch_x_posts() -> list[dict]:
    """Synchronous wrapper. Returns [] on any failure."""
    if not (X_USERNAME or COOKIES_FILE.exists()):
        logger.warning("[x_collector] No X credentials — skipping")
        return []

    try:
        posts = asyncio.run(_fetch_posts())
        logger.info(f"[x_collector] Fetched {len(posts)} posts from X")
        return posts
    except Exception as e:
        logger.error(f"[x_collector] Failed: {e}")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    posts = fetch_x_posts()
    print(f"\n=== Top {len(posts)} X posts (past {LOOKBACK_HRS}hrs) ===\n")
    for p in posts:
        print(f"@{p['author']} [{p['published']}] ❤️ {p['likes']} 🔁 {p['retweets']}")
        print(f"  {p['text'][:120]}...")
        print(f"  {p['url']}\n")
