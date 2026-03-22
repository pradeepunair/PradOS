---
name: goodmorning
description: Run the morning DailyBrief pipeline — fetch news, summarize with Claude, fetch X posts, build digest, save markdown, send email
---

Run the DailyBrief pipeline. Use the Bash tool to execute:

    cd "/Users/pradeepnair/Desktop/GEN AI/PradOS/Projects/DailyBrief/src" && /usr/local/bin/python3.11 main.py

Stream all output so each step is visible as it runs.

The pipeline runs 5 steps:
1. Fetch top 3 articles for Payments/BNPL and AI/LLMs (Brave API, Claude fallback)
2. Summarize each article with Claude (2-3 sentences, fintech PM audience)
3. Fetch top 5 trending X posts on payments + AI (graceful fallback if unavailable)
4. Build markdown + HTML digest
5. Save digest to output/YYYY-MM-DD-digest.md, then send via Gmail SMTP

After the command completes:
- Read `Projects/DailyBrief/output/YYYY-MM-DD-digest.md` (use today's date) and display its full content inline
- Report status summary: digest saved ✓/✗ | email delivered ✓/✗ | X posts ✓/✗
- If email failed: show the error and note the digest is still saved to output/
