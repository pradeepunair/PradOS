# ResumePrep Agent — Brief

**Started:** 2026-03-15
**Owner:** Pradeep Nair
**Status:** Active

---

## Problem

Manually reviewing job descriptions, matching them to a resume, and researching a company before applying takes 30–60 minutes per job. This agent automates the full pre-application workflow.

## Goal

Given a job URL or pasted JD, the agent produces:
1. Extracted key skills from the JD
2. Skills matched against Pradeep's resume
3. Skills missing from the resume (with suggestions to address)
4. Job fit % score
5. Company profile doc — background + news from past 2 months

Target: Full output in under 60 seconds per job.

## Constraints

- **Resume source:** `Knowledge/Reference/resume.md` (must be added — see Open Questions)
- **Output format:** Markdown file saved to `Projects/ResumePrep/output/YYYY-MM-DD-[company].md`
- **Scope:** Single-job analysis only (no batch mode in v1)
- **Tools available:** Claude API (claude-opus-4-6 or claude-sonnet-4-6), Python, web fetch

## Approach

1. **Input handler** — accept job URL or raw JD text via CLI arg or stdin
2. **JD scraper** — if URL provided, fetch and extract job content (requests + BeautifulSoup)
3. **Skills extractor** — Claude prompt to pull required skills, level, and role context from JD
4. **Resume matcher** — Claude prompt to compare extracted skills vs resume.md, output matched / missing / fit %
5. **Company researcher** — web search for company name + "news" filtered to last 60 days, summarize with Claude
6. **Report writer** — combine all outputs into a structured markdown file, save to output/

## Stack

| Component | Tool |
|-----------|------|
| Language | Python |
| LLM | Claude API (anthropic SDK) |
| JD fetch | requests + BeautifulSoup4 |
| Company news | web search (Brave Search API or similar) |
| Resume source | Knowledge/Reference/resume.md |
| Output | Markdown → output/YYYY-MM-DD-[company].md |

## Open Questions

- [ ] **Resume not yet in PradOS** — add your resume to `Knowledge/Reference/resume.md` before building the matcher
- [ ] Which news source for company research? (Brave Search API, NewsAPI, or Claude web search tool?)
- [ ] Should the agent also suggest edits to resume bullets, or just flag missing skills?
- [ ] CLI only in v1, or also a simple web UI?

## Links

- Research: research/ folder
- Assets: assets/ folder
- Output: output/ folder
- Related tasks: Tasks/active.md
- Example JD: Affirm — Capital Risk & Reporting PM role
