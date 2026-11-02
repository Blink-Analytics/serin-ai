---
name: serin-evaluations
description: "Serin MCP evaluations module: how interview scores, integrity and attempts work, plus interview session reports, recording links and job analysis"
---

# Serin MCP: interview evaluations

Part of the Serin MCP skills - start from `../using-serin-mcp/SKILL.md` for authentication, the rules every tool follows and the other modules.

Tools: `get_interview_session`, `get_interview_recording`, `get_job_analysis`.
Evaluations also appear on every application (`list_job_applications`,
`get_application_detail`, `compare_candidates` - see
`../serin-applications/SKILL.md`); this module explains how to read them.

## How evaluations work

**One attempt counts.** A candidate can have several interview attempts
("Serin Interview 1, 2, …"). Exactly one — their **latest** attempt (the one the
application points at, else the most recent by start time) — is the *primary*
attempt, and it alone drives the score, band, integrity tier and displayed
status, exactly as in the Serin dashboard. Earlier attempts are reachable but
**never** counted, blended or averaged. If the latest attempt has no report yet
the evaluation is `pending` — it does *not* fall back to an older attempt's
score: give no score rather than quoting an older one as the candidate's
result.

Every application carries an **`evaluation`** (compact in lists, fuller in
`get_application_detail`):

- `state` — for your own reasoning, **not something to show the recruiter**
  (give them the application status and, when there is one, the score):
  `ready` (scored), `pending` (interview finished, report still being
  generated, usually 10-15 minutes), `in_progress`, `scheduled`,
  `not_enough_data` (interview under 5 minutes or too little data; no score),
  `no_interview`. `note` explains non-ready states.
- `score` — 0-100, the dashboard number. Current reports: 60% objective
  fulfillment (weighted by importance), 25% Core Skills, 15% Soft Skills.
  Older reports: the plain mean of objective fulfillment, behavioral traits and
  communication skills. A component without a score is left out and the rest
  reweighted (see `components` in the detail; the ones that don't apply to a
  report are null). `band`: `high` (≥70), `medium` (≥40), `low`.
- `integrity` — tier `high` / `medium` / `low` (`low` = suspected cheating,
  `medium` = doubtful), or `pending` / `not_enough_data`; in the detail also the
  raised flags and the **AI-assistance signal** (`ai_assist`). Treat the AI
  signal as a weak automated hint that guides a review - never as proof or a
  reason to reject someone on its own.
- `attempt_number` / `of_attempts`, and in the detail `other_attempts` (an index
  of earlier attempts: id, number, date, status — deliberately no scores).

`displayed_status` is the status the dashboard shows (derived from the
interview); `status` is the raw database value. `redo_scheduled` means the
candidate was invited back for another attempt.

## Tools

- **`get_interview_session(session_id, sections=None, transcript_offset=0, transcript_limit=40)`**
  — one attempt's full report. A `session_id` comes from an evaluation's
  `primary_session` or `other_attempts`. The header (score, band, components,
  recommendation, summary, timing) is always returned together with
  `is_primary`; for an earlier attempt, `notes` says which attempt counts and
  its score is for reference only. `sections` picks what else to include
  (default `objectives`, `custom_questions`, `skills`, `integrity`):
  `objectives` (score, label, reasoning, evidence per interview objective),
  `custom_questions`, `skills` (current reports: **Core Skills** — answer
  relevance, depth, reasoning plus job-domain metrics — and **Soft Skills** —
  clarity, listening, handling follow-ups, conduct; older reports: Behavioral
  Traits and Communication Skills; each with sub-scores and feedback. A `null`
  sub-score means the transcript held not enough evidence — say so, never
  treat it as 0; a card with no scored metric is labelled "Not assessed"),
  `integrity` (tier, flags, checks, flagged answers)
  and `transcript` (opt-in — long; page with `transcript_offset` /
  `transcript_limit`, max 200). A section is `null` when not requested and `[]`
  when requested but empty.
- **`get_job_analysis(job_id)`** — the job's analysis overview as on the
  dashboard: `applications_received`, `total_interviews`, `average_score`
  (over primary attempts), `average_duration_minutes`, plus a status `funnel`,
  evaluation-state / score-band / integrity-tier breakdowns and the top
  candidates.
- **`get_interview_recording(session_id)`** — the Serin player page for an
  attempt's recording (`player_url`, with `has_recording` /
  `has_screen_recording`). Give the recruiter that `player_url` exactly as
  returned; there is no direct file link and none should be shared. It is
  `null` when the attempt has no recording. `get_interview_session` carries the
  same `player_url` when the attempt has a recording.

## Flows

**Review applicants for a job:**
1. `list_organization_jobs(search=...)` to find the `job_id`.
2. `get_job_analysis(job_id)` for the overview, then
   `list_job_applications(job_id, sort_by="score")` to see who is strongest.
3. `get_application_detail(application_id)` per applicant of interest for the
   full picture (profile, resume screening, primary evaluation).
4. `get_interview_session(session_id)` when the recruiter wants the reasoning,
   evidence or transcript behind a score.
5. `update_application(application_id, status=..., final_feedback=...)` to
   record a decision.

## Errors

- `"Interview session not found in your organization"` — from
  `get_interview_session`: the `session_id` doesn't exist or belongs to another
  org.
