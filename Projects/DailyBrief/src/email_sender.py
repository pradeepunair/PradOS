"""
email_sender.py — Sends the daily digest via Gmail SMTP.

Requires in .env:
  GMAIL_USER         — your Gmail address
  GMAIL_APP_PASSWORD — 16-char App Password (not your Gmail login)
  DIGEST_RECIPIENT   — delivery address (can equal GMAIL_USER)

Setup: Gmail → Security → 2-Step Verification → App Passwords → Create
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

GMAIL_USER        = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
DIGEST_RECIPIENT  = os.getenv("DIGEST_RECIPIENT", GMAIL_USER)


def send_digest(subject: str, html_body: str, markdown_body: str) -> None:
    """
    Send digest as multipart/alternative email (HTML + plain-text fallback).
    Raises on auth or send failure.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise RuntimeError(
            "GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env\n"
            "Setup: Gmail → Security → 2-Step Verification → App Passwords"
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = DIGEST_RECIPIENT

    msg.attach(MIMEText(markdown_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, DIGEST_RECIPIENT, msg.as_string())

    logger.info(f"[email] Digest sent to {DIGEST_RECIPIENT}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    send_digest(
        subject="DailyBrief — test email",
        html_body="<h1>Test</h1><p>HTML email is working.</p>",
        markdown_body="# Test\n\nPlain text email is working.",
    )
    print("Test email sent — check your inbox.")
