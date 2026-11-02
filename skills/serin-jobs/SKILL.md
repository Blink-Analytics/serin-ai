---
name: serin-jobs
description: "Serin MCP jobs module: organization profile, location search, and listing, reading, creating, editing and deleting job postings (including how to write interview objectives)"
---

# Serin MCP: jobs

Part of the Serin MCP skills - start from `../using-serin-mcp/SKILL.md` for authentication, the rules every tool follows and the other modules.

Tools: `get_organization_details`, `search_locations`, `list_organization_jobs`,
`get_job_details`, `create_job`, `update_job`, `delete_job`.

## Tools

### Organization context and places

- **`get_organization_details()`** — the caller's organization profile: name,
  description, website, address, domains, team size, type, founding year.
  Fields the org hasn't filled in are null — don't invent them. Also `labels`:
  the org's application-label catalog (`{id, name}`); the `id` slugs are what
  `label_ids` takes on the application tools.
- **`search_locations(query)`** — Google Places city search. Returns
  `{place_id, description}` candidates. A job's city and country are resolved
  from a `place_id` on the server, so they are always real; never make up a
  `place_id`.

### Jobs (`app/tools/jobs.py`)

- **`list_organization_jobs(job_status=None, application_status=None, search=None, limit=25, offset=0)`**
  — the org's job postings, newest first, with the numbers the dashboard's
  jobs table shows: settings (`job_status`, `job_visibility`,
  `application_status`, `application_deadline_at`, `tags`,
  `screen_recording_enabled`, `allow_poor_connectivity_retry`,
  `resume_threshold`), `created_at`/`updated_at`, `is_accepting_applications`
  (published, applications open, deadline not passed - the dashboard's
  "Open"), and raw counts `applications_received`, `accepted_applications`,
  `interviews_completed`. Filter by `job_status` (`draft` | `published` |
  `archived`), `application_status` (`open` | `closed`) and `search` (title,
  2+ characters). Paged: `total` matches, `has_more` means another page at
  `offset + limit`. For scores and the evaluated funnel use
  `get_job_analysis`; for the full job use `get_job_details`.
- **`get_job_details(job_id)`** — everything stored for one job: settings,
  the job description (`details`), `job_description` (the recruiter's source
  text), `job_domains`, `objectives`, `interview_custom_questions` and
  `pre_application_questions` (with their `id`s). Shaped like the inputs of
  `create_job`/`update_job`, so read → tweak → send back.
