---
name: serin-candidate-outreach
description: "Serin candidate outreach module: inviting candidates, emailing them about their application, redo-interview invitations, and adding, screening and inviting sourced prospects"
---

# Serin: candidate outreach

Part of the Serin skills - start from `../using-serin-mcp/SKILL.md` for authentication, the rules every tool follows and the other modules.

Tools: `invite_candidate`, `send_application_email`, `redo_interview`,
`schedule_meeting`, `request_resume_upload`, `add_prospect`,
`screen_prospect_resume`, `invite_prospect` (and `upload_resume_file`, which only
the upload card calls).

These create applications or meetings or **email candidates**, and an email
can't be unsent. Every one except `screen_prospect_resume` works in two steps:
call without `confirm` to get a preview (the email itself, or who would be
added), show it to the recruiter, and call again with `confirm=true` only after
they explicitly agree. The recipient is always the candidate's email on file.

## Invite vs add: invite is the default

"Add", "invite", "put X on the job", "bring X in" and similar all mean
**`invite_candidate`** unless the recruiter says otherwise. After the invite
(at the preview step, or when it is sent), end your reply with a P.S. offering
the other option, e.g.:

> P.S. If you'd rather add Jane as a prospect instead - resume on file,
> screened first, no email yet - I can do that.

Use `add_prospect` directly only when the recruiter explicitly asks for a
prospect, for adding someone without emailing them yet, or for sourcing someone
with a resume to screen first.

| | `invite_candidate` (default) | `add_prospect` |
|---|---|---|
| Creates | an `invited` application | a `prospect` application |
| Emails the candidate | yes - the interview invite | no (invite later with `invite_prospect`) |
| Needs a resume | no | yes |

## Ask about labels for every new application

`invite_candidate` and `add_prospect` create an application, and **every time**
you must ask the recruiter whether to add labels to it - even if they didn't
mention labels. Labels are optional for the recruiter, but asking is not
optional for you:

- The preview lists the organization's labels (`available_labels`, and a
  "Labels: not chosen yet" line). Ask in one short line, e.g. "Add any labels?
  Available: Strong, VIP - or I can create a new one." Ask it alongside the
  preview question, not as a separate round-trip.
- If none fits and the recruiter wants one, create it with
  `update_organization_labels(create=[{name: ...}])` (see
  `../serin-applications/SKILL.md`) and use the `id` from `created`.
- Pass the answer on the `confirm=true` call as `label_ids` (catalog `id`s, max
  10). **If they don't want labels, pass `label_ids=[]`.** A `confirm=true`
  call without `label_ids` is refused with "Labels not chosen yet" and nothing
  is created or sent - ask, then call again.
- Never invent a label id or use a display name; unknown ids are refused before
  anything is sent.

## Display an email preview once

A client that can show Serin's preview cards gets the full email in the card,
and the tool's text is then only a one-line status - nothing to repeat. That
card is the preview the recruiter reviews: do not create a second email
composer, writing block or artifact, and do not repeat the recipient, subject
or body in chat. Reply with a short plain-text status, such as "Preview ready;
not sent." Ask for confirmation only when sending is the intended next step; if
the user asked for a preview only, stop after the preview and acknowledgement.

A client without cards (a terminal such as Claude Code or OpenCode) gets the
whole email as text: show it once, exactly as returned. Preserve the same
preview-before-confirmation requirement in both cases. Send through the Serin
tool only after explicit approval; do not redirect this workflow to ChatGPT's
email connection or another mail provider.

## Tools

