---
name: serin-jobs
description: "Serin jobs module: organization profile, location search, and listing, reading, creating, editing and deleting job postings (including how to write interview objectives)"
---

# Serin: jobs

Part of the Serin skills - start from `../using-serin-mcp/SKILL.md` for authentication, the rules every tool follows and the other modules.

Tools: `get_organization_details`, `update_organization_details`,
`search_locations`, `list_organization_jobs`, `get_job_details`, `create_job`,
`update_job`, `delete_job`.

## Tools

### Organization context and places

- **`get_organization_details()`** — the caller's organization profile: name,
  description, website, email, phone, address, domains, team size, type,
  founding year. Fields the org hasn't filled in are null — don't invent them.
  Also `labels`: the org's application-label catalog (`{id, name, color}`); the
  `id`s are what `label_ids` takes on the application tools. To read or change
  just the labels use `list_organization_labels` /
  `update_organization_labels` / `delete_organization_labels` (applications
  module).
- **`update_organization_details(org_name=None, description=None, website=None, email=None, phone=None, address=None, org_type=None, founded=None, team_size=None, work_domains=None)`**
  — edits the organization profile, the same fields as the website's
  organization settings. The profile is public (it appears on the org's job
  pages). Only what you pass changes; `""` clears an optional text field
  (`org_name` can't be cleared). `website` needs `https://`; `phone` is
  international format (`+14155550100`); `founded` is 1800 to this year;
  `team_size` is one of `1-10`, `11-50`, `51-200`, `201-500`, `500+`;
  `work_domains` is up to 2 of Engineering, Robotics, Design, Sales, Marketing,
  Ops, Finance, HR, Legal (replaces the list). Only the org's owner or an
  admin/manager may edit. **Show the recruiter the change (old → new) and save
  only after they agree**; write only facts the recruiter gave or confirmed.
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
    first. These are what the AI interviewer assesses. Generate them with
    "Generating interview objectives" below and **review them with the
    recruiter before saving**; the call is rejected unless
    `objectives_approved=true`, which you may only set after the recruiter has
    confirmed. Required to publish.
  - `job_visibility` — `Public` (default; anyone with the job link can apply)
    or `Private` (only candidates you invite, and the organization's members,
    can open it; pre-application answers never auto-reject). **Ask the
    recruiter** - don't silently keep the default.
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
   the posting doesn't say (employment type, location, salary, interview duration, 
   job domain, experience in years) instead of assuming — and **ask whether the job 
   is Public or Private** (see `job_visibility` above).
3. ONSITE/HYBRID: `search_locations(query)`, confirm the city with the
   recruiter when several match, and put the chosen `place_id` in
   `details.location`.
4. Generate the interview objectives with "Generating interview objectives"
   (below), show them, swap in alternatives or adjust as the recruiter asks,
   and only then pass the final set with `objectives_approved=true`.
5. `create_job(...)` as a draft first so the recruiter can review it; when they
   are happy, `update_job(job_id, job_status="published",
   application_deadline_at=...)` (or create it published directly).

**Edit the organization profile:**
1. `get_organization_details()`.
2. Show the recruiter each field you would change, old → new.
3. Only after a yes: `update_organization_details(...)` with only those fields.

**Edit a job:**
1. `get_job_details(job_id)`.
2. `update_job(job_id, ...)` with only the changed parts.

## Generating interview objectives

