"""
board_reader.py — Reads Projects/*/brief.md and returns structured project card data.

Each brief.md must have:
  **Status:** Discovery | Active | Complete | Paused

Task items are parsed from ALL checkbox lines in the file:
  - [ ] pending task
  - [x] completed task
"""

import json
import re
from pathlib import Path
from typing import Optional

PROJECTS_ROOT = Path(__file__).parent.parent.parent.parent  # PradOS root
PROJECTS_DIR  = PROJECTS_ROOT / "Projects"
TOKEN_STATS_FILE = PROJECTS_ROOT / "Projects/TokenTimeTracker/src/data/stats.json"


def _load_token_stats() -> dict:
    """Load per-project token/time stats from TokenTimeTracker output. Returns {} if unavailable."""
    if not TOKEN_STATS_FILE.exists():
        return {}
    try:
        with open(TOKEN_STATS_FILE) as f:
            data = json.load(f)
        return data.get("projects", {})
    except (json.JSONDecodeError, OSError):
        return {}

STATUS_TO_LANE = {
    "discovery": "backlog",
    "paused":    "backlog",
    "active":    "in_progress",
    "complete":  "completed",
}


def get_all_projects() -> list[dict]:
    """
    Scan Projects/*/brief.md and return list of project card dicts.
    Excludes _template/. Attaches token/time stats from TokenTimeTracker.
    """
    token_stats = _load_token_stats()
    projects = []
    for brief_path in sorted(PROJECTS_DIR.glob("*/brief.md")):
        if brief_path.parent.name.startswith("_"):
            continue
        project = _parse_brief(brief_path)
        if project:
            stats = token_stats.get(project["name"], {})
            project["tokens"]   = stats.get("total_tokens", 0)
            project["cost_usd"] = stats.get("cost_usd", 0.0)
            project["hours"]    = stats.get("hours", 0.0)
            project["sessions"] = stats.get("sessions", 0)
            projects.append(project)
    return projects


def get_projects_by_lane() -> dict[str, list[dict]]:
    """Return projects grouped by lane: backlog / in_progress / completed."""
    lanes = {"backlog": [], "in_progress": [], "completed": []}
    for project in get_all_projects():
        lane = project["lane"]
        if lane in lanes:
            lanes[lane].append(project)
    return lanes


def update_project_status(name: str, new_status: str) -> bool:
    """
    Update the Status: field in a project's brief.md.
    new_status must be one of: Discovery, Active, Complete, Paused
    Returns True on success, False if project not found.
    """
    brief_path = PROJECTS_DIR / name / "brief.md"
    if not brief_path.exists():
        return False

    content = brief_path.read_text()
    updated = re.sub(
        r"(\*\*Status:\*\*\s*)[\w\s|]+",
        rf"\g<1>{new_status}",
        content,
        count=1
    )
    brief_path.write_text(updated)
    return True


def toggle_task(project_name: str, task_index: int) -> bool:
    """
    Toggle a checkbox item in a project's brief.md by its 0-based index
    among all checkbox lines in the file.
    Returns True on success.
    """
    brief_path = PROJECTS_DIR / project_name / "brief.md"
    if not brief_path.exists():
        return False

    lines = brief_path.read_text().splitlines(keepends=True)
    checkbox_count = 0

    for i, line in enumerate(lines):
        if re.match(r"\s*- \[[ x]\]", line):
            if checkbox_count == task_index:
                if "- [ ]" in line:
                    lines[i] = line.replace("- [ ]", "- [x]", 1)
                else:
                    lines[i] = line.replace("- [x]", "- [ ]", 1)
                brief_path.write_text("".join(lines))
                return True
            checkbox_count += 1

    return False


# ---------------------------------------------------------------------------
# Internal parser
# ---------------------------------------------------------------------------

def _parse_brief(path: Path) -> Optional[dict]:
    content = path.read_text()
    name = path.parent.name

    # Title from H1
    title_match = re.search(r"^#\s+(.+?)(?:\s+—\s+.+)?$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else name

    # Status
    status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", content)
    status = status_match.group(1).strip() if status_match else "Discovery"
    lane = STATUS_TO_LANE.get(status.lower(), "backlog")

    # Started date
    started_match = re.search(r"\*\*Started:\*\*\s*([\d-]+)", content)
    started = started_match.group(1) if started_match else ""

    # One-liner: first non-empty line under ## Problem
    problem_match = re.search(r"## Problem\s*\n+(.+?)(?:\n\n|\n##)", content, re.DOTALL)
    description = ""
    if problem_match:
        description = problem_match.group(1).strip().split("\n")[0][:120]

    # Tasks: all checkbox lines in the file
    tasks = []
    for i, line in enumerate(content.splitlines()):
        m = re.match(r"\s*- \[([ x])\]\s+(.+)", line)
        if m:
            tasks.append({
                "index": len(tasks),
                "done": m.group(1) == "x",
                "text": m.group(2).strip(),
            })

    return {
        "name": name,
        "title": title,
        "status": status,
        "lane": lane,
        "started": started,
        "description": description,
        "tasks": tasks,
        "task_counts": {
            "total": len(tasks),
            "done": sum(1 for t in tasks if t["done"]),
        },
    }