- **`create_job(job_title, job_description, details, job_domains=None, experience_years=None, interview_duration=60, objectives=None, objectives_approved=False, interview_custom_questions=None, pre_application_questions=None, tags=None, job_visibility="Public", allow_poor_connectivity_retry=True, allow_resume_reupload=False, screen_recording_enabled=False, resume_threshold=0, application_deadline_at=None, job_status="draft")`**
  — creates a complete job, equivalent to the Serin website's New Job page.
  The website runs AI steps on the recruiter's title + description;
  **you do that part yourself** (see "Create a job" below) and pass the results
  in:
  - `job_description` — the recruiter's free-text posting (max 5,000 chars).
  - `details` — the structured job description (schema v1.4): `job_summary`,
    `employment_type {agreement: Employee|Contractor|Intern, schedule:
    Full-time|Part-time, term: Permanent|Temporary}`, `location {type:
    REMOTE|ONSITE|HYBRID, place_id, applicantLocationRequirement}`,
    `key_objectives`, `day_to_day_duties`, `technical_skills`, `soft_skills`
    (plain string lists), `experience_description`, `required_qualification`,
    `accepts_experience_in_lieu`, `company_summary`, `growth_opportunities`,
    `salary {min, max, currency, frequency: hourly|weekly|monthly|annually}`
    (optional) and `benefits`. Only extract what the posting supports; leave a
    field at its default rather than inventing facts.
    - `location.place_id` (from `search_locations`) is **required for
      ONSITE/HYBRID** and optional for REMOTE. `applicantLocationRequirement`
      is at most 4 words ("Pune, India", "US hours"); it defaults to the
      resolved "City, Country".
  - `job_domains` — up to 3 of: Engineering, Software Development, Data
    Science & Analytics, Product Management, Design & UX, Marketing, Sales,
    Finance & Accounting, Human Resources, Operations, Customer Success, Legal,
    Healthcare, Education, Manufacturing, Consulting, Research & Development,
    IT & Infrastructure, Cybersecurity, Quality Assurance, Business
    Development, Supply Chain & Logistics, Administrative.
  - `experience_years` — required years (sets the job's experience filter).
  - `interview_duration` — minutes, 10-60.
  - `objectives` — exactly **5** `{objective, importance 0-10, difficulty
    0-10}` items (**3** when `interview_duration` is under 20), most critical
    first. These are what the AI interviewer assesses. **Review them with the
    recruiter before saving** (see "Writing interview objectives"); the call is
    rejected unless `objectives_approved=true`, which you may only set after
    the recruiter has confirmed. Required to publish.
  - `interview_custom_questions` — optional `{question, evaluationHints,
    difficulty, importance}` items Serin asks live. Limit by duration: 3 (up to
    20 min), 6 (up to 40), 9 (up to 60). Weak prompts such as a bare topic are
    rewritten into full questions (listed in `notes`).
  - `pre_application_questions` — optional `{enabled, deliveryMode:
    application|phone_call, questions: [{question, type: yes_no|numeric,
    expectedAnswer, numericOperator: gt|lt|eq}]}`, 1-10 questions.
  - `job_status="draft"` (default) saves a draft; `"published"` requires
    `objectives` and `application_deadline_at` (ISO 8601, in the future) and
    fails if the organization already has 10 published jobs. Publishing inserts
    the draft and then publishes it in a follow-up update, as the website does.
  - Saving a draft whose title matches one of *your* existing drafts in the
    organization updates that draft instead of creating a duplicate (the
    website does the same); the result's `notes` says so.
- **`update_job(job_id, job_title=None, job_description=None, details=None, job_domains=None, experience_years=None, interview_duration=None, objectives=None, objectives_approved=False, interview_custom_questions=None, pre_application_questions=None, tags=None, job_visibility=None, allow_poor_connectivity_retry=None, allow_resume_reupload=None, screen_recording_enabled=None, resume_threshold=None, application_deadline_at=None, job_status=None, application_status=None)`**
  — edits any part of a job; only pass what you want to change (call
  `get_job_details` first).
  - `details` is a partial edit: unset fields are kept; a list or object you
    set replaces the stored one. To move an ONSITE/HYBRID job, pass a new
    `place_id` in `details.location`; without one the stored city/country stay.
  - `objectives` replaces the whole set and needs `objectives_approved=true`
    after the recruiter confirms the change. Shortening `interview_duration`
    below 20 minutes without sending 3 objectives is flagged in `notes`.
  - `interview_custom_questions` / `pre_application_questions` replace the
    whole list — re-send existing questions with their `id` to keep them (ids
    are what past interview reports refer to).
  - `job_status`: `published` runs the same checks as `create_job`; `draft`
    unpublishes and closes applications; `archived`. `application_status`
    (`open` | `closed`) opens/closes applications.
  - `application_deadline_at` can be moved but never cleared, and must be in
    the future.
- **`delete_job(job_id, confirm=False)`** — permanently deletes a job with
  all its applications and interview sessions. **Two steps:** without
  `confirm` nothing is deleted and you get a preview (`requires_confirmation`,
  `applications_count`, `interviews_count`, whether it is still accepting
  applications). Show that to the recruiter and only call again with
  `confirm=true` after they explicitly agree. To just take a job off the site
  use `update_job(job_status="draft")`, which keeps the data. Only the job's
  author, the organization's owner, or an admin/manager may delete. Candidates
  are not notified. Its applications, interview sessions and candidate
  submissions go with it.

## Flows

**Delete a job:**
1. `delete_job(job_id)` — read the preview back to the recruiter (title,
   applications and interviews that would be lost).
2. Only after an explicit yes: `delete_job(job_id, confirm=true)`.

**Create a job:**
1. `get_organization_details()` — write `company_summary` and
   `growth_opportunities` from the real profile; leave them empty if the org
   hasn't provided one rather than guessing.
2. Draft `details` from the recruiter's posting. Ask about anything essential
   the posting doesn't say (employment type, location, salary) instead of
   assuming.
3. ONSITE/HYBRID: `search_locations(query)`, confirm the city with the
   recruiter when several match, and put the chosen `place_id` in
   `details.location`.
4. Propose the interview objectives (below), discuss and adjust them with the
   recruiter, and only then pass them with `objectives_approved=true`.
5. `create_job(...)` as a draft first so the recruiter can review it; when they
   are happy, `update_job(job_id, job_status="published",
   application_deadline_at=...)` (or create it published directly).

**Edit a job:**
1. `get_job_details(job_id)`.
2. `update_job(job_id, ...)` with only the changed parts.

## Writing interview objectives

Objectives are the competencies the AI interviewer will assess in the live
interview, so they must be things a candidate can demonstrate in the interview's
duration. Propose them, show them to the recruiter with their scores, ask
whether to keep or change any, and apply their edits before saving.

- **Exactly 5** (3 for interviews under 20 minutes), ranked by how strongly
  they predict success in the role: the first is the most critical area.
- Cover nearly everything the posting demands with as little overlap as
  possible — if two would lead to similar interview questions, merge or
  rewrite one.
- Concise (5-10 words): *competency + desired outcome or seniority signal*
  (e.g. "Designs fault-tolerant services that scale under load"). Synthesize —
  don't copy-paste posting phrases — and don't name the job domain.
- Calibrate to seniority (`experience_years`): juniors → tool proficiency,
  fundamentals, execution accuracy; seniors → architectural judgment,
  trade-offs, mentoring, scalability, reliability.
- **importance** 0-10 (business value): 9-10 deal-breaker (the core reason the
  role exists), 7-8.5 must-have, 4-6.5 expected baseline, 1-3.5 nice-to-have.
  Make exactly one objective 9+ and at least one 3 or below; spread the scores
  by at least 6 points; scores must reflect each objective's real value, not
  its position in the list.
- **difficulty** 0-10 (how hard it is to assess): 8.5-10 rare expertise
  (7-10+ years), 5-8 intermediate to advanced (3-6 years), 1-4.5 routine or
  foundational.

## Errors

- `"Job not found in your organization"` - the `job_id` exists but belongs to
  another organization (or doesn't exist).
- `"Not authorized: only the job's author, the organization's owner or an
  admin/manager can delete a job"` — from `delete_job`. To take a job off the
  site without losing its data, use `update_job(job_status="draft")`.
- `"search must be at least 2 characters"` — from `list_organization_jobs`.
- `"Interview objectives must be reviewed with the recruiter first: ..."` — from
  `create_job`/`update_job` when `objectives` were sent without
  `objectives_approved=true`. Show the objectives to the recruiter, ask whether
  to keep or change them, then retry.
- `"City and Country are required for onsite jobs: ..."` — an ONSITE/HYBRID
  `details.location` without a `place_id`; use `search_locations`.
- `"Unknown place_id - get one from search_locations ..."` — the `place_id`
  wasn't returned by `search_locations`. Never guess one.
- `"Location lookup is not configured: GOOGLE_MAPS_API_KEY is not set"` — the
  server operator hasn't set up location search; tell the recruiter.
- `"Provide exactly 5 interview objectives for a N-minute interview ..."`,
  `"Application deadline is required"`, `"Application deadline must be in the
  future"`, `"Interview objectives are required to publish a job"`,
  `"Maximum published jobs limit reached (10)..."`, `"You can add up to N custom
  questions for a M-minute interview."` — save/publish rules, same as the
  website's.
