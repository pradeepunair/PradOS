# ⚙️ PradOS

> A personal operating system built inside Claude Code — making every AI session start with full context, every project leave a trace, and every week compound on the last.

**Owner:** Pradeep Nair · Product Manager · Fintech / Payments / AI Tooling
**Version:** 1.0 · February 2026

---

## What is PradOS?

PradOS is a structured folder workspace that Claude Code reads and writes. It replaces the stateless "start from scratch every session" problem with a durable, compounding system of context. Claude reads `CLAUDE.md` on every session start and immediately knows who Pradeep is, what he's working on, and how to help.

The system is inspired by the [personal OS pattern](https://amankhan1.substack.com/p/how-carl-set-up-his-personal-os-in) — a flat, purpose-driven folder architecture where every file has exactly one job.

---

## Folder Structure

```
PradOS/
├── CLAUDE.md                    ← Claude reads this first, every session
├── GOALS.md                     ← Identity, ownership areas, 90-day goals
├── PRD.md                       ← Full implementation brief
├── infographic.html             ← Visual system map (open in browser)
│
├── Tasks/
│   ├── backlog.md               ← Everything captured, not yet scheduled
│   ├── active.md                ← This week's committed work (max 5 items)
│   └── archive/                 ← Completed tasks with dates
│
├── Projects/
│   ├── README.md                ← Index of all active projects
│   └── _template/               ← Copy this to start a new project
│       ├── brief.md
│       ├── research/
│       └── assets/
│
├── Workflows/
│   ├── README.md                ← Index of all workflows
│   └── _template/               ← Copy this to create a new workflow
│       ├── CLAUDE.md
│       ├── workflow-spec.md
│       ├── step-1.md
│       └── Drafts/
│
├── Meetings/
│   ├── README.md
│   ├── 1on1s/                   ← YYYY-MM-DD-[person].md
│   └── standups/                ← YYYY-MM-DD.md
│
├── Knowledge/
│   ├── README.md
│   ├── Reference/
│   │   └── about-me.md          ← Durable facts Claude should always know
│   ├── Research/                ← Topic deep-dives (never expires)
│   └── People/                  ← One file per stakeholder/collaborator
│
├── Templates/
│   ├── prd.md
│   ├── meeting-notes.md
│   ├── project-brief.md
│   ├── 1on1.md
│   └── weekly-reflection.md
│
├── .claude/
│   ├── launch.json              ← Dev server configs
│   └── skills/                  ← Slash commands available in Claude Code
│       ├── standup.md
│       ├── weekly-update.md
│       ├── new-project.md
│       ├── meeting-prep.md
│       └── reflect.md
│
├── Tools/                       ← Shell scripts and utilities
└── _temp/                       ← Zero-friction dump zone. No rules here.
```

---

## Folder Reference

### `CLAUDE.md`
The entry point Claude Code reads automatically at the start of every session. Contains a folder map, list of available skills, and behavioral rules (date format, how to handle captures, when to suggest Knowledge updates). Kept under 100 lines — pointers only, no full content.

### `GOALS.md`
Single file for identity, ownership areas, and rolling 90-day goals with metrics. Updated quarterly for goals, anytime for ownership changes. This is the file Claude references when grounding recommendations in what Pradeep is actually trying to achieve.

### `Tasks/`
Three-state task lifecycle with no overhead:
- **`backlog.md`** — brain dump. Everything that could be worked on, sorted by rough priority. Reviewed weekly.
- **`active.md`** — this week's commitments only. Max 5 items. Blocked items tracked with the reason.
- **`archive/`** — completed tasks filed with a completion date. Referenced by `/standup` and `/reflect`.

### `Projects/`
One folder per initiative. Each project is a self-contained workspace with:
- **`brief.md`** — what, why, who, timeline. Always filled in first.
- **`research/`** — raw inputs: articles, interview notes, competitive analysis.
- **`assets/`** — outputs: decks, diagrams, exported files.

Start a new project with `/new-project [name]` or by copying `_template/`.

### `Workflows/`
Repeatable multi-step processes that Claude executes with you. A workflow is created when a task repeats 2+ times. Each workflow has its own `CLAUDE.md` so Claude has full context when operating inside it.

Structure: `workflow-spec.md` for the overview → `step-N.md` files for each step → `Drafts/` for outputs in progress.

### `Meetings/`
Notes organised by type:
- **`1on1s/`** — one file per person per meeting. Filename: `YYYY-MM-DD-[person-name].md`
- **`standups/`** — daily standup notes. Filename: `YYYY-MM-DD.md`. Auto-populated by `/standup`.

### `Knowledge/`
Durable reference material that never expires and applies across all projects:
- **`Reference/about-me.md`** — who Pradeep is, communication preferences, technical context, working patterns. Claude reads this for any session involving stakeholders or writing.
- **`Research/`** — deep-dives on industry topics, trends, frameworks. Permanent and reusable (unlike `Projects/research/` which is project-scoped and temporary).
- **`People/`** — one file per stakeholder or collaborator. Contains working style, preferences, history of interactions. Referenced by `/meeting-prep`.

### `Templates/`
Starter files for every document type. Copied (not edited in place) when creating new documents:

| Template | Used for |
|----------|----------|
| `prd.md` | Product requirements documents |
| `project-brief.md` | New project kick-offs |
| `meeting-notes.md` | Ad-hoc and recurring meetings |
| `1on1.md` | Recurring 1-on-1 sessions |
| `weekly-reflection.md` | End-of-week reviews |

### `.claude/skills/`
Slash commands available inside this Claude Code project:

| Skill | What it does |
|-------|-------------|
| `/standup` | Generates today's standup from Tasks/ and Meetings/standups/ |
| `/weekly-update` | Drafts a stakeholder update email from the week's work |
| `/new-project [name]` | Scaffolds Projects/[name]/ with brief.md, research/, assets/ |
| `/meeting-prep [topic]` | Pulls context from Knowledge/People/ and prior meeting notes |
| `/reflect` | Runs a weekly or monthly reflection prompt, saves output |

### `Tools/`
Shell scripts and utilities that support PradOS operations. Simple tools are single `.sh` or `.py` files. Complex tools get their own folder with `run.py`, `README.md`, and `config.json`.

### `_temp/`
Zero-friction capture zone. No organisation required. When Pradeep says "capture this", Claude writes here with a `YYYY-MM-DD` timestamp. Files older than 30 days are reviewed and either promoted to the right folder or deleted.

---

## Core Principles

1. **Pointers over content** — `CLAUDE.md` links to files, never duplicates them. Depth lives at the leaves.
2. **Capture before organising** — `_temp/` exists because friction kills capture. Organise later.
3. **Every task has a lifecycle** — backlog → active → archive. Nothing lives in limbo.
4. **Workflows multiply leverage** — a process written once runs with Claude indefinitely.
5. **Intelligence compounds through writing** — every note, brief, and reflection makes the next session sharper.

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/pradeepunair/PradOS.git

# Open in Claude Code
claude /path/to/PradOS
```

Claude will read `CLAUDE.md` automatically. First actions:
1. Fill in `GOALS.md` — identity and current 90-day goals
2. Fill in `Knowledge/Reference/about-me.md` — communication preferences and context
3. Add items to `Tasks/backlog.md`
4. Run `/new-project` for anything active

---

## Visual Map

Open `infographic.html` in any browser for a full visual overview of the system — folder architecture, task lifecycle, Claude interaction flows, skills reference, and information flow diagram.

---

*Built with [Claude Code](https://claude.ai/claude-code) · February 2026*
