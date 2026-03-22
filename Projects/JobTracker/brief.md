# Job Application Tracker

**Status:** Discovery
**Started:** 2026-03-22

## Problem
No centralized view of jobs applied to, their current status, or recruiter reply tracking.

## Context
Pradeep is actively job hunting (Director / Senior PM roles in fintech/AI). Applications are tracked
manually with no automated status updates. Gmail contains recruiter replies, rejections, and next-step
emails that could be parsed to auto-update application status.

## Proposed Approach
- Build a dashboard (Flask or simple HTML) to log job applications (company, role, date, link, status)
- Integrate with Gmail MCP / Gmail API to scan inbox for reply threads per company
- Auto-classify email replies: No response / Recruiter screen / Interview / Offer / Rejection
- Surface status on a clean table with filters (by status, date, company)
- Optionally connect to ResumePrep project for JD matching scores

## Tasks
- [ ] Define data schema: (company, role, JD_url, date_applied, status, last_email_date, notes)
- [ ] Build Flask app with CRUD for job applications (add/edit/delete)
- [ ] Add CSV export for backup
- [ ] Integrate Gmail API to search threads by company name
- [ ] Build email classifier to map reply content → status (screen/interview/rejection/offer)
- [ ] Auto-update application status from Gmail scan
- [ ] Create dashboard UI: table view with status badges + timeline
- [ ] Add filter/sort by status, company, date range
- [ ] Connect to ResumePrep: show JD match score per application
