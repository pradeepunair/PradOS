# WebsiteChatbot — Brief

**Started:** 2026-03-17
**Owner:** Pradeep Nair
**Status:** Discovery

---

## Problem

Visitors to pradeepunair.me have no interactive way to explore Pradeep's case studies, blog posts, and background without navigating multiple static pages.

## Goal

A RAG-based chatbot for pradeepunair.me that answers visitor questions from site content — available as a standalone `/chat/` page and an embedded floating widget on all pages. Privacy-safe: shares email only, no PII.

## Constraints

- Privacy: Only info from website — email for contact, no phone/address/salary
- Hosting: API must be separate from cPanel (Render/Railway free tier); widget is static JS on cPanel
- Budget: < $5/mo at ~50 chats/day
- Source: `git@github.com:pradeepunair/website_files.git`

## Stakeholders

| Name | Role | Involvement |
|------|------|------------|
| Pradeep Nair | Owner | Builder + sole user |

## Approach

1. Index site HTML → chunk → embed → FAISS vector store
2. FastAPI backend: RAG endpoint (retrieve → Claude answer + citations) + privacy filter
3. Standalone `/chat/` page + embeddable floating widget (vanilla JS/CSS)
4. Auto-refresh: webhook on git push or daily cron

## Tasks

- [ ] Create `src/indexer.py` — parse HTML (BeautifulSoup4), chunk into ~500-token passages
- [ ] Create `src/embedder.py` — generate embeddings (OpenAI text-embedding-3-small), store in FAISS
- [ ] Create `src/retriever.py` — query vector store, return top-k passages with source URLs
- [ ] Create `src/chat.py` — Claude API call with privacy system prompt + retrieved context
- [ ] Create `src/privacy.py` — post-processing filter to block PII leakage
- [ ] Create `src/api.py` — FastAPI: POST /api/chat, rate limiting (20 req/min per IP), CORS for pradeepunair.me
- [ ] Create `frontend/chat-page.html` — standalone /chat/ page (message bubbles, typing indicator)
- [ ] Create `frontend/widget.js` — floating bubble + expandable chat window
- [ ] Create `frontend/widget.css` — widget styling matching site dark/gradient theme
- [ ] Create `scripts/reindex.py` — CLI to re-scrape site and rebuild vector store
- [ ] Create `scripts/deploy_widget.py` — inject widget script tag into all site HTML pages
- [ ] Create `.env.example` and `requirements.txt`
- [ ] Deploy API to Render/Railway free tier
- [ ] Test privacy filter against blocked info list
- [ ] Deploy widget + chat page to cPanel

## Links

- PRD: `Projects/WebsiteChatbot/prd.md`
- Website repo: `git@github.com:pradeepunair/website_files.git`
- Live site: `https://pradeepunair.me`
