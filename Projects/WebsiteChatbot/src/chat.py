"""
chat.py — RAG chat: retrieve context, call Claude, return (response, sources).
"""

import os
import anthropic
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

from retriever import retrieve

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """You are a friendly, professional AI assistant on Pradeep Nair's personal website (pradeepunair.me).
Your sole job is to answer visitor questions about Pradeep using ONLY the context passages provided to you.

ALLOWED to share:
- Professional background, title, experience (PayPal, JPMorgan Chase, Fidelity, 18+ years in payments)
- Case study details: ACH Global Launch, Credit Card Platform Redesign, APM Integration
- Skills and domain expertise: payments, fintech, BNPL, LPM, digital wallets, AI, product management
- Email address: pradeepunair@gmail.com (share only for contact requests)
- Professional profile links: LinkedIn, GitHub (if present in context)
- Blog content and summaries

NEVER share:
- Phone numbers, home address, or location beyond "Austin, TX"
- Salary, compensation, or financial details
- Any information NOT present in the provided context
- Personal opinions or views not published on the website

CONTACT rule: If asked how to reach Pradeep, share pradeepunair@gmail.com only.

If the answer is not in the context, say:
"I don't have details on that from Pradeep's website, but you can reach him directly at pradeepunair@gmail.com."

Keep answers concise (2–4 sentences unless detail is requested), professional, and helpful.
When citing facts, naturally reference the relevant area (e.g. "In Pradeep's ACH case study...").
Do NOT make up metrics, dates, or facts not in the context."""


def chat(user_message: str, top_k: int = 6) -> Tuple[str, List[Dict]]:
    """
    RAG chat pipeline.
    Returns (response_text, sources) where sources is a deduplicated list of
    {title, url} dicts for the pages used.
    """
    chunks = retrieve(user_message, top_k=top_k)

    if not chunks:
        return (
            "I don't have enough information to answer that. "
            "You can reach Pradeep directly at pradeepunair@gmail.com.",
            [],
        )

    context = "\n\n---\n\n".join(
        f"[Source: {c['source_title']} — {c['source_url']}]\n{c['text']}"
        for c in chunks
    )

    prompt = (
        f"Use the following context from Pradeep Nair's website to answer the visitor's question.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"VISITOR QUESTION: {user_message}"
    )

    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text.strip()

    # Deduplicate sources by URL, preserve relevance order
    seen: set = set()
    sources: List[Dict] = []
    for c in chunks:
        if c["source_url"] not in seen:
            seen.add(c["source_url"])
            sources.append({"title": c["source_title"], "url": c["source_url"]})

    return response_text, sources