- **`invite_candidate(job_id, email=None, candidate_user_id=None, label_ids=None, application_deadline_at=None, confirm=False)`**
  — **the default for "add" or "invite" someone** (see above): invites a
  candidate to a job: creates the `invited` application **and emails them
  their interview invite** (if delivery fails nothing is kept).
  Name the candidate with exactly one of `email` (works for someone with no
  Serin account yet — an account is created when the invite is sent and they get
  a first-time sign-in link) or `candidate_user_id` (an existing candidate
  account). **Two steps:** without `confirm` nothing is created or sent and you
  get a preview of **the email itself** (a card where the client shows one, and
  always the same thing as text: recipient, subject and the whole message, plus
  whether an account will be created and when the link expires) — show it to the
  recruiter and only call again with `confirm=true` after an explicit yes. A candidate who already applied is refused.
  **Ask about labels** before confirming and pass `label_ids` (`[]` for none) -
  see "Ask about labels" above. `application_deadline_at` (ISO, future, not
  later than the job's) is when the invite link expires. Requires permission to
  manage the job.
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

- **`schedule_meeting(application_id, topic, scheduled_time, timezone, duration_minutes, session_id=None, confirm=False)`**
  — schedules a live video meeting on Serin between the recruiter (host) and a
  candidate, e.g. a follow-up call after the interview: creates the meeting
  and **emails the candidate and the host the invitation with the join link**,
  plus an in-app notice. Meetings are private (only participants can join).
  **Ask the recruiter** for the date, time, timezone and length rather than
  assuming. `scheduled_time` is ISO 8601; without an offset
  (`2026-11-20T15:00`) it is read as local time in `timezone` (an IANA name such
  as `Asia/Kolkata`); it must be in the future. `duration_minutes` 1-480.
  `session_id` optionally ties it to a **completed** interview attempt (an
  evaluation's `primary_session`). **Two steps:** without `confirm` nothing is
  created or sent and you get the invitation as a preview; only after an
  explicit yes call again with `confirm=true`. The result has the `join_url`
  to give the recruiter, and says if an invitation email couldn't be
  delivered (then the recruiter should share the link themselves).

- **`request_resume_upload(job_id, use_link=False)`** — gets a resume **file**
  to `add_prospect` when you can't read the file yourself (a chat client - a
  file attached to the chat message can't be forwarded to a tool either). PDF
  or DOCX, max 10 MB; it works once, for this job, and expires in about 15
  minutes. What it shows depends on the client:
  - **Upload card** (clients that show Serin cards - Claude.ai, ChatGPT): the
    recruiter drops the file into the card and it goes straight to Serin over
    their own connection; there is **no link**. Tell them in one line to drop
    it in the card, then wait until the card (or they) say it is uploaded.
  - **Link** (clients without cards, or `use_link=true`): a one-time upload
    page. Show the link once and ask them to open it and choose the file. Use
    `use_link=true` only when the recruiter says the card doesn't appear or its
    upload fails.

  Then pass the upload id from the result text to `add_prospect` as
  `resume_upload_id` - never show it to the recruiter. The file never passes
  through the conversation.
- **`upload_resume_file(upload_id, files)`** — **the upload card calls this,
  never you.** It receives the file dropped into the card. It isn't offered to
  the model; if you somehow see it, ignore it.
- **`add_prospect(job_id, email, first_name, last_name, resume_url=None, phone=None, label_ids=None, application_deadline_at=None, confirm=False, resume_upload_id=None, resume_file_base64=None, resume_file_name=None)`**
  — adds a sourced candidate to a job as a **prospect** (resume on file, not
  invited, **not emailed**). **Not the default** - only when the recruiter asks
  for a prospect or for adding without emailing (see "Invite vs add"). Give
  **exactly one** resume source:
  - `resume_url` — the recruiter gave a public `https` link to a PDF or DOCX,
    max 10 MB.
  - For a resume **file**, in this order of preference:
    1. `resume_file_base64` + `resume_file_name` — you can read the file on the
       machine you run on (Claude Code, Codex, OpenCode and similar CLIs).
       Base64-encode its exact bytes (`base64 -w0 resume.pdf`, or your
       file-reading tool) - never type out, summarise or reconstruct a resume.
       The preview call checks it; send it again with the `confirm=true` call.
    2. `resume_upload_id` — you can't read the file (a chat client): call
       `request_resume_upload`, which shows the **upload card** where the client
       supports it and a one-time **link** only as the last resort.

  The file is stored and attached to the candidate and the application like an
  upload on the website; PDF or DOCX only, judged by its bytes. **Always get the resume
  from the recruiter**, even when the person already has a Serin account: never
  go looking for their resume in storage or reuse a resume URL from another
  application or tool result - ask the recruiter for the file or link before
  calling. **Two steps:** without `confirm` nothing is created, but the resume
  is checked, and you get who would be added and whether an account will be
  created; only call again with `confirm=true` after an explicit yes (an
  uploaded file stays available for that second call). **Ask about labels**
  before confirming and pass `label_ids` (`[]` for none), as for
  `invite_candidate`. Someone who already applied is refused.
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

**Invite a candidate to a job** (also what "add Jane to the job" means):
1. `invite_candidate(job_id, email="jane@example.com")` — show the recruiter the
   email that would go out (recipient, subject, message), and whether an account
   will be created and until when the link works. Ask whether to add labels
   (listing the available ones). End with the P.S. offering to add them as a
   prospect instead.
2. Only after an explicit yes: the same call with `confirm=true` and
   `label_ids=[...]` (or `label_ids=[]` if they want none).

**Tell a candidate the outcome:**
1. `get_application_detail(application_id)` to confirm who and where they are.
2. `send_application_email(application_id, template="accepted")` (or
   `rejected` / `under_review`) — show the preview to the recruiter.
3. Only after an explicit yes: the same call with `confirm=true`.

**Take a sourced candidate through to an invite** (only when the recruiter asks
for a prospect):
1. Ask the recruiter for the candidate's resume (needed even if the person
   already has a Serin account).
   - A file you can read (a CLI): `add_prospect(job_id, email, first_name,
     last_name, resume_file_base64=..., resume_file_name="jane.pdf")`.
   - A file you can't read (a chat client, including a file attached to the
     message): `request_resume_upload(job_id)`. With the upload card, ask them
     to drop the file into it and wait for "uploaded"; without one, show the
     link once. Then `add_prospect(..., resume_upload_id=...)`.
   - A public link: `add_prospect(..., resume_url=...)`.

   Show who would be added and ask whether to add labels, then (after a yes)
   the same call with `confirm=true` and `label_ids` (`[]` for none).
