"""
summarizer.py — Writes a 2-3 sentence summary per article using Claude.

One Claude call per article for reliability and failure isolation.
"""

import os
import logging

import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

client = anthropic.Anthropic()


def summarize_all(articles_by_topic: dict) -> dict:
    """
    Summarize all articles across all topics.
    Returns same structure with 'summary' field added to each article.
    """
    enriched = {}
    for topic_key, articles in articles_by_topic.items():
        from news_collector import TOPIC_LABELS
        label = TOPIC_LABELS.get(topic_key, topic_key)
        enriched[topic_key] = summarize_topic_articles(articles, label)
    return enriched


def summarize_topic_articles(articles: list, topic_label: str) -> list:
    """Summarize each article in a topic. Returns enriched list."""
    enriched = []
    for article in articles:
        summary = summarize_article(article, topic_label)
        enriched.append({**article, "summary": summary})
    return enriched


def summarize_article(article: dict, topic_context: str) -> str:
    """
    Write a 2-3 sentence summary for a single article using Claude.
    Falls back to the raw snippet if Claude call fails.
    """
    title   = article.get("title", "")
    snippet = article.get("snippet", "")

    if not title and not snippet:
        return ""

    prompt = (
        f"Write a 2-3 sentence summary of this news article for a fintech product manager "
        f"staying current on {topic_context}. Be factual and neutral. "
        f"Do not speculate beyond what is stated. Do not start with 'This article'.\n\n"
        f"Title: {title}\n"
        f"Snippet: {snippet}"
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response.content[0].text.strip()
        logger.info(f"[summarizer] Summarized: {title[:60]}...")
        return summary
    except Exception as e:
        logger.warning(f"[summarizer] Claude failed for '{title[:40]}': {e} — using snippet")
        return snippet


if __name__ == "__main__":
    import logging
    from news_collector import fetch_all_topics, TOPIC_LABELS

    logging.basicConfig(level=logging.INFO)
    raw = fetch_all_topics()
    enriched = summarize_all(raw)

    for topic, articles in enriched.items():
        print(f"\n=== {TOPIC_LABELS[topic]} ===")
        for a in articles:
            print(f"\n  {a['title']}")
            print(f"  {a['summary']}")
