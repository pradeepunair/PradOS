# Website Chatbot — Product Requirements Document

**Owner:** Pradeep Nair
**Status:** Draft
**Last Updated:** 2026-03-17
**Version:** 1.0

---

## 1. Problem Statement

Visitors to pradeepunair.me have no interactive way to explore Pradeep's professional background, case studies, or blog content. They must navigate multiple static pages to piece together his story. A RAG-based chatbot provides a low-friction, conversational layer on top of existing site content — letting recruiters, collaborators, and blog readers get answers instantly without leaving the page.

---

## 2. Goals

- Enable visitors to ask natural-language questions answered exclusively from pradeepunair.me content
- Surface case studies and blog posts proactively in responses with direct links
- Protect personal info: share email for contact only, block all other PII
- Stay current automatically as the site is updated with new blogs or case studies

## Non-Goals (V1)

- Multi-language support
- Voice / audio chat
- User authentication or session persistence
- Analytics dashboard or conversation logging UI
- Admin CMS for content management

---

## 3. Users

| User Type | Description | Key Need |
|-----------|-------------|----------|
| Recruiters | Evaluating Pradeep for Director/Senior PM roles | Quick experience summary + links to case studies |
| Collaborators | Assessing domain expertise before reaching out | Payments/fintech/AI signal without cold email |
| Blog readers | Curious about the author behind a post | Context on who Pradeep is and his broader work |

---

## 4. Requirements

### Functional

| # | Requirement | Priority | Notes |
|---|-------------|----------|-------|
| F1 | Content indexer — parse site HTML, chunk text (~500 tokens), generate embeddings | Must have | Source: `website_files.git` |
| F2 | Vector store — store and query embeddings for semantic retrieval | Must have | FAISS (local file, no cloud dependency) |
| F3 | RAG chat endpoint — embed query → retrieve top-k passages → Claude generates answer | Must have | Model: claude-sonnet-4-6 |
| F4 | Privacy guardrails — system prompt + post-processing filter blocks restricted info | Must have | See Privacy Rules table below |
| F5 | Standalone `/chat/` page on pradeepunair.me | Must have | Linked from site nav or footer |
| F6 | Embedded floating widget popup on all pages | Must have | Bubble → expandable chat window on click |
| F7 | Source citations in responses | Should have | Link to relevant page (e.g. "See ACH case study →") |
| F8 | Auto-refresh pipeline — re-index on git push or daily cron | Should have | Webhook (option A) or cron (option B) |
| F9 | Rate limiting on API | Must have | 20 requests/min per IP to prevent abuse |

### Non-Functional

- **Latency:** Chat response < 3s for typical queries
- **Privacy:** No PII (phone, address, salary) ever returned; enforced at system prompt + filter layer
- **Availability:** API hosted on Render/Railway free tier — acceptable cold start latency
- **CORS:** API must allow requests from `pradeepunair.me` only
- **Cost:** Target < $5/mo total at ~50 chats/day

---

## 5. Privacy Rules

System prompt must enforce: *"Only share information present on pradeepunair.me. For contact, share email only."*

| Allowed to Share | NOT Allowed to Share |
|------------------|----------------------|
| Email: pradeepunair@gmail.com | Phone number |
| Professional title & experience summary | Home address / exact location |
| Case study details (ACH, Credit Card, APM) | Salary or compensation details |
| Blog post content & summaries | Private social accounts |
| Skills, domain expertise (payments, fintech, AI) | Info not present on the website |
| LinkedIn, GitHub, Twitter/X profile links | Personal opinions not published on site |

---

## 6. Solution Design

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Website (pradeepunair.me — cPanel/LiteSpeed)        │
│  ┌──────────┐  ┌──────────────────────────────────┐  │
│  │ /chat/   │  │ Widget popup (all pages)          │  │
│  │ page     │  │ Floating bubble → chat window     │  │
│  └────┬─────┘  └────────────┬─────────────────────┘  │
│       └──────────┬──────────┘                         │
└──────────────────┼────────────────────────────────────┘
                   │ HTTPS API calls
        ┌──────────▼──────────┐
        │  Chat Backend       │
        │  FastAPI (Python)   │
        │  POST /api/chat     │
        │  Claude API         │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Vector Store       │
        │  FAISS (local file) │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Content Indexer    │
        │  HTML → chunks →    │
        │  embeddings         │
        └─────────────────────┘