2. `screen_prospect_resume(application_id)` — tell the recruiter the score.
3. `invite_prospect(application_id)` — show the email, then (after a yes)
   `confirm=true`.

**Give a candidate another attempt:**
1. `get_application_detail(application_id)` to confirm they've interviewed.
2. `redo_interview(application_id)` — show the invitation, then (after a yes)
   `confirm=true`.

**Schedule a follow-up meeting with a candidate:**
1. Find the application (`list_job_applications(job_id, search="Jane")`).
2. Ask for the date, time, timezone and length if the recruiter didn't say.
3. `schedule_meeting(application_id, topic=..., scheduled_time=..., timezone=...,
   duration_minutes=...)` — show the invitation and the time, then (after a yes)
   the same call with `confirm=true`; give the recruiter the `join_url`.

**Invite a specific candidate to apply:**
1. `list_organization_jobs(search=...)` to find the `job_id`.
2. `invite_candidate(job_id, candidate_user_id)`.

## Errors

- `"Labels not chosen yet. Before creating this application, ask the
  recruiter..."` — from `invite_candidate` / `add_prospect` with `confirm=true`
  and no `label_ids`. Nothing was created or sent: ask the recruiter, then call
  again with their labels or `label_ids=[]`.
- `"Unknown label(s): ..."` / `"An application can have at most 10 labels"` —
  from `invite_candidate` / `add_prospect`; use `id`s from
  `list_organization_labels`.
- `"Candidate already has an application for this job"` / `"Candidate not
  found"` / `"That user is a team member, not a candidate"` / `"You do not have
  permission to send invites for this job"` / `"Provide exactly one of `email`
  or `candidate_user_id`"` / `"A valid candidate email is required"` / `"The
  candidate deadline can't be later than the job application deadline."` —
  from `invite_candidate`.
- `"A custom email needs both a subject and a body"` / `"You do not have
  permission to email for this job"` / `"This candidate has no email address on
  file"` — from `send_application_email`.
- `"Resume screening already completed for this application"` / `"Resume
  screening is already in progress for this application"` / `"Only
  prospect-origin applications can be screened from analysis"` / `"This
  application does not have a resume to screen"` — from
  `screen_prospect_resume`.
- `"Provide the resume in exactly one way: ..."` — from `add_prospect` with no
  resume source or more than one.
- `"resume_file_base64 is not valid base64..."` / `"The resume file must be a
  PDF or DOCX"` / `"The resume file is larger than 10MB"` — from `add_prospect`
  with `resume_file_base64` (send the file's real bytes; ask for a PDF or DOCX).
- `"That upload link was not found, has expired or was issued for another
  job..."` / `"No resume has been uploaded yet..."` — from `add_prospect` with
  `resume_upload_id` (wait for the upload, or call `request_resume_upload`
  again if it expired or was refused).
- In the upload card (shown to the recruiter, not to you): `"This upload card
  has expired or belongs to someone else..."` / `"A resume was already uploaded
  with this card."` / file-type and size errors. If the recruiter reports one,
  call `request_resume_upload` again; if the card itself doesn't work, call it
  with `use_link=true`.
- `"The resume link must use https"` / `"The resume link must point to a PDF or
  DOCX file"` / `"The resume link is not allowed"` / `"That person already has
  an application for this job"` — from `add_prospect`.
- `"Only prospect applications can be promoted to invited"` / `"Resume is
  required before sending an invite."` / `"Resume screening is in progress for
  this candidate."` / `"Resume score is below the job threshold for sending an
  invite."` — from `invite_prospect`.
- `"This candidate has not taken an interview yet, so there is nothing to
  redo"` / `"The candidate withdrew this application"` — from `redo_interview`.
- `"The meeting time must be in the future"` / `"Unknown timezone - use an IANA
  name ..."` / `"scheduled_time must be an ISO 8601 date and time ..."` /
  `"Interview session must be completed before scheduling a meeting"` / `"You
  do not have permission to schedule meetings for this job"` — from
  `schedule_meeting`.

- If a `confirm=true` call comes back as `"The result of ... could not be
  confirmed"`, **do not call again** - that can email the candidate twice. Settle
  it first: after `invite_candidate`, `list_job_applications` shows whether the
  candidate now has an `invited` application; after `add_prospect`, whether the
  person is listed; after `invite_prospect`, `get_application_detail` shows
  whether the status is `invited`. An email with nothing to look up
  (`send_application_email`, `redo_interview`, `schedule_meeting`) is the
  recruiter's decision to repeat.
