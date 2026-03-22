#!/usr/bin/env python3
"""
reindex.py — Rebuild the chatbot vector index from website HTML files.

Run this after updating the website (new blog posts, case study edits, etc.).

Usage:
  cd Projects/WebsiteChatbot
  python scripts/reindex.py
"""

import sys
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

import indexer
import embedder


def main():
    print("=" * 50)
    print("  Website Chatbot — Reindex")
    print("=" * 50)
    print(f"\n  Website path: {indexer.WEBSITE_PATH}")
    print(f"  Base URL:     {indexer.WEBSITE_BASE_URL}\n")

    if not indexer.WEBSITE_PATH.exists():
        print(f"  ERROR: Website path not found.\n  Update WEBSITE_PATH in .env")
        sys.exit(1)

    print("Step 1 — Parsing HTML files...")
    chunks = indexer.get_all_chunks()

    if not chunks:
        print("\n  ERROR: No chunks extracted. Check that HTML files exist at the target paths.")
        sys.exit(1)

    print(f"\nStep 2 — Building embeddings + FAISS index...")
    embedder.build_index(chunks)

    print(f"\n  Done. Restart the API server to use the updated index.")
    print("=" * 50)


if __name__ == "__main__":
    main()
