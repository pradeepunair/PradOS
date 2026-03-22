"""
jd_scraper.py — Job Description scraper for ResumePrep agent

Accepts a job URL or raw JD text.
Returns structured JD content: title, company, location, requirements, responsibilities.

Supported job boards (specific parsers):
  - Greenhouse (job-boards.greenhouse.io)
  - Lever (jobs.lever.co)
  - Workday (*.myworkdayjobs.com)

All other URLs fall back to generic text extraction.
Raw text input is passed directly to Claude for structuring.
"""

import os
import re
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup
import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def scrape_jd(input_text: str) -> dict:
    """
    Accept a URL or raw JD text. Return structured JD dict.

    Returns:
        {
            "company": str,
            "title": str,
            "location": str,
            "raw_text": str,
            "structured": {
                "responsibilities": [str],
                "required_skills": [str],
                "preferred_skills": [str],
                "seniority": str,
                "domain": str
            }
        }
    """
    is_url = input_text.strip().startswith("http")

    if is_url:
        url = input_text.strip()
        logger.info(f"[jd_scraper] Fetching URL: {url}")
        raw_text, metadata = _fetch_url(url)
    else:
        logger.info("[jd_scraper] Using raw JD text input")
        raw_text = input_text.strip()
        metadata = {"company": "", "title": "", "location": ""}

    if not raw_text:
        raise ValueError("Could not extract job description content.")

    structured = _structure_with_claude(raw_text, metadata)

    return {
        "company": structured.get("company") or metadata.get("company", ""),
        "title": structured.get("title") or metadata.get("title", ""),
        "location": structured.get("location") or metadata.get("location", ""),
        "raw_text": raw_text,
        "structured": {
            "responsibilities": structured.get("responsibilities", []),
            "required_skills": structured.get("required_skills", []),
            "preferred_skills": structured.get("preferred_skills", []),
            "seniority": structured.get("seniority", ""),
            "domain": structured.get("domain", ""),
        },
    }


# ---------------------------------------------------------------------------
# URL fetcher — routes to board-specific or generic parser
# ---------------------------------------------------------------------------

def _fetch_url(url: str) -> tuple[str, dict]:
    if "greenhouse.io" in url:
        return _parse_greenhouse(url)
    elif "lever.co" in url:
        return _parse_lever(url)
    elif "myworkdayjobs.com" in url:
        return _parse_workday(url)
    else:
        return _parse_generic(url)


# ---------------------------------------------------------------------------
# Board-specific parsers
# ---------------------------------------------------------------------------

def _parse_greenhouse(url: str) -> tuple[str, dict]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = _text(soup.find("h1", class_="app-title") or soup.find("h1"))
    location = _text(soup.find("div", class_="location"))

    # Company from URL: job-boards.greenhouse.io/{company}/jobs/...
    parts = url.split("/")
    company = parts[3].capitalize() if len(parts) > 3 else ""

    content_div = (
        soup.find("div", id="content")
        or soup.find("div", class_="job-post")
        or soup.find("div", {"class": re.compile(r"content|description", re.I)})
    )
    raw_text = content_div.get_text(separator="\n", strip=True) if content_div else soup.get_text(separator="\n", strip=True)

    return raw_text, {"company": company, "title": title, "location": location}


def _parse_lever(url: str) -> tuple[str, dict]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = _text(soup.find("h2"))
    location = _text(soup.find("div", class_="location"))
    company = _text(soup.find("div", class_="main-header-text posting-category"))

    content_div = soup.find("div", class_="content") or soup.find("div", class_="section-wrapper")
    raw_text = content_div.get_text(separator="\n", strip=True) if content_div else soup.get_text(separator="\n", strip=True)

    return raw_text, {"company": company, "title": title, "location": location}


def _parse_workday(url: str) -> tuple[str, dict]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Workday is heavily JS-rendered; extract what's available in initial HTML
    title = _text(soup.find("h2") or soup.find("h1"))
    raw_text = soup.get_text(separator="\n", strip=True)

    # Company from subdomain: company.myworkdayjobs.com
    company = url.split(".")[0].replace("https://", "").capitalize()

    return raw_text, {"company": company, "title": title, "location": ""}


def _parse_generic(url: str) -> tuple[str, dict]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove nav, footer, scripts, styles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = _text(soup.find("h1"))
    raw_text = soup.get_text(separator="\n", strip=True)

    # Clean up excessive whitespace
    raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)

    return raw_text, {"company": "", "title": title, "location": ""}


# ---------------------------------------------------------------------------
# Claude structurer — converts raw text into clean schema
# ---------------------------------------------------------------------------

def _structure_with_claude(raw_text: str, metadata: dict) -> dict:
    client = anthropic.Anthropic()

    # Trim raw text to avoid token bloat (first 4000 chars usually has full JD)
    trimmed = raw_text[:4000]

    prompt = f"""Extract structured information from this job description. Return ONLY valid JSON with these exact keys:

{{
  "company": "company name",
  "title": "job title",
  "location": "location or Remote",
  "seniority": "IC / Senior IC / Manager / Director / VP / C-level",
  "domain": "primary domain e.g. Payments, BNPL, Risk, Platform, Growth",
  "responsibilities": ["list of key responsibilities, max 8"],
  "required_skills": ["hard and soft skills explicitly required"],
  "preferred_skills": ["nice-to-have or preferred skills"]
}}

Known metadata (use if not found in text):
- Company: {metadata.get('company', 'unknown')}
- Title: {metadata.get('title', 'unknown')}
- Location: {metadata.get('location', 'unknown')}

Job Description:
{trimmed}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    # Extract JSON block
    import json
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        logger.warning("[jd_scraper] Claude did not return valid JSON — returning raw")
        return {
            "company": metadata.get("company", ""),
            "title": metadata.get("title", ""),
            "location": metadata.get("location", ""),
            "responsibilities": [],
            "required_skills": [],
            "preferred_skills": [],
            "seniority": "",
            "domain": "",
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _text(tag) -> str:
    return tag.get_text(strip=True) if tag else ""


# ---------------------------------------------------------------------------
# CLI test entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import json
    import pprint

    logging.basicConfig(level=logging.INFO)

    input_arg = sys.argv[1] if len(sys.argv) > 1 else "https://job-boards.greenhouse.io/affirm/jobs/7615044003"
    result = scrape_jd(input_arg)

    print(f"\n=== JD: {result['title']} @ {result['company']} ===")
    print(f"Location : {result['location']}")
    print(f"Seniority: {result['structured']['seniority']}")
    print(f"Domain   : {result['structured']['domain']}")
    print(f"\n--- Responsibilities ---")
    for r in result["structured"]["responsibilities"]:
        print(f"  • {r}")
    print(f"\n--- Required Skills ---")
    for s in result["structured"]["required_skills"]:
        print(f"  • {s}")
    print(f"\n--- Preferred Skills ---")
    for s in result["structured"]["preferred_skills"]:
        print(f"  • {s}")
