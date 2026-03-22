"""
news_fetcher.py — Company news research module for ResumePrep agent

Fallback chain:
  1. Brave Search API  (primary)
  2. NewsAPI           (when Brave quota exhausted)
  3. Claude web search (final fallback)
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import requests
import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

BRAVE_NEWS_URL = "https://api.search.brave.com/res/v1/news/search"
NEWSAPI_URL = "https://newsapi.org/v2/everything"


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def fetch_company_news(company: str, days: int = 60) -> dict:
    """
    Fetch recent news for a company using the fallback chain.

    Returns:
        {
            "company": str,
            "source": "brave" | "newsapi" | "claude",
            "articles": [ {"title": str, "url": str, "published": str, "summary": str} ],
            "digest": str   # Claude-written 2-3 paragraph summary
        }
    """
    articles = None
    source = None

    # 1. Try Brave
    if BRAVE_API_KEY:
        try:
            articles = _fetch_brave(company, days)
            source = "brave"
            logger.info(f"[news] Brave returned {len(articles)} articles for '{company}'")
        except QuotaExceeded:
            logger.warning("[news] Brave quota exhausted — falling back to NewsAPI")
        except Exception as e:
            logger.warning(f"[news] Brave failed ({e}) — falling back to NewsAPI")

    # 2. Try NewsAPI
    if articles is None and NEWSAPI_KEY:
        try:
            articles = _fetch_newsapi(company, days)
            source = "newsapi"
            logger.info(f"[news] NewsAPI returned {len(articles)} articles for '{company}'")
        except Exception as e:
            logger.warning(f"[news] NewsAPI failed ({e}) — falling back to Claude")

    # 3. Claude web search fallback
    if articles is None:
        logger.info("[news] Using Claude web search fallback")
        return _fetch_claude(company, days)

    digest = _summarize_with_claude(company, articles)

    return {
        "company": company,
        "source": source,
        "articles": articles,
        "digest": digest,
    }


# ---------------------------------------------------------------------------
# Source 1: Brave Search API
# ---------------------------------------------------------------------------

def _fetch_brave(company: str, days: int) -> list[dict]:
    query = f"{company} company news"
    # Brave freshness: "pd"=day, "pw"=week, "pm"=month
    # For ~60 days we run two calls: last month + previous month via date filter
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    params = {
        "q": query,
        "count": 20,
        "freshness": "pm",  # past month — run twice to cover ~60 days
        "text_decorations": False,
        "search_lang": "en",
    }

    resp = requests.get(BRAVE_NEWS_URL, headers=headers, params=params, timeout=10)

    if resp.status_code == 429:
        raise QuotaExceeded("Brave Search API quota exceeded")
    resp.raise_for_status()

    data = resp.json()
    results = data.get("results", [])

    articles = []
    cutoff = datetime.utcnow() - timedelta(days=days)

    for item in results:
        published_str = item.get("age") or item.get("page_age", "")
        articles.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "published": published_str,
            "summary": item.get("description", ""),
        })

    return articles


# ---------------------------------------------------------------------------
# Source 2: NewsAPI
# ---------------------------------------------------------------------------

def _fetch_newsapi(company: str, days: int) -> list[dict]:
    from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = datetime.utcnow().strftime("%Y-%m-%d")

    params = {
        "q": f'"{company}"',
        "from": from_date,
        "to": to_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWSAPI_KEY,
    }

    resp = requests.get(NEWSAPI_URL, params=params, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"NewsAPI error: {data.get('message')}")

    articles = []
    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "published": item.get("publishedAt", "")[:10],  # YYYY-MM-DD
            "summary": item.get("description", "") or item.get("content", "")[:300],
        })

    return articles


# ---------------------------------------------------------------------------
# Source 3: Claude web search fallback
# ---------------------------------------------------------------------------

def _fetch_claude(company: str, days: int) -> dict:
    client = anthropic.Anthropic()
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    prompt = (
        f"Search for recent news about {company} published after {cutoff_date}. "
        f"Focus on: funding rounds, leadership changes, product launches, layoffs, "
        f"partnerships, regulatory actions, and earnings. "
        f"Return a structured JSON with keys: articles (list of title/url/published/summary) "
        f"and digest (2-3 paragraph narrative summary of the company's recent trajectory)."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text content from response
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    # Try to parse JSON; fall back to treating the whole response as the digest
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            parsed = json.loads(text[start:end])
            return {
                "company": company,
                "source": "claude",
                "articles": parsed.get("articles", []),
                "digest": parsed.get("digest", text),
            }
    except json.JSONDecodeError:
        pass

    return {
        "company": company,
        "source": "claude",
        "articles": [],
        "digest": text,
    }


# ---------------------------------------------------------------------------
# Summarizer — runs after Brave or NewsAPI fetch
# ---------------------------------------------------------------------------

def _summarize_with_claude(company: str, articles: list[dict]) -> str:
    if not articles:
        return f"No recent news found for {company}."

    client = anthropic.Anthropic()

    article_text = "\n".join(
        f"- [{a['published']}] {a['title']}: {a['summary']}"
        for a in articles[:15]  # cap to avoid token bloat
    )

    prompt = (
        f"Based on these recent news headlines about {company}, write a 2-3 paragraph "
        f"company profile digest. Cover: what the company does, their current trajectory, "
        f"any notable recent developments (funding, product, leadership, risk). "
        f"Tone: neutral, factual, useful for a job candidate doing pre-interview research.\n\n"
        f"Headlines:\n{article_text}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class QuotaExceeded(Exception):
    pass


# ---------------------------------------------------------------------------
# CLI test entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import pprint

    logging.basicConfig(level=logging.INFO)

    company = sys.argv[1] if len(sys.argv) > 1 else "Affirm"
    result = fetch_company_news(company)

    print(f"\n=== News for {result['company']} (source: {result['source']}) ===\n")
    print(f"Articles found: {len(result['articles'])}\n")
    for a in result["articles"]:
        print(f"  [{a['published']}] {a['title']}")
        print(f"  {a['url']}\n")
    print("=== Digest ===")
    print(result["digest"])
