#!/usr/bin/env python3
"""
token_parser.py — Claude Code session log parser for PradOS.

Reads all JSONL session files from ~/.claude/projects/[prados-dir]/,
attributes each session to a project by scanning tool call file paths,
and writes aggregated token + time stats to data/stats.json.

Usage:
    python3 token_parser.py
"""

import json
import glob
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ── Paths ─────────────────────────────────────────────────────────────────────

SESSIONS_DIR = Path.home() / ".claude/projects/-Users-pradeepnair-Desktop-GEN-AI-PradOS"
PRADOS_ROOT  = Path("/Users/pradeepnair/Desktop/GEN AI/PradOS")
PROJECTS_DIR = PRADOS_ROOT / "Projects"
OUTPUT_FILE  = Path(__file__).parent / "data/stats.json"

# ── Pricing (USD per million tokens) ──────────────────────────────────────────

MODEL_PRICING = {
    "claude-opus":    {"input": 15.00, "output": 75.00, "cache_read": 1.50,  "cache_create": 18.75},
    "claude-sonnet":  {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_create": 3.75},
    "claude-haiku":   {"input": 0.80,  "output": 4.00,  "cache_read": 0.08,  "cache_create": 1.00},
}
DEFAULT_PRICING = MODEL_PRICING["claude-sonnet"]


def get_pricing(model: str) -> dict:
    model_lower = (model or "").lower()
    for key, pricing in MODEL_PRICING.items():
        if key in model_lower:
            return pricing
    return DEFAULT_PRICING


def compute_cost(usage: dict, model: str) -> float:
    p = get_pricing(model)
    M = 1_000_000
    return (
        usage.get("input_tokens", 0)                 * p["input"]        / M +
        usage.get("output_tokens", 0)                * p["output"]       / M +
        usage.get("cache_read_input_tokens", 0)      * p["cache_read"]   / M +
        usage.get("cache_creation_input_tokens", 0)  * p["cache_create"] / M
    )


# ── Project name discovery ─────────────────────────────────────────────────────

EXCLUDE_PROJECTS = {"_template"}

def get_project_names() -> list[str]:
    """Return all project folder names under Projects/ (excluding templates)."""
    if not PROJECTS_DIR.exists():
        return []
    return [p.name for p in PROJECTS_DIR.iterdir()
            if p.is_dir() and p.name not in EXCLUDE_PROJECTS]


def extract_project_hits(line_obj: dict, project_names: list[str]) -> list[str]:
    """
    Scan a tool_use block for file paths referencing Projects/[name].
    Returns list of project names hit (may have duplicates for weighting).
    """
    hits = []
    content = line_obj.get("message", {}).get("content", [])
    for block in content:
        if block.get("type") != "tool_use":
            continue
        inp = block.get("input", {})
        # Combine all string values in the input to search for project paths
        text = " ".join(str(v) for v in inp.values() if isinstance(v, str))
        for name in project_names:
            pattern = rf"Projects[/\\]{re.escape(name)}[/\\]"
            count = len(re.findall(pattern, text))
            hits.extend([name] * count)
    return hits


# ── Session parser ────────────────────────────────────────────────────────────

def parse_session(jsonl_path: Path, project_names: list[str]) -> dict:
    """
    Parse a single session JSONL file.
    Returns dict with token totals, cost, duration, project attribution.
    """
    usage_totals = defaultdict(int)
    project_hit_counts = defaultdict(int)
    timestamps = []
    models_seen = defaultdict(int)

    with open(jsonl_path, encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            ts = obj.get("timestamp")
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                except ValueError:
                    pass

            if obj.get("type") == "assistant":
                usage = obj.get("message", {}).get("usage", {})
                if usage:
                    model = obj.get("message", {}).get("model", "") or obj.get("model", "")
                    models_seen[model] += 1
                    usage_totals["input_tokens"]                += usage.get("input_tokens", 0)
                    usage_totals["output_tokens"]               += usage.get("output_tokens", 0)
                    usage_totals["cache_read_input_tokens"]     += usage.get("cache_read_input_tokens", 0)
                    usage_totals["cache_creation_input_tokens"] += usage.get("cache_creation_input_tokens", 0)

                # Scan tool calls for project attribution
                for name in extract_project_hits(obj, project_names):
                    project_hit_counts[name] += 1

    # Dominant model
    dominant_model = max(models_seen, key=models_seen.get) if models_seen else ""

    # Total tokens (all types)
    total_tokens = sum(usage_totals.values())

    # Cost
    cost = compute_cost(dict(usage_totals), dominant_model)

    # Duration — capped at 4h per session (avoids inflating from idle/paused gaps)
    MAX_SESSION_HOURS = 4.0
    hours = 0.0
    if len(timestamps) >= 2:
        timestamps.sort()
        delta = (timestamps[-1] - timestamps[0]).total_seconds()
        hours = min(max(delta / 3600, 1 / 60), MAX_SESSION_HOURS)

    # Project attribution: most-hit project wins; fallback to "PradOS"
    attributed_project = "PradOS"
    if project_hit_counts:
        attributed_project = max(project_hit_counts, key=project_hit_counts.get)

    return {
        "attributed_project": attributed_project,
        "input_tokens":       usage_totals["input_tokens"],
        "output_tokens":      usage_totals["output_tokens"],
        "cache_read":         usage_totals["cache_read_input_tokens"],
        "cache_create":       usage_totals["cache_creation_input_tokens"],
        "total_tokens":       total_tokens,
        "cost_usd":           cost,
        "hours":              hours,
        "dominant_model":     dominant_model,
        "first_ts":           timestamps[0].isoformat() if timestamps else None,
        "last_ts":            timestamps[-1].isoformat() if timestamps else None,
    }


# ── Aggregator ────────────────────────────────────────────────────────────────

def aggregate_all_sessions() -> dict:
    """Parse all JSONL files and return per-project aggregated stats."""
    project_names = get_project_names()
    jsonl_files = sorted(SESSIONS_DIR.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No JSONL files found in {SESSIONS_DIR}")
        return {}

    print(f"Found {len(jsonl_files)} session files | {len(project_names)} projects")

    per_project: dict[str, dict] = defaultdict(lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read": 0,
        "cache_create": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "hours": 0.0,
        "sessions": 0,
        "last_active": None,
    })

    for jsonl_path in jsonl_files:
        try:
            session = parse_session(jsonl_path, project_names)
        except Exception as e:
            print(f"  Error parsing {jsonl_path.name}: {e}")
            continue

        proj = session["attributed_project"]
        agg  = per_project[proj]

        agg["input_tokens"]  += session["input_tokens"]
        agg["output_tokens"] += session["output_tokens"]
        agg["cache_read"]    += session["cache_read"]
        agg["cache_create"]  += session["cache_create"]
        agg["total_tokens"]  += session["total_tokens"]
        agg["cost_usd"]      += session["cost_usd"]
        agg["hours"]         += session["hours"]
        agg["sessions"]      += 1

        last_ts = session.get("last_ts")
        if last_ts and (agg["last_active"] is None or last_ts > agg["last_active"]):
            agg["last_active"] = last_ts

        print(f"  {jsonl_path.name[:8]}… → {proj:20s} | "
              f"{session['total_tokens']:>8,} tokens | "
              f"{session['hours']:.1f}h | "
              f"${session['cost_usd']:.3f}")

    # Round floats for readability
    result = {}
    for proj, agg in sorted(per_project.items()):
        result[proj] = {
            "input_tokens":  agg["input_tokens"],
            "output_tokens": agg["output_tokens"],
            "cache_read":    agg["cache_read"],
            "cache_create":  agg["cache_create"],
            "total_tokens":  agg["total_tokens"],
            "cost_usd":      round(agg["cost_usd"], 4),
            "hours":         round(agg["hours"], 2),
            "sessions":      agg["sessions"],
            "last_active":   agg["last_active"],
        }

    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PradOS Token & Time Parser")
    print("=" * 60)

    stats = aggregate_all_sessions()

    if not stats:
        print("No data to write.")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "projects": stats,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 60)
    print("Summary by project:")
    print(f"{'Project':<22} {'Tokens':>12} {'Cost':>8} {'Hours':>7} {'Sessions':>9}")
    print("-" * 60)

    grand_tokens = grand_cost = grand_hours = grand_sessions = 0
    for proj, s in sorted(stats.items(), key=lambda x: x[1]["total_tokens"], reverse=True):
        grand_tokens   += s["total_tokens"]
        grand_cost     += s["cost_usd"]
        grand_hours    += s["hours"]
        grand_sessions += s["sessions"]
        print(f"{proj:<22} {s['total_tokens']:>12,} {s['cost_usd']:>7.3f} {s['hours']:>7.1f} {s['sessions']:>9}")

    print("-" * 60)
    print(f"{'TOTAL':<22} {grand_tokens:>12,} {grand_cost:>7.3f} {grand_hours:>7.1f} {grand_sessions:>9}")
    print()
    print(f"Stats written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
