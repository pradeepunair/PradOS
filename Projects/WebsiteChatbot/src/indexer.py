"""
indexer.py — Parse website HTML pages into clean text chunks.

Reads from WEBSITE_PATH (env var or default local path).
Skips <header>, <footer>, <nav>, <script>, <style> boilerplate.
Returns list of chunk dicts: {id, text, source_url, source_title, chunk_index}
"""

import os
import re
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

WEBSITE_PATH = Path(
    os.getenv("WEBSITE_PATH",
              "/Users/pradeepnair/Desktop/Website/Portfolio-Website/HTMLfiles/website_files")
)
WEBSITE_BASE_URL = os.getenv("WEBSITE_BASE_URL", "https://pradeepunair.me").rstrip("/")

# HTML files to index (relative to WEBSITE_PATH)
TARGET_PATHS = [
    "index.html",
    "about/index.html",
    "case-studies/index.html",
    "case-studies/ach-global-launch/index.html",
    "case-studies/credit-card-redesign/index.html",
    "case-studies/apm-integration/index.html",
    "contact/index.html",
]

CHUNK_SIZE = 400    # words per chunk
CHUNK_OVERLAP = 60  # words of overlap between chunks
MIN_CHUNK_WORDS = 30


def _file_to_url(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    if parts[-1] == "index.html":
        parts = parts[:-1]
    path = "/".join(parts)
    return f"{WEBSITE_BASE_URL}/{path}/" if path else f"{WEBSITE_BASE_URL}/"


def _page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    tag = soup.find("title")
    if tag:
        return tag.get_text(strip=True).split("|")[0].strip()
    return "Pradeep Nair"


def _extract_nextjs_flight_text(soup: BeautifulSoup) -> str:
    """
    Extract readable text from Next.js __next_f flight data scripts.
    Used when the main HTML is sparse (content rendered client-side from JSON).
    Returns concatenated markdown/plain text strings found in the script payloads.
    """
    import json as _json
    texts = []
    for script in soup.find_all("script"):
        raw = script.get_text()
        if "__next_f" not in raw:
            continue
        # Each chunk: self.__next_f.push([<int>, "<escaped-json-string>"])
        matches = re.findall(r'self\.__next_f\.push\(\[\d+,\s*"(.*?)"\]\)', raw, re.DOTALL)
        for match in matches:
            try:
                # The payload is a JSON-escaped string — decode it
                decoded = _json.loads('"' + match + '"')
                # Keep only if it looks like prose (contains spaces and letters)
                if len(decoded) > 80 and re.search(r"[a-zA-Z]{4,}", decoded):
                    # Strip markdown syntax for cleaner indexing
                    cleaned = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", decoded)
                    cleaned = re.sub(r"#{1,4}\s+", "", cleaned)
                    cleaned = re.sub(r"-\s+", "• ", cleaned)
                    texts.append(cleaned.strip())
            except Exception:
                continue
    return "\n\n".join(texts)


def _extract_text(soup: BeautifulSoup) -> str:
    """Extract clean text from a page. Falls back to Next.js flight data if HTML is sparse."""
    # Keep a copy before stripping scripts (needed for flight fallback)
    soup_copy = BeautifulSoup(str(soup), "lxml")

    # Remove navigation boilerplate
    for tag in soup.find_all(["header", "footer", "nav", "script", "style", "noscript"]):
        tag.decompose()
    # Remove Next.js hidden hydration markers
    for tag in soup.find_all(attrs={"hidden": True}):
        tag.decompose()

    root = soup.find("main") or soup.find("body") or soup
    lines = []
    for el in root.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "blockquote"]):
        text = el.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text.split()) >= 4:
            lines.append(text)
    html_text = "\n\n".join(lines)

    # If the HTML extraction is sparse, pull richer content from Next.js flight data
    if len(html_text.split()) < 80:
        flight_text = _extract_nextjs_flight_text(soup_copy)
        if len(flight_text.split()) > len(html_text.split()):
            return (html_text + "\n\n" + flight_text).strip()

    return html_text


def _chunk(text: str) -> List[str]:
    words = text.split()
    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for i in range(0, len(words), step):
        chunk = " ".join(words[i: i + CHUNK_SIZE])
        if len(chunk.split()) >= MIN_CHUNK_WORDS:
            chunks.append(chunk)
    return chunks


def get_all_chunks() -> List[Dict]:
    """
    Parse all target HTML pages and return chunk list.
    Each chunk: {id, text, source_url, source_title, chunk_index}
    """
    chunks: List[Dict] = []
    chunk_id = 0

    for rel_path in TARGET_PATHS:
        file_path = WEBSITE_PATH / rel_path
        if not file_path.exists():
            print(f"  [skip] {rel_path} — file not found")
            continue

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "lxml")

        url = _file_to_url(rel_path)
        title = _page_title(soup)
        text = _extract_text(soup)

        if not text.strip():
            print(f"  [skip] {rel_path} — no extractable text")
            continue

        page_chunks = _chunk(text)
        for i, chunk_text in enumerate(page_chunks):
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "source_url": url,
                "source_title": title,
                "chunk_index": i,
            })
            chunk_id += 1

        print(f"  [ok]   {rel_path} → {len(page_chunks)} chunks  ({title!r})")

    print(f"\n  Total: {len(chunks)} chunks from {len(TARGET_PATHS)} target pages")
    return chunks
