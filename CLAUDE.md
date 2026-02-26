# PradOS — Claude Entry Point

You are working inside PradOS, the personal operating system of Pradeep Nair.
Read this file first. Every session.

## Who is Pradeep

Product Manager. Domain expertise: fintech, payments, AI tooling.
Full profile: Knowledge/Reference/about-me.md
Current goals: GOALS.md

## Folder Map

| Folder | Purpose |
|--------|---------|
| Tasks/ | backlog → active → archive lifecycle |
| Projects/ | One folder per initiative. Start with brief.md |
| Workflows/ | Repeatable processes. Each has its own CLAUDE.md |
| Meetings/ | Notes by type: 1on1s/, standups/ |
| Knowledge/ | Reference/, Research/, People/ |
| Templates/ | Starter files for new documents |
| .claude/skills/ | Slash commands available in this project |
| Tools/ | Shell scripts and utilities |
| _temp/ | Dump area. No organization required |

## Available Skills

- /standup — generate today's standup from recent work
- /weekly-update — draft stakeholder communication
- /new-project [name] — scaffold a new project folder
- /meeting-prep [person or topic] — pull context for a meeting
- /reflect — weekly or monthly reflection prompt

## Behavioral Rules

- When Pradeep says "capture this", write it to _temp/ with a YYYY-MM-DD timestamp filename.
- When starting a new project, always create Projects/[project-name]/brief.md first.
- When a task is completed, move it from active.md to archive/ with a completion date.
- When you learn something about Pradeep's preferences, suggest adding it to Knowledge/Reference/about-me.md.
- Default date format: YYYY-MM-DD.
- Prefer markdown tables over bullet lists when comparing options.
- Keep this file under 100 lines. Move growing content to the appropriate folder.
