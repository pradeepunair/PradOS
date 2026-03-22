---
name: reflect
description: Run a weekly or monthly reflection prompt and save the output
---

Ask: "Weekly or monthly reflection?"

**For weekly:** use Templates/weekly-reflection.md as the structure. Pre-fill:
- Today's date as the week identifier
- Any tasks completed this week from Tasks/archive/
- Active goal status from GOALS.md

**For monthly:** prompt with these questions one at a time:
1. What are you most proud of this month?
2. What surprised you (positively or negatively)?
3. What did you learn that changed how you think about something?
4. Are your 90-day goals still the right goals? What would you change?
5. What do you want to do differently next month?

After gathering responses, compile into a reflection document.

Save to: `_temp/YYYY-MM-DD-reflection.md` (or ask if they want it somewhere else).

Close with: "I'll also update the status column in GOALS.md if you tell me how each goal is tracking."
