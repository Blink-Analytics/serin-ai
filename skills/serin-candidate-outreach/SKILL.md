---
name: serin-candidate-outreach
description: "Serin MCP candidate outreach module: inviting candidates, emailing them about their application, redo-interview invitations, and adding, screening and inviting sourced prospects"
---

# Serin MCP: candidate outreach

Part of the Serin MCP skills - start from `../using-serin-mcp/SKILL.md` for authentication, the rules every tool follows and the other modules.

Tools: `invite_candidate`, `send_application_email`, `redo_interview`,
`request_resume_upload`, `add_prospect`, `screen_prospect_resume`,
`invite_prospect`.

These create applications or **email candidates**, and an email can't be
unsent. Every one except `screen_prospect_resume` works in two steps: call
without `confirm` to get a preview (the email itself, or who would be added),
show it to the recruiter, and call again with `confirm=true` only after they
explicitly agree. The recipient is always the candidate's email on file.

## Display an email preview once

When the client displays a Serin email or invitation preview card, that card
is the preview the recruiter reviews. Do not create a second email composer,
writing block, artifact, or repeat the recipient, subject or body in chat.
Reply with a short plain-text status, such as "Preview ready; not sent."
Ask for confirmation only when sending is the intended next step; if the user
asked for a preview only, stop after the preview and acknowledgement.

If the card is unavailable or the user explicitly requests a text copy, show
the exact returned recipient, subject and body once as plain text. Preserve
the same preview-before-confirmation requirement in both cases. Send through
the Serin tool only after explicit approval; do not redirect this workflow
to ChatGPT's email connection or another mail provider.

## Tools

- **`invite_candidate(job_id, email=None, candidate_user_id=None, label_ids=None, application_deadline_at=None, confirm=False)`**
  — invites a candidate to a job: creates the `invited` application **and
  emails them their interview invite** (if delivery fails nothing is kept).
  Name the candidate with exactly one of `email` (works for someone with no
  Serin account yet — an account is created when the invite is sent and they get
  a first-time sign-in link) or `candidate_user_id` (an existing candidate
  account). **Two steps:** without `confirm` nothing is created or sent and you
  get a preview of **the email itself** (a card where the client shows one, and
  always the same thing as text: recipient, subject and the whole message, plus
  whether an account will be created and when the link expires) — show it to the
  recruiter and only call again with `confirm=true` after an explicit yes. A candidate who already applied is refused.
  `application_deadline_at` (ISO, future, not later than the job's) is when the
  invite link expires. Requires permission to manage the job.
- **`send_application_email(application_id, template, subject=None, body=None, skip_status_update=False, confirm=False)`**
  — emails the candidate about their application using Serin's branded
  templates (`under_review`, `accepted`, `rejected`, `interview_completed`) or a
  `custom` one (needs `subject` and plain-text `body`; `{{candidateName}}`-style
  merge tags are filled in). **Two steps:** without `confirm` nothing is sent
  and you get the email as a preview — a card where the client shows one, and
  always the full message as text (recipient, subject, body). Follow the
  display-once rule above and only call again with `confirm=true` after an
  explicit yes.
  The recipient is always the candidate's email on file (no CC/BCC/attachments).
  `under_review` / `accepted` / `rejected` also move the application to that
  status **once the email is delivered** (not instantly) — pass
  `skip_status_update=true` to send without that. Requires permission to manage
  the job.

- **`redo_interview(application_id, confirm=False)`** — invites a candidate who
  has already interviewed to **retry**: moves the application back to
  `interview_scheduled`, notifies them in the app and **emails them the redo
  invitation**. **Two steps:** without `confirm` nothing is changed or sent and
  you get the invitation as a preview (a card where the client shows one, and
  always as text: recipient, subject, whole message) — show it and only call
  again with `confirm=true` after an explicit yes. The recipient and wording are
  fixed. Refused for a withdrawn application or one with no interview taken.

- **`request_resume_upload(job_id)`** — a one-time link where the recruiter
  uploads a candidate's resume **file** (PDF or DOCX, max 10 MB) for
  `add_prospect`. Show them `upload_url` and ask them to open it and choose the
  file (an agent that can run commands and has the file can
  `curl -F file=@resume.pdf <upload_url>`); the file never passes through the
  conversation. It works once and expires in about 15 minutes. When they say it
  is uploaded, pass `upload_id` to `add_prospect` as `resume_upload_id`.
- **`add_prospect(job_id, email, first_name, last_name, resume_url=None, phone=None, label_ids=None, application_deadline_at=None, confirm=False, resume_upload_id=None)`**
  — adds a sourced candidate to a job as a **prospect** (resume on file, not
  invited, **not emailed**). Give **exactly one** resume source: `resume_upload_id`
  (a file uploaded through `request_resume_upload` — stored and attached to the
  candidate and the application like an upload on the website) or `resume_url`
  (a public `https` link to a PDF or DOCX, max 10 MB). **Always get the resume
  from the recruiter**, even when the person already has a Serin account: never
  go looking for their resume in storage or reuse a resume URL from another
  application or tool result - ask the recruiter for the file or link before
  calling. **Two steps:** without `confirm` nothing is created, but the resume
  is checked, and you get who would be added and whether an account will be
  created; only call again with `confirm=true` after an explicit yes (an
  uploaded file stays available for that second call). Someone who already
  applied is refused.
- **`screen_prospect_resume(application_id)`** — scores a prospect's resume
  against the job (0-100 and a one-sentence reason). Internal, nothing is sent,
  so no confirm step. Only for prospects with a resume that haven't been
  screened. The score is what `invite_prospect` checks against the job's resume
  threshold.
- **`invite_prospect(application_id, confirm=False)`** — invites a prospect to
  interview: `prospect` → `invited` and **emails the invite**. **Two steps** like
  `invite_candidate` (the preview is the email itself). Refused if the
  application isn't a prospect, has no resume, is still being screened, or its
  score is below the job's threshold.

## Flows

**Invite a candidate to a job:**
1. `invite_candidate(job_id, email="jane@example.com")` — show the recruiter the
   email that would go out (recipient, subject, message), and whether an account
   will be created and until when the link works.
2. Only after an explicit yes: the same call with `confirm=true`.

**Tell a candidate the outcome:**
1. `get_application_detail(application_id)` to confirm who and where they are.
2. `send_application_email(application_id, template="accepted")` (or
   `rejected` / `under_review`) — show the preview to the recruiter.
3. Only after an explicit yes: the same call with `confirm=true`.

**Take a sourced candidate through to an invite:**
1. Ask the recruiter for the candidate's resume (needed even if the person
   already has a Serin account). A link goes straight into
   `add_prospect(job_id, email, first_name, last_name, resume_url=...)`. A file:
   `request_resume_upload(job_id)`, have them open the link and choose the file,
   then `add_prospect(..., resume_upload_id=...)`. Show who would be added, then
   (after a yes) `confirm=true`.
