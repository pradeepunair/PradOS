# Token & Time Tracker

**Status:** Discovery
**Started:** 2026-03-22

## Problem
Track Claude API token usage and time spent building each project on the Kanban board.

## Context
Each project on the board involves Claude-assisted work sessions. Currently there is no visibility into
how many tokens were consumed per project or how many hours were invested. This tracker will surface
that data alongside the existing Kanban cards.

## Proposed Approach
- Parse Claude Code session logs or hook into Claude API usage endpoint
- Log (project, timestamp, tokens_used, session_duration) per work session
- Expose a lightweight API or embed stats into the Kanban card UI
- Show per-card: total tokens used, total time spent, last active date

## Tasks
- [ ] Research Claude Code session log format and token usage APIs
- [ ] Design data schema: project → sessions → (tokens, duration, date)
- [ ] Build session logger (Python script or Claude hook)
- [ ] Create API endpoint to aggregate stats per project
- [ ] Extend KanbanBoard card UI to show token count + time spent
- [ ] Add weekly rollup view (total tokens across all projects)
