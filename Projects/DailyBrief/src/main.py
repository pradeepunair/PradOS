"""
main.py — DailyBrief orchestrator. Run this daily via cron.

Pipeline:
  1. Fetch top 3 articles per topic (Brave)
  2. Summarize each article (Claude)
  3. Build markdown + HTML digest
  4. Save to output/YYYY-MM-DD-digest.md
  5. Send via Gmail SMTP

Markdown output is saved BEFORE email is attempted —
so the digest is never lost due to email failure.
"""

import os
import sys
import logging
from datetime import date
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from news_collector import fetch_all_topics
from summarizer import summarize_all
from digest_builder import build_markdown_digest, build_html_digest
from email_sender import send_digest
from x_collector import fetch_x_posts

OUTPUT_DIR = Path(__file__).parent.parent / "output"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_daily_brief() -> None:
    today = date.today().strftime("%Y-%m-%d")
    logger.info(f"=== DailyBrief starting — {today} ===")

    # 1. Fetch
    logger.info("Fetching news...")
    raw = fetch_all_topics()
    total = sum(len(v) for v in raw.values())
    logger.info(f"Fetched {total} articles across {len(raw)} topics")

    # 2. Summarize
    logger.info("Summarizing with Claude...")
    enriched = summarize_all(raw)

    # 3. Fetch X posts (graceful fallback — never blocks the email)
    logger.info("Fetching X posts...")
    x_posts = []
    try:
        x_posts = fetch_x_posts()
        logger.info(f"X: {len(x_posts)} posts fetched")
    except Exception as e:
        logger.warning(f"X fetch failed — skipping section: {e}")

    # 4. Build digest
    markdown = build_markdown_digest(enriched, today, x_posts=x_posts)
    html     = build_html_digest(enriched, today, x_posts=x_posts)

    # 5. Save markdown (always, before email attempt)
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{today}-digest.md"
    output_file.write_text(markdown)
    logger.info(f"Digest saved → {output_file}")

    # 6. Send email
    subject = f"DailyBrief — {today}"
    try:
        send_digest(subject=subject, html_body=html, markdown_body=markdown)
        logger.info("Email delivered successfully")
    except Exception as e:
        logger.error(f"Email failed (digest still saved to output/): {e}")
        sys.exit(1)

    logger.info("=== DailyBrief complete ===")


if __name__ == "__main__":
    run_daily_brief()
