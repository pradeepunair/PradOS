# DailyBrief — Brief

**Started:** 2026-03-15
**Owner:** Pradeep Nair
**Status:** Active

---

## Problem

Staying current on Payments/BNPL and AI news requires manually checking multiple sources daily — slow and inconsistent.

## Goal

A daily automated email digest with top 3 news articles per topic (Payments, AI), each with a 2-3 sentence summary and source link. Delivered to inbox at 7 AM CST. Zero manual effort after setup.

## Constraints

- Timeline: Flexible
- Resources: Brave Search API, Claude API, Gmail SMTP — all free tier
- Scope: Top 3 articles per topic only. Email delivery only in v1 (no SMS).

## Stakeholders

| Name | Role | Involvement |
|------|------|------------|
| Pradeep Nair | Owner | Builder + sole consumer |

## Approach

1. `news_collector.py` — Brave Search API, 2 topic queries/day, freshness=pd with pw fallback
2. `summarizer.py` — Claude writes 2-3 sentence paragraph per article (per-article calls)
3. `digest_builder.py` — HTML (inline CSS) + markdown output
4. `email_sender.py` — Gmail SMTP, multipart HTML + plain-text
5. `main.py` — orchestrator, saves output/YYYY-MM-DD-digest.md, runs via cron at 7 AM CST

## Open Questions

- [ ] Gmail App Password — needs to be generated and added to .env
- [ ] Confirm delivery address for digest email

## Links

- PRD: Tasks/backlog.md → DailyBrief section
- Reuse: Projects/ResumePrep/src/news_fetcher.py (Brave + Claude patterns)
- Output: output/ folder