2. `screen_prospect_resume(application_id)` — tell the recruiter the score.
3. `invite_prospect(application_id)` — show the email, then (after a yes)
   `confirm=true`.

**Give a candidate another attempt:**
1. `get_application_detail(application_id)` to confirm they've interviewed.
2. `redo_interview(application_id)` — show the invitation, then (after a yes)
   `confirm=true`.

**Invite a specific candidate to apply:**
1. `list_organization_jobs(search=...)` to find the `job_id`.
2. `invite_candidate(job_id, candidate_user_id)`.

## Errors

- `"Candidate already has an application for this job"` / `"Candidate not
  found"` / `"That user is a team member, not a candidate"` / `"You do not have
  permission to send invites for this job"` — from `invite_candidate`.
- `"A custom email needs both a subject and a body"` / `"You do not have
  permission to email for this job"` / `"This candidate has no email address on
  file"` — from `send_application_email`.
- `"Provide exactly one of `email` or `candidate_user_id`"` / `"A valid
  candidate email is required"` / `"That user is a team member, not a
  candidate"` / `"The candidate deadline can't be later than the job
  application deadline."` — from `invite_candidate`.
- `"Resume screening already completed for this application"` / `"Resume
  screening is already in progress for this application"` / `"Only
  prospect-origin applications can be screened from analysis"` / `"This
  application does not have a resume to screen"` — from
  `screen_prospect_resume`.
- `"That upload link was not found, has expired or was issued for another
  job..."` / `"No file has been uploaded for that link yet..."` /
  `"Provide the resume as either a resume link (resume_url) or an uploaded file
  (resume_upload_id...), not both"` / `"The resume file must be a PDF or DOCX"`
  — from `add_prospect` with an uploaded file (request a new link if it
  expired or was refused).
- `"The resume link must use https"` / `"The resume link must point to a PDF or
  DOCX file"` / `"The resume file is larger than 10MB"` / `"The resume link is
  not allowed"` / `"That person already has an application for this job"` —
  from `add_prospect`.
- `"Only prospect applications can be promoted to invited"` / `"Resume is
  required before sending an invite."` / `"Resume screening is in progress for
  this candidate."` / `"Resume score is below the job threshold for sending an
  invite."` — from `invite_prospect`.
- `"This candidate has not taken an interview yet, so there is nothing to
  redo"` / `"The candidate withdrew this application"` — from `redo_interview`.

- If a `confirm=true` call comes back as `"The result of ... could not be
  confirmed"`, **do not call again** - that can email the candidate twice. Settle
  it first: after `invite_candidate`, `list_job_applications` shows whether the
  candidate now has an `invited` application; after `add_prospect`, whether the
  person is listed; after `invite_prospect`, `get_application_detail` shows
  whether the status is `invited`. An email with nothing to look up
  (`send_application_email`, `redo_interview`) is the recruiter's decision to
  resend.
