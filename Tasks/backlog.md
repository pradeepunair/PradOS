# Backlog

Last updated: 2026-03-15

Items here are captured but not yet scheduled. Review weekly.
Move to active.md when you commit to working on something this week.

---

## Job Search

- [ ] Update resume for Director/Senior PM roles — emphasize LPM, BNPL, Digital Wallets scope
- [ ] Audit LinkedIn profile (headline, about, featured section, experience bullets)
- [ ] Build target company list — FinTech, Finance, AI-adjacent companies (20+ targets)
- [ ] Identify 5+ people to reach out to in payments / fintech network
- [ ] Set up job alert filters on LinkedIn, Greenhouse, Lever, Rippling
- [ ] Draft cover letter template for PM roles (payments angle)
- [ ] Create job application tracker in Projects/ or Notion

## Side Projects

- [ ] Inventory all current project ideas (dump into _temp/)
- [ ] Review Career Bot — assess what's built, what works, what the original goal was
- [ ] Run decision framework: pick ONE primary side project to focus on this quarter
- [ ] Define MVP scope for chosen project with success criteria
- [ ] Set up project folder in Projects/ for chosen initiative
- [ ] Build website chatbot — RAG-based assistant for pradeepunair.me → see `Projects/WebsiteChatbot/prd.md`

## AI Skill Building

- [ ] Build one tool from scratch using the Claude API (not just prompting)
- [ ] Use PradOS skills daily for 2 weeks — /standup, /weekly-update, etc.
- [ ] Explore Claude Agent SDK — understand how multi-agent workflows work
- [ ] Document 3 AI learnings or patterns in Knowledge/Research/

## PradOS Setup

- [ ] Add 3–5 key contacts to Knowledge/People/ (manager, peers, mentors)
- [ ] Create first workflow — candidate: job application process
- [ ] Test all 5 skills to confirm they produce useful outputs
- [ ] Add active.md item for each currently in-progress initiative
- [ ] Decide: keep Career Bot in launch.json or archive it

---

### DailyBrief — Social Feed Extension (LinkedIn + X) — PRD

**Goal:** Extend DailyBrief to include posts from your LinkedIn network and X accounts you follow — delivered in the same daily email.

**Project folder:** `Projects/DailyBrief/` (extends existing project)

#### ⚠️ Risk Assessment

`twscrape` works today but expect it to break every 2-4 weeks when X updates their defenses — community patches it within a week. Low maintenance, not zero.

#### Features

| # | Feature | Source | Notes |
|---|---------|--------|-------|
| 1 | X home timeline — top 5 posts from past 24hrs | `twscrape` | Filter by engagement (likes + retweets) to surface best posts |
| 2 | Summarize posts with Claude | Claude API | 1-2 sentence summary per post |
| 3 | New section in DailyBrief email | digest_builder.py | Third section after Payments and AI |
| 4 | Graceful fallback | — | If scraper breaks, skip section and send email without it |

#### Modules to Add

- [ ] `src/x_collector.py` — `twscrape` wrapper, fetch top 5 posts from home timeline past 24hrs
- [ ] Update `src/digest_builder.py` — add X section
- [ ] Update `src/main.py` — wire in X collector with try/except fallback

#### Dependencies

- `twscrape`: `pip install twscrape`
- X account credentials stored in `.env`

#### New .env vars needed
```
X_USERNAME=your_x_username
X_PASSWORD=your_x_password
X_EMAIL=your_x_email
```

#### Risk Mitigation
- Wrap collector in `try/except` — if it fails, email sends without X section
- Check `launchd.log` if X section disappears from email

---

## Projects in Progress

### ResumePrep Agent
Status: Active development — news fetcher ✅, JD scraper ✅, resume matcher pending

- [ ] Build `resume_matcher.py` — match JD skills vs resume.md, output matched/missing/fit %
- [ ] Build `main.py` — orchestrate full pipeline (JD → skills → match → company news → report)
- [ ] Update resume.md with new job roles (Pradeep to provide)
- [ ] Test full pipeline on Affirm JD: `job-boards.greenhouse.io/affirm/jobs/7615044003`

---

### DailyBrief Agent — PRD

**Goal:** Automated daily news digest covering Payments/BNPL/LPM and AI/LLMs. Top 3 articles per topic, summarized and delivered via email every morning at 7 AM CST.

**Project folder:** `Projects/DailyBrief/` (not yet created)

#### Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | News Collection | Brave Search API — top 3 articles/topic, `freshness=pd` (falls back to `pw` if < 3 results) |
| 2 | Summarization | Claude (claude-sonnet-4-6) — one 2-3 sentence paragraph per article, PM-audience tone |
| 3 | Digest Builder | Markdown + HTML output — two sections (Payments, AI), article cards with title/summary/link |
| 4 | Email Delivery | Gmail SMTP via Python `smtplib` — multipart HTML + plain-text email, self-delivered |
| 5 | Daily Scheduling | cron job at 7 AM CST — output saved to `output/YYYY-MM-DD-digest.md` regardless of email status |

#### Modules to Build (in order)

- [ ] `Projects/DailyBrief/brief.md`
- [ ] `Projects/DailyBrief/.env.example` + `.env`
- [ ] `Projects/DailyBrief/requirements.txt`
- [ ] `src/news_collector.py` — adapt `_fetch_brave()` from ResumePrep/src/news_fetcher.py
- [ ] `src/summarizer.py` — adapt `_summarize_with_claude()` from ResumePrep/src/news_fetcher.py
- [ ] `src/digest_builder.py` — HTML (inline CSS) + markdown output
- [ ] `src/email_sender.py` — Gmail SMTP, needs `GMAIL_APP_PASSWORD`
- [ ] `src/main.py` — full pipeline orchestrator
- [ ] `cron_setup.md` — cron entry + macOS LaunchAgent alternative

#### Free Tier Budget

| Service | Daily Usage | Monthly | Free Limit |
|---------|------------|---------|-----------|
| Brave Search API | 2–4 calls | ~62–124 | 2,000/mo ✅ |
| Claude Sonnet | ~2,500 tokens | ~78k tokens | Negligible cost ✅ |
| Gmail SMTP | 1 email | 31 emails | 500/day ✅ |

#### Env Vars Needed
- `BRAVE_API_KEY` — already in ResumePrep/.env
- `ANTHROPIC_API_KEY` — already in ResumePrep/.env
- `GMAIL_USER` — Gmail address
- `GMAIL_APP_PASSWORD` — 16-char app password (Gmail → Security → 2-Step → App Passwords)
- `DIGEST_RECIPIENT` — delivery address (can be same as GMAIL_USER)

#### Reuse from ResumePrep
- `_fetch_brave()` pattern → `news_collector.py`
- `_summarize_with_claude()` pattern → `summarizer.py`
- `QuotaExceeded` exception, dotenv loading, article schema `{title, url, published, snippet}`

---

### PradOS Kanban Dashboard — PRD

**Goal:** A local interactive Kanban board that visualizes all PradOS projects as cards across three swimlanes: Backlog, In Progress, and Completed. Reads project status from `Projects/*/brief.md`. Drag-and-drop moves cards and updates the source files.

**Project folder:** `Projects/KanbanBoard/` (not yet created)

#### Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Project card rendering | Each card shows: project name, one-line description, status badge, and link to brief.md |
| 2 | Three swimlanes | Backlog / In Progress / Completed — driven by `Status:` field in each `brief.md` |
| 3 | Drag-and-drop | Move cards between lanes → Flask backend updates `Status:` in the project's `brief.md` |
| 4 | Add new project | Button to scaffold a new project folder + brief.md from the UI |
| 5 | Local server | Python Flask on `localhost:5000` — single command to launch |

#### How It Works

- **Data source:** Scans `Projects/*/brief.md` (excludes `_template/`), parses `Status:` field
- **Status values:** `Discovery` → Backlog, `Active` → In Progress, `Complete` / `Paused` → Completed
- **On drag:** POST to Flask API → patch `Status:` line in brief.md on disk
- **No database:** Markdown files are the source of truth

#### Modules to Build (in order)

- [ ] `Projects/KanbanBoard/brief.md`
- [ ] `src/app.py` — Flask server, routes: `GET /`, `GET /api/projects`, `PATCH /api/projects/<name>`
- [ ] `src/board_reader.py` — scan Projects/, parse brief.md files into card dicts
- [ ] `src/templates/index.html` — Kanban UI with SortableJS drag-and-drop
- [ ] `src/static/style.css` — card/lane styling
- [ ] `requirements.txt` — Flask, python-dotenv

#### Stack

| Component | Tool |
|-----------|------|
| Backend | Python Flask |
| Frontend | Vanilla HTML/CSS + SortableJS (CDN) |
| Data | `Projects/*/brief.md` (markdown, no DB) |
| Launch | `python src/app.py` → `localhost:5000` |

#### Dependency
All projects must have a `Projects/[name]/brief.md` with a valid `Status:` field to appear on the board. Create briefs for DailyBrief and ResumePrep before building the board.

---


## Capture Zone

Dump new ideas here. Sort during weekly review.

-
