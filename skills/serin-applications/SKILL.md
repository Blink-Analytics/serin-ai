---
name: serin-applications
description: "Serin MCP applications module: listing, reading, comparing and updating a job's applications, and changing many at once (status, labels, deadlines)"
---

# Serin MCP: applications

Part of the Serin MCP skills - start from `../using-serin-mcp/SKILL.md` for authentication, the rules every tool follows and the other modules.

Tools: `list_job_applications`, `get_application_detail`, `compare_candidates`,
`update_application`, `bulk_update_application_status`,
`bulk_update_application_labels`, `bulk_update_application_deadline`.

Every application carries an `evaluation` (score, band, integrity, attempts);
read `../serin-evaluations/SKILL.md` before quoting or comparing scores -
only the candidate's latest attempt counts. To email or invite candidates use
`../serin-candidate-outreach/SKILL.md`.

## What to tell the recruiter about an application

Report the **application status** (`displayed_status`, e.g. "Interview
completed", "Under review") - that is what recruiters track. **Do not report the
interview `state`** (`ready`, `pending`, `in_progress`, `scheduled`,
`not_enough_data`, `no_interview`) or its `note`: it is bookkeeping for you, not
information the recruiter wants, and "no interview" / "ready" / "pending" labels
only add noise. Use it silently to decide what you can quote: when the state is
`ready`, give the score and band; when it isn't, simply give no score (never
borrow an earlier attempt's). Don't announce "evaluation not ready" or list
candidates by interview state.

## Tools

- **`list_job_applications(job_id, status=None, label_ids=None, applied_after=None, applied_before=None, search=None, sort_by=None, sort_direction="desc", limit=50, offset=0)`**
  — applicants for one of the caller's org's jobs: candidate name/email, status
  and displayed status, labels, notes, resume score, source, and the compact
  `evaluation` — so you can rank candidates without opening each application.
  - `status`: list of raw pipeline values (see below) — matches any.
  - `label_ids`: label slugs from `get_organization_details` — any overlap.
  - `applied_after` / `applied_before`: ISO timestamps bounding `applied_at`.
  - `search`: candidate name or email. Every word of a name must match; an
    email address is matched on its own (any punctuation around it is ignored),
    so pass just the address to find one person.
  - `sort_by`: `applied_at`, `status`, `application_deadline_at`,
    `resume_score`, or computed `score`, `integrity`, `interview_date`, `name`
    (default newest first). Candidates without a value sort last.
  - Paging: `limit` (max 100) / `offset`; `total` and `has_more` in the result.
  - Not supported: the website's "hide internal applications" filter.
- **`get_application_detail(application_id)`** — one application: candidate
  profile (name, email, phone), application fields (status, notes, feedback,
  deadline, labels, resume URL), resume screening score and reasoning,
  pre-screening answers, and the full primary-attempt `evaluation`: score,
  components, recommendation, overall rating, summary, integrity (flags,
  AI-assistance signal) and per-objective scores. Use `get_interview_session`
  for the evidence behind them.
- **`compare_candidates(application_ids)`** — 2 to 6 candidates for the **same
  job**, side by side, each on their primary attempt. `objectives` is the union
  of assessed objectives and each candidate's `objective_scores` lines up with
  it (null = not assessed). A candidate whose latest attempt is still pending
  shows no score — don't compare them on an older attempt.
- **`update_application(application_id, status=None, application_notes=None, final_feedback=None, application_deadline_at=None, label_ids=None)`**
  — partial update. `status` must be one of the pipeline's exact values
  (`prospect`, `applied`, `invited`, `task_assigned`, `task_submitted`,
  `interview_scheduled`, `interview_inprogress`, `interview_completed`,
  `under_review`, `accepted`, `rejected`, `withdrawn`), follows the dashboard's
  rules (milestone time + decider recorded; no going back to `applied` /
  `invited` after a completed interview; `withdrawn` is locked). **It does not
  email or notify the candidate** — use `send_application_email` for that.
  `application_notes` max 4000 chars (`""` clears); `application_deadline_at` is
  a per-candidate ISO deadline, in the future and not later than the job's own
  (it can be moved, not cleared); `label_ids` replaces the labels (slugs from
  `get_organization_details`, max 10, `[]` clears).

- **`bulk_update_application_status(job_id, application_ids, status, confirm=False)`**
  / **`bulk_update_application_labels(job_id, application_ids, mode, label_ids=None, confirm=False)`**
  / **`bulk_update_application_deadline(job_id, application_ids, application_deadline_at=None, confirm=False)`**
  — change several of one job's applications at once (max 500). **Two steps:**
  without `confirm` nothing changes and you get who would be updated and who
  would be skipped, each with a reason (`already_accepted`, `withdrawn`,
  `interview_already_completed`, `unchanged`, `invite_failed`, `not_found`);
  show it and only call again with `confirm=true` after an explicit yes.
  `status` is one of `accepted`, `rejected`, `under_review` or — to undo a
  mistake before the interview — `applied`/`invited`. Candidates get an in-app
  notification of a status change; **no email** — use `send_application_email`.
  Labels: `mode` is `add`, `remove` or `set` with organization label slugs (max
  10 per application; ones that would go over are counted in
  `skipped_over_label_limit`). Deadline: ISO 8601 UTC ending in `Z`, future, not
  later than the job's; omit it to clear. Repeating a call is safe (already
  changed applications are skipped).

## Flows

**Act on a shortlist at once:**
1. `list_job_applications(job_id, sort_by="score", limit=...)` to pick the
   applicants.
2. `bulk_update_application_status(job_id, application_ids, status=...)` (or the
   labels / deadline variants) — read back who would change and who is skipped,
   then (after a yes) `confirm=true`.

**Compare finalists:**
1. `list_job_applications(job_id, sort_by="score", limit=10)` to shortlist.
2. `compare_candidates([application_id_1, application_id_2, ...])`.

## Errors

- `"Application not found in your organization"` - the `application_id` exists
  but belongs to another organization (or doesn't exist).
- `"No fields provided to update"` — an `update_*` call with every optional
  argument left as `None`.
- `"Need at least 2 application_ids to compare"` / `"Can compare at most 6 candidates at once"` / `"All candidates must be applying to the same job"`
  — from `compare_candidates`.
- `"Cannot update a withdrawn application"` / `"Cannot revert to this status -
  the candidate's interview has already been completed."` /
  `"Unknown label(s): ..."` / `"The candidate deadline must be in the future..."`
  / `"The candidate deadline can't be later than the job application deadline."`
  — `update_application` rules, same as the website's.
- `"No applications updated: ..."` — from the `bulk_update_*` tools when every
  application was skipped; the reasons are listed.
