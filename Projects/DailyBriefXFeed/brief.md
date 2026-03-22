# DailyBrief — X Feed Extension — Brief

**Started:** 2026-03-16
**Owner:** Pradeep Nair
**Status:** Complete

---

## Problem

DailyBrief covers news articles but misses real-time signal from people Pradeep follows on X — where fintech and AI conversations often happen first.

## Goal

Add a third section to the DailyBrief email: top 5 posts from Pradeep's X home timeline in the past 24 hours, filtered by engagement, summarized by Claude. Falls back gracefully if the scraper breaks.

## Constraints

- Timeline: Flexible
- Resources: `twscrape` (open source, free), Claude API for summaries
- Scope: X only — no LinkedIn. Read-only, no posting.
- Risk: `twscrape` breaks every 2-4 weeks when X updates defenses; community patches within a week

## Approach

1. `src/x_collector.py` — `twscrape` wrapper, fetch top 5 posts from home timeline past 24hrs, ranked by engagement (likes + retweets)
2. Update `src/digest_builder.py` — add X section after Payments and AI sections
3. Update `src/main.py` — wire in X collector wrapped in try/except fallback
4. Add X credentials to `.env`

## Open Questions

- [ ] X account credentials needed — add `X_USERNAME`, `X_PASSWORD`, `X_EMAIL` to DailyBrief `.env`
- [ ] How many posts to show — 5 is the plan, confirm before building

## Links

- PRD: Tasks/backlog.md → DailyBrief Social Feed Extension section
- Extends: Projects/DailyBrief/
- Dependency: `pip install twscrape`
