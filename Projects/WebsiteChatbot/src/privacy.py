"""
privacy.py — Post-processing filter to catch PII leakage before returning responses.

Runs as a safety net after Claude's answer is generated.
The system prompt is the primary guardrail; this is the fallback.
"""

import re
from typing import Tuple

# (pattern, replacement) pairs
PII_PATTERNS: list[tuple[str, str]] = [
    # US phone formats
    (r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", "[phone redacted]"),
    (r"\(\d{3}\)\s*\d{3}[-.\s]\d{4}\b", "[phone redacted]"),
    # International phone
    (r"\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{3,10}\b", "[phone redacted]"),
    # ZIP codes (standalone 5-digit numbers)
    (r"\b\d{5}(?:-\d{4})?\b", "[zip redacted]"),
    # Salary / compensation — only match when followed by pay-period keywords
    (
        r"\$\s*\d[\d,]*(?:\.\d+)?\s*[kKmM]?"
        r"\s*(?:per|/)\s*(?:year|yr|month|mo|hour|hr|annum|annual)\b",
        "[compensation redacted]",
    ),
]

BLOCKED_TERMS: list[str] = [
    "social security",
    "ssn",
    "passport number",
    "driver's license",
    "bank account number",
    "routing number",
    "credit card number",
]


def filter_response(text: str) -> Tuple[str, bool]:
    """
    Apply privacy filters to Claude's response.
    Returns (filtered_text, was_modified).
    """
    result = text
    modified = False

    for pattern, replacement in PII_PATTERNS:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            modified = True
            result = new

    for term in BLOCKED_TERMS:
        if term.lower() in result.lower():
            # Redact the sentence containing the blocked term
            sentence_pattern = r"[^.!?\n]*" + re.escape(term) + r"[^.!?\n]*[.!?]?"
            new = re.sub(sentence_pattern, "[information redacted]", result, flags=re.IGNORECASE)
            if new != result:
                modified = True
                result = new

    return result, modified
