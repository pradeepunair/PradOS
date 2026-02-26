---
name: standup
description: Generate a daily standup update from recent work in Tasks/ and Meetings/
---

Read Tasks/active.md and scan the most recent entries in Meetings/standups/ and Tasks/archive/.

Generate a standup in this format:

**Yesterday:**
[What was worked on, based on task status and recent standup notes]

**Today:**
[What is planned, based on active tasks]

**Blockers:**
[Any blocked tasks from Tasks/active.md. If none, say "None."]

Keep each section to 2-3 bullet points max. Be specific. Avoid vague language like "worked on stuff".

After generating, ask: "Should I save this to Meetings/standups/YYYY-MM-DD.md?"