Objectives are the competencies the AI interviewer assesses in the live
interview. On the Serin website they are generated by a fixed prompt; over MCP
**you** generate them, so follow that same procedure exactly (it is the
website's `generate-objectives` prompt, restated) to get the same kind of result
a recruiter would get on the website. Work through it silently and show only
the result.

**Act as** a lead talent architect and brutally honest technical hiring manager
with 15+ years of experience, turning the job description into high-signal
interview objectives scored on real business impact and technical complexity.

**Inputs** - the job title and description, plus, when known (they are
authoritative over anything the description implies):
- `job_domains`: background only, to help choose which competencies to assess.
  Never write these words, or synonyms of them, in an objective.
- `experience_years`: 0-2 → junior (tool proficiency, fundamentals, execution
  accuracy); 3-6 → intermediate to advanced (difficulty band 5.0-8.0); 7+ →
  senior (architectural judgment, trade-offs, mentoring, scalability, system
  reliability). Don't infer a different seniority from the description.
- `interview_duration` (minutes, *d*; 10 if unknown) - calibrates the time
  each objective gets (below) and how many are used: **5**, or **3** when *d*
  is under 20.

**Phase 1 - extraction and synthesis.** Identify the **5 highest-value
assessment areas** for success in the role. For each area write **two**
objectives:
- **Primary (P1-P5):** more specific, deeper or niche - specialised skills,
  technologies or advanced competencies.
- **Alternative (A1-A5):** broader or more general, assessing the same
  competency from a wider perspective; interchangeable with its Primary. A1 is
  the alternative of P1, A2 of P2, and so on.

Rules:
1. **Formula:** action verb + specific competency/skill + desired outcome or
   seniority signal, 5-10 words. Never mention the job domain, department or
   industry (it is already on the job). Bad: "Execute targeted outbound
   prospecting in Sales/Marketing to drive customer acquisition". Good:
   "Execute targeted outbound prospecting to drive customer acquisition".
2. **Maximum coverage:** together the 5 areas cover nearly all critical
   technical, functional, domain and business expectations, stated or implied.
3. **Minimum overlap:** a Primary and its Alternative assess the same
   competency at different depth; different areas assess distinct
   competencies. If two areas would lead to similar interview questions, merge
   or rewrite them.
4. **Synthesis:** don't copy-paste phrases from the description; combine
   technical skills with their real business responsibilities.
5. **Rank** the areas by how strongly they predict success: P1 is the most
   critical, P5 the least - a short interview uses only the first 3.
6. **Business value first:** the competencies that best predict success, not a
   list of every technology or duty.
7. **Seniority calibration** as above.
8. **Interview-testable:** each must be assessable within a *d*-minute
   interview.

Before showing them, check silently: the 5 areas cover nearly the whole
description; every Primary has exactly one Alternative assessing the same
competency; no two areas overlap substantially; swapping a Primary for its
Alternative changes only depth, not coverage; no objective names the domain,
department or industry.

**Phase 2 - scoring** (1.0-10.0, one decimal, e.g. 8.4), for all 10:
- **Importance** (business value), with the interview time it deserves in a
  *d*-minute interview:
  - 9.0-10.0 deal-breaker, the core reason the role exists (max(2, ⌊0.35·d⌋)+
    minutes)
  - 7.0-8.5 must-have, critical for success (max(1, ⌊0.25·d⌋)+ minutes)
  - 4.0-6.5 expected baseline competency (max(1, ⌊0.15·d⌋)+ minutes)
  - 1.0-3.5 nice-to-have or peripheral
- **Difficulty** (technical complexity): 8.5-10.0 rare expertise (7-10+ years
  of specialisation); 5.0-8.0 intermediate to advanced (3-6 years); 1.0-4.5
  routine or foundational.

**Phase 3 - mandatory scoring rules:**
1. Exactly **one** objective has importance 9.0-10.0, and at least **one** has
   importance 1.0-3.0.
2. No positional bias: don't score in ascending or descending order; each
   score reflects that objective's own value.
3. The highest and lowest importance differ by at least **6.0**.

**Show the recruiter** the active set - P1-P5 (P1-P3 for an interview under 20
minutes) with importance and difficulty - and list each one's Alternative as a
swap-in, exactly as the website's objective picker does. Ask whether to keep,
swap or change any; apply their edits (re-check the Phase 3 rules if scores
change). Then pass **only the final active set**, most critical first, as
`objectives` with `objectives_approved=true` (the alternatives aren't stored).

## Errors

- `"Job not found in your organization"` - the `job_id` exists but belongs to
  another organization (or doesn't exist).
- `"Not authorized: only the job's author, the organization's owner or an
  admin/manager can delete a job"` — from `delete_job`. To take a job off the
  site without losing its data, use `update_job(job_status="draft")`.
- `"search must be at least 2 characters"` — from `list_organization_jobs`.
- `"Not authorized: only the organization's owner or an admin/manager can edit
  its profile"` / `"Organization name is required"` / `"Please enter a valid
  URL (including https://)"` / `"Please enter a valid email"` / `"Enter the
  phone number in international format ..."` / `"Founded year cannot be in the
  future"` / `"No fields provided to update"` — from
  `update_organization_details`.
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