```

### Content Sources to Index

| Source | Path in `website_files.git` | Content Type |
|--------|-----------------------------|--------------|
| Homepage | `index.html` | Intro, headline, skills summary |
| About | `about/index.html` | Professional background, experience |
| Case Study: ACH | `case-studies/ach-global-launch/index.html` | ACH global launch, 32% settlement risk reduction |
| Case Study: Credit Card | `case-studies/credit-card-redesign/index.html` | Card redesign, 28% conversion increase |
| Case Study: APM | `case-studies/apm-integration/index.html` | Alt payment methods, 45% market reach expansion |
| Blog posts | `blog/*/index.html` | ISO 20022, PM lessons, embedded finance |
| Contact | `contact/index.html` | Email only (filtered by privacy layer) |

### Modules to Build (in order)

- [ ] `src/indexer.py` — parse HTML pages (BeautifulSoup4), extract text, chunk into ~500-token passages
- [ ] `src/embedder.py` — generate embeddings (OpenAI `text-embedding-3-small` or Voyage), store in FAISS
- [ ] `src/retriever.py` — query vector store, return top-k passages with source URLs
- [ ] `src/chat.py` — Claude API call: system prompt (privacy rules) + retrieved context + user query
- [ ] `src/privacy.py` — post-processing filter to catch any PII leakage before returning response
- [ ] `src/api.py` — FastAPI server: `POST /api/chat` (accepts message, returns response + sources), rate limiter
- [ ] `frontend/chat-page.html` — standalone `/chat/` page (message bubbles, typing indicator, source links)
- [ ] `frontend/widget.js` — embeddable floating bubble + expandable chat window
- [ ] `frontend/widget.css` — widget styling (matches site's gradient/dark theme)
- [ ] `scripts/reindex.py` — CLI to re-scrape site and rebuild vector store
- [ ] `scripts/deploy_widget.py` — inject widget `<script>` tag into all site HTML pages
- [ ] `.env.example` — API keys template
- [ ] `requirements.txt` — fastapi, uvicorn, faiss-cpu, beautifulsoup4, anthropic, openai, python-dotenv
- [ ] `brief.md` — project brief

### Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| Backend | Python FastAPI | Lightweight, async, easy to deploy |
| LLM | Claude (claude-sonnet-4-6) | Best quality/cost for conversational Q&A |
| Embeddings | OpenAI `text-embedding-3-small` | Low cost (~$0.02/1M tokens), strong retrieval |
| Vector store | FAISS (local) | No cloud dependency, fast, file-based |
| HTML parsing | BeautifulSoup4 | Reliable HTML text extraction |
| Frontend | Vanilla JS + CSS | No build step, works with static cPanel hosting |
| API hosting | Render / Railway (free tier) | Separate from cPanel — needs Python runtime |
| Widget hosting | cPanel (same as site) | Static JS/CSS injected into existing pages |

### Content Refresh Strategy

| Trigger | Mechanism |
|---------|-----------|
| Manual | `python scripts/reindex.py` after adding blog/case study |
| Automated (Option A) | GitHub webhook on push to `website_files.git` → calls `/api/reindex` on API server |
| Automated (Option B) | Daily cron on API server — pulls latest HTML, re-indexes if content hash changed |
| Cache busting | Widget JS loaded with version query param (`widget.js?v=YYYYMMDD`) |

### Deployment Notes

- **API server** must be hosted separately (cPanel doesn't run Python servers) — use Render/Railway free tier
- **Widget JS + CSS** are static files deployed to cPanel alongside site HTML
- **Chat page** (`/chat/index.html`) is a static HTML page on cPanel that calls the API
- **CORS** configured on FastAPI to allow requests from `pradeepunair.me` only
- **Website repo:** `git@github.com:pradeepunair/website_files.git`
- **Live site:** `https://pradeepunair.me`

---

## 7. Open Questions

| Question | Owner | Due Date | Status |
|----------|-------|----------|--------|
| Which auto-refresh option: webhook (A) or daily cron (B)? | Pradeep | 2026-04-01 | Open |
| Embedding provider: OpenAI or Voyage? (Voyage has no separate API key needed if using Anthropic) | Pradeep | 2026-04-01 | Open |
| Where to show chat link in site nav — header, footer, or both? | Pradeep | 2026-04-01 | Open |

---

## 8. Success Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| Chat widget clicks | 0 | 20% of unique visitors interact | Plausible/analytics on site |
| Response relevance | — | < 5% off-topic or hallucinated answers | Manual spot-check weekly |
| Privacy compliance | — | 0 incidents of blocked info shared | Post-processing filter log |
| Monthly API cost | $0 | < $5/mo | Anthropic + OpenAI dashboards |
| Index freshness | Manual only | Auto-refresh within 24hrs of site push | Reindex log timestamps |

---

## 9. Timeline

| Milestone | Date | Owner |
|-----------|------|-------|
| PRD approved | 2026-03-17 | Pradeep |
| Indexer + vector store working locally | TBD | Pradeep |
| RAG chat endpoint functional | TBD | Pradeep |
| Widget + chat page deployed to staging | TBD | Pradeep |
| Privacy filter validated | TBD | Pradeep |
| Live on pradeepunair.me | TBD | Pradeep |
