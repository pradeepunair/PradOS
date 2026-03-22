"""
app.py — Flask server for PradOS Kanban Board

Routes:
  GET  /                              → render board UI
  GET  /api/projects                  → all projects grouped by lane (JSON)
  PATCH /api/projects/<name>/status   → update project status
  PATCH /api/projects/<name>/tasks/<int:idx> → toggle task checkbox
"""

from flask import Flask, render_template, jsonify, request, abort
from board_reader import get_projects_by_lane, update_project_status, toggle_task

app = Flask(__name__)

VALID_STATUSES = {"Discovery", "Active", "Complete", "Paused"}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/projects")
def api_projects():
    return jsonify(get_projects_by_lane())


@app.patch("/api/projects/<name>/status")
def api_update_status(name: str):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "")

    if new_status not in VALID_STATUSES:
        abort(400, f"Invalid status '{new_status}'. Must be one of: {VALID_STATUSES}")

    success = update_project_status(name, new_status)
    if not success:
        abort(404, f"Project '{name}' not found")

    return jsonify({"ok": True, "project": name, "status": new_status})


@app.patch("/api/projects/<name>/tasks/<int:idx>")
def api_toggle_task(name: str, idx: int):
    success = toggle_task(name, idx)
    if not success:
        abort(404, f"Task {idx} not found in project '{name}'")
    return jsonify({"ok": True, "project": name, "task_index": idx})


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    print("\n  PradOS Kanban Board → http://localhost:8080\n")
    app.run(debug=True, port=8080)
