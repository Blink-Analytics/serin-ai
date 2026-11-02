---
name: using-serin-mcp
description: Start here for the Serin MCP server - authentication, the rules every tool follows, and which module skill (jobs, applications, evaluations, candidate outreach) to read before using a tool
---

# Using Serin MCP

Serin MCP exposes org-side recruiting tools for the Serin platform: job posting
management, applicant review, interview analysis, and the application
pipeline. Every tool call is scoped to the caller's own organization - there
is no way to read or write another org's data.

This is the entry point. The tools are documented in module skills; **read the
module for the job at hand before calling its tools** (they are separate
resources so you only load what you need):

| Module | Read it for | Tools |
|---|---|---|
| `../serin-jobs/SKILL.md` | Posting, editing and removing jobs; writing interview objectives | `get_organization_details`, `search_locations`, `list_organization_jobs`, `get_job_details`, `create_job`, `update_job`, `delete_job` |
| `../serin-applications/SKILL.md` | Reviewing applicants, changing status/labels/deadlines, acting on many at once | `list_job_applications`, `get_application_detail`, `compare_candidates`, `update_application`, `bulk_update_application_status`, `bulk_update_application_labels`, `bulk_update_application_deadline` |
| `../serin-evaluations/SKILL.md` | What a score, band and integrity tier mean; interview reports, recordings, job analysis | `get_interview_session`, `get_interview_recording`, `get_job_analysis` |
| `../serin-candidate-outreach/SKILL.md` | Inviting and emailing candidates, redo invitations, sourced prospects | `invite_candidate`, `send_application_email`, `redo_interview`, `request_resume_upload`, `add_prospect`, `screen_prospect_resume`, `invite_prospect` |

Which flows span modules:

- *Review applicants and decide:* jobs (find the job) -> applications (list,
  detail, update) -> evaluations (the reasoning behind a score) -> outreach (tell
  the candidate).
- *Create a job and invite people:* jobs -> outreach.

## Authentication

This server requires Supabase OAuth. Connect with `auth="oauth"` (or your
client's equivalent) — the first connection opens a browser to Supabase login,
then a consent screen on the Serin website.

- **Candidate accounts** see a plain consent screen (client name, requested
  scopes, redirect target).
- **Recruiter accounts** additionally pick which organization the connection
  acts on, if they belong to more than one. That choice is fixed for the life
  of the connection — there is no way to switch orgs mid-session; disconnect
  and reconnect (repeating consent) to pick a different org.

All of the tools below require a recruiter account. They are hidden from
`list_tools()` for non-recruiter callers, and calling one directly by name
returns a `ToolError` mentioning "recruiter role".

## Never show raw IDs to the end user

Every tool result includes UUIDs — `job_id`, `application_id`,
`candidate_user_id`/`user_id`, `organization_id`, `session_id` — purely so you
can chain them into follow-up tool calls (e.g. take a `job_id` from
`list_organization_jobs` and pass it to `list_job_applications`). **Never
print these IDs in your response to the end user** — they're internal
plumbing, not information a recruiter finds useful. Refer to rows by their
human-meaningful fields instead: job title, candidate name/email, application
status, dates, scores, etc. Keep the IDs in your own working context only,
for the next tool call.

## Rules every tool follows

- **Two-step actions.** Anything that emails a candidate, deletes data or
  changes many records at once takes `confirm` (default `false`). Without it
  nothing happens and you get a preview. Show the preview to the recruiter and
  only call again with `confirm=true` after an explicit yes. A preview that
  can't show what would happen is a failure, not an empty preview.
- **Results are typed.** A tool returns its result object or an `error` field
  (`ErrorResult`) instead of raising - check for `error` rather than assuming
  success.
- **Don't invent.** Fields an organization or candidate hasn't filled in are
  null; say so rather than guessing.

## Errors that apply everywhere

- `"Not authenticated"` - no valid access token on the call.
- `"Not authorized: recruiter role required"` - caller isn't a recruiter.
- `"Job not found in your organization"` / `"Application not found in your organization"` /
  `"Interview session not found in your organization"` - the id exists but
  belongs to a different org (or doesn't exist at all).
- `"Your session was not accepted for this action. Please reconnect and try
  again."` - the connection's sign-in needs to be refreshed.
- `"This action is not available right now. Please try again shortly."` and the
  tool-specific `"... could not be sent / created / deleted right now. Nothing
  was ..."` - the request was refused or never went out (also what a *preview*
  returns when it fails); nothing was changed, so trying again is safe once the
  recruiter has reconfirmed.
- `"The result of ... could not be confirmed - it may or may not ..."` - from a
  `confirm=true` call when no answer came back (a timeout, a dropped connection,
  a server error). **The action may have happened, so do not just call again**:
  that can email a candidate twice. Tell the recruiter the outcome is uncertain
  and settle it first where you can - each module says how (`delete_job`: check
  `list_organization_jobs`; invites and prospects: check the application; a
  `bulk_update_*` is safe to repeat). An email with nothing to look up is the
  recruiter's decision to resend.

Module-specific errors are listed in each module.
