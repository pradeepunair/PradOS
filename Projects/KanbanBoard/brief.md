# KanbanBoard — Brief

**Started:** 2026-03-15
**Owner:** Pradeep Nair
**Status:** Complete

---

## Problem

PradOS projects are tracked across multiple markdown files with no visual overview. Hard to see what's in flight vs backlog at a glance.

## Goal

A local interactive Kanban board at `localhost:5000` that reads all `Projects/*/brief.md` files and renders them as draggable cards across Backlog / In Progress / Completed swimlanes. Drag-and-drop updates the source markdown files.

## Constraints

- Timeline: Flexible
- Resources: Python Flask, SortableJS (CDN), no database — markdown is source of truth
- Scope: Local only (no deployment). Read + write to Projects/ folder only.

## Stakeholders

| Name | Role | Involvement |
|------|------|------------|
| Pradeep Nair | Owner | Builder + sole user |

## Approach

1. `board_reader.py` — scan `Projects/*/brief.md`, parse Status field into card dicts
2. `app.py` — Flask server: `GET /` renders board, `GET /api/projects` returns JSON, `PATCH /api/projects/<name>` updates status
3. `index.html` — Kanban UI with SortableJS drag-and-drop
4. `style.css` — card and lane styling

## Decisions

- **Paused projects** → move back to Backlog lane (Status: Paused maps to Backlog)
- **Board shows projects only** — Active cards expand to show their task checklist with individual statuses
- **Status → Lane mapping:** Discovery/Paused → Backlog | Active → In Progress | Complete → Completed

## Links

- PRD: Tasks/backlog.md → KanbanBoard section
- Data source: Projects/*/brief.md (Status field)
- Launch: `python src/app.py`
