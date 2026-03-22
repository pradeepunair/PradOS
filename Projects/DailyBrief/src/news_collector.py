"""
news_collector.py — Fetches top 3 news articles per topic for DailyBrief.

Topics:
  payments → Payments, BNPL, Alternative Payment Methods, LPM, Fintech
  ai_llm   → AI, LLM, Large Language Models, Claude, OpenAI, Anthropic

Brave Search API primary source.
Freshness: past day (pd), falls back to past week (pw) if < 3 results.
"""

import os
import logging
from datetime import datetime
from typing import Optional

import json
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_NEWS_URL = "https://api.search.brave.com/res/v1/news/search"

MAX_PER_TOPIC = 3

TOPICS = {
    "payments": "payments BNPL \"buy now pay later\" alternative payment methods fintech LPM",
    "ai_llm":   "AI LLM \"large language model\" Claude OpenAI Anthropic GPT artificial intelligence",
}

TOPIC_LABELS = {
    "payments": "Payments / BNPL / Alternative Payment Methods",
    "ai_llm":   "AI & LLMs",
}


class QuotaExceeded(Exception):
    pass


def fetch_all_topics() -> dict:
    """
    Fetch top 3 articles for each topic.
    Returns: {"payments": [articles], "ai_llm": [articles]}
    """
    results = {}
    for key in TOPICS:
        results[key] = fetch_topic_articles(key)
    return results


def fetch_topic_articles(topic_key: str) -> list:
    """
    Fetch up to MAX_PER_TOPIC articles for a topic.
    Tries Brave (pd → pw), falls back to Claude web search.
    """
    # 1. Try Brave — past day
    try:
        articles = _call_brave(topic_key, freshness="pd")
        if len(articles) < MAX_PER_TOPIC:
            logger.info(f"[collector] {len(articles)} articles for '{topic_key}' today — widening to past week")
            articles = _call_brave(topic_key, freshness="pw")
        articles = articles[:MAX_PER_TOPIC]
        logger.info(f"[collector] '{topic_key}' → {len(articles)} articles (Brave)")
        return articles
    except QuotaExceeded:
        logger.warning(f"[collector] Brave quota exceeded — falling back to Claude for '{topic_key}'")
    except Exception as e:
        logger.warning(f"[collector] Brave error ({e}) — falling back to Claude for '{topic_key}'")

    # 2. Claude web search fallback
    return _fetch_claude(topic_key)


def _fetch_claude(topic_key: str) -> list:
    """Fetch top 3 articles via Claude web search tool."""
    label = TOPIC_LABELS.get(topic_key, topic_key)
    client = anthropic.Anthropic()

    prompt = (
        f"Search for the top 3 most recent and important news articles about {label} "
        f"from the past 24-48 hours. Return ONLY a JSON array with exactly this structure:\n"
        f'[{{"title":"...", "url":"...", "published":"...", "snippet":"...", "source":"..."}}]\n'
        f"No other text. Just the JSON array."
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract text blocks
        text = " ".join(b.text for b in response.content if hasattr(b, "text"))
        start, end = text.find("["), text.rfind("]") + 1
        if start != -1 and end > start:
            articles = json.loads(text[start:end])
            logger.info(f"[collector] '{topic_key}' → {len(articles)} articles (Claude)")
            return articles[:MAX_PER_TOPIC]
    except Exception as e:
        logger.error(f"[collector] Claude fallback failed for '{topic_key}': {e}")

    return []


def _call_brave(topic_key: str, freshness: str) -> list:
    if not BRAVE_API_KEY:
        raise RuntimeError("BRAVE_API_KEY not set in .env")

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    params = {
        "q": TOPICS[topic_key],
        "count": 10,
        "freshness": freshness,
        "text_decorations": False,
        "search_lang": "en",
    }

    resp = requests.get(BRAVE_NEWS_URL, headers=headers, params=params, timeout=10)

    if resp.status_code == 429:
        raise QuotaExceeded("Brave Search API quota exceeded")
    resp.raise_for_status()

    return [_normalize(item) for item in resp.json().get("results", [])]


def _normalize(item: dict) -> dict:
    return {
        "title":     item.get("title", ""),
        "url":       item.get("url", ""),
        "published": item.get("age") or item.get("page_age", ""),
        "snippet":   item.get("description", ""),
        "source":    _domain(item.get("url", "")),
    }


def _domain(url: str) -> str:
    try:
        return url.split("/")[2].replace("www.", "")
    except IndexError:
        return ""


if __name__ == "__main__":
    import pprint
    logging.basicConfig(level=logging.INFO)
    data = fetch_all_topics()
    for topic, articles in data.items():
        print(f"\n=== {TOPIC_LABELS[topic]} ===")
        for a in articles:
            print(f"  [{a['published']}] {a['title']}")
            print(f"  {a['url']}\n")
