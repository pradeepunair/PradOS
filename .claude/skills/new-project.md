---
name: new-project
description: Scaffold a new project folder with brief.md and standard structure
---

Ask for the project name if not provided as an argument.

Create the following structure at Projects/[project-name]/:
- brief.md (copy from Templates/project-brief.md, replace [Project Name] with the actual name and YYYY-MM-DD with today's date)
- research/ (empty folder — create a .gitkeep placeholder)
- assets/ (empty folder — create a .gitkeep placeholder)

Then open brief.md and ask Pradeep to fill in:
1. The problem statement (one or two sentences)
2. The goal and what success looks like
3. Any known constraints or stakeholders

Once filled, add the project to the table in Projects/README.md with today's date and status "Active".

Finally, ask: "Should I create a task for this project in Tasks/active.md?"
