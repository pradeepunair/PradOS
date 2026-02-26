# PradOS — Product Requirements Document
## Implementation Brief for Claude Code

**Owner:** Pradeep Nair
**Version:** 1.0
**Last Updated:** 2026-02-25

---

## 1. Context: Why This System Exists

Pradeep is a product manager working across multiple domains: fintech, AI tooling, and personal projects. Conversations with Claude are currently stateless — every session starts cold. PradOS fixes this by making context durable, structured, and compounding. Instead of re-explaining who Pradeep is and what he's working on every session, CLAUDE.md acts as a permanent entry point that orients Claude instantly. Over time, every project, meeting note, and decision captured here makes the next interaction sharper.

This is a personal operating system, not a productivity app. It has no backend. It runs entirely as a folder structure that Claude Code reads, writes, and navigates.

---

## 2. Philosophy: Five Core Principles

**1. Pointers over content.**
CLAUDE.md does not contain everything. It contains pointers to where everything lives. Files stay lean. Depth lives in the leaves (Projects/, Knowledge/), not the root.

**2. Capture before organizing.**
`_temp/` exists so friction never stops capture. Dump first, organize later. Entropy is acceptable in `_temp/`. It is not acceptable anywhere else.

**3. Every task has a lifecycle.**
Ideas start in `Tasks/backlog.md`. When acted on, they move to `Tasks/active.md`. When done, they go to `Tasks/archive/`. Nothing stays in active indefinitely.

**4. Workflows multiply leverage.**
A workflow written once can be executed dozens of times with Claude. The Workflows/ directory is the factory. Each workflow has its own CLAUDE.md so Claude understands context when invoked inside it.

**5. Intelligence compounds through writing.**
A meeting note written today becomes Knowledge/ six months from now. A project brief written at kickoff becomes a reference during retrospective. The system only works if output is captured. Claude should always be looking for opportunities to write things down.

---

## 3. Complete Directory Structure

```
PradOS/
├── CLAUDE.md                          ← Entry point (<100 lines)
├── GOALS.md                           ← Identity, ownership, 90-day goals
├── PRD.md                             ← This document
├── infographic.html                   ← Visual system map
├── Tasks/
│   ├── backlog.md
│   ├── active.md
│   └── archive/
├── Projects/
│   ├── README.md
│   └── _template/
│       ├── brief.md
│       ├── research/
│       └── assets/
├── Workflows/
│   ├── README.md
│   └── _template/
│       ├── CLAUDE.md
│       ├── workflow-spec.md
│       ├── step-1.md
│       └── Drafts/
├── Meetings/
│   ├── README.md
│   ├── 1on1s/
│   └── standups/
├── Knowledge/
│   ├── README.md
│   ├── Reference/
│   │   └── about-me.md
│   ├── Research/
│   └── People/
├── Templates/
│   ├── prd.md
│   ├── meeting-notes.md
│   ├── project-brief.md
│   ├── 1on1.md
│   └── weekly-reflection.md
├── .claude/
│   ├── settings.local.json
│   ├── launch.json                    ← Dev server configurations
│   └── skills/
│       ├── standup.md
│       ├── weekly-update.md
│       ├── new-project.md
│       ├── meeting-prep.md
│       └── reflect.md
├── Tools/
│   └── README.md
└── _temp/
    └── README.md
```

---

## 4. Available Skills (Slash Commands)

| Skill | Purpose |
|-------|---------|
| `/standup` | Generate today's standup from Tasks/ and Meetings/ |
| `/weekly-update` | Draft stakeholder communication |
| `/new-project [name]` | Scaffold Projects/[name]/ with brief.md |
| `/meeting-prep [topic]` | Pull context from Knowledge/ and prior notes |
| `/reflect` | Weekly or monthly reflection prompt |

---

## 5. Behavioral Guidelines for Claude

- When Pradeep says "capture this" → write to `_temp/YYYY-MM-DD-[topic].md`
- When starting a project → always create `Projects/[name]/brief.md` first
- When a task is completed → move from `active.md` to `archive/YYYY-MM-DD-completions.md`
- When discovering a preference → suggest adding to `Knowledge/Reference/about-me.md`
- Default date format: `YYYY-MM-DD`
- Keep `CLAUDE.md` under 100 lines at all times

---

## 6. Post-Setup First Actions for Pradeep

1. Open `GOALS.md` and fill in the identity section and at least two current goals
2. Open `Knowledge/Reference/about-me.md` and fill in professional background
3. Add 3-5 items to `Tasks/backlog.md` from whatever is currently on your mind
4. If there's an active project, run `/new-project` to scaffold it
5. Test `/standup` — it will return sparse output at first, which is expected

The system gets smarter as it gets populated. First week: setup. Second week: habit formation.

---

## 7. GitHub Repository

**Remote:** https://github.com/pradeepunair/PradOS.git

To sync after making changes:
```bash
git add -A
git commit -m "Update PradOS"
git push origin main
```
