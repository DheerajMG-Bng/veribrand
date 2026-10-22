FIELD 1 - FEATURES COMPLETED

Guided demo creates and opens sample draft 1 in the live browser.
Sample dropdown loads a supplied draft into the form and saves it as content.
Rules-only review returns exact draft spans with real knowledge codes and Rule-based / Verified citation labels.
Clicking a cited code opens its approved knowledge item in the live UI.
An uncached live Groq review returned an AI-origin unsupported endorsement finding and increased tokens_today by 917.
The live UI labels that finding AI-suggested and Unverified, needs a human, with Accept disabled.
Creator accept, edit and reject decisions work; rejection without a reason returns a clear 422 error.
Apply decisions creates a new version; unapplied text is not silently changed.
Version history, plain before/after comparison and manual revision work on the live service.
Comments and return notes are saved against content.
Submission requires review of the latest version and decisions on high findings; unapplied fixes block submission.
Manager approval routes retained medical-risk findings to Reviewer; reasoned Reviewer sign-off approves.
Return with comment, new version, review, resubmission and Manager approval work end to end.
Audit trail records the tested workflow, decisions and AI involvement.
Knowledge Base groups all 19 supplied items; live Admin editing saves and can restore the original item.
The role switcher changes available controls; wrong-role API approval returns 403. Roles are simulated, not authentication.
AI status chip displays AI available after loading; the public status endpoint exposes observed token usage and local budget states.
The public API accepts 5,000 draft characters and rejects 5,001 with a friendly message.
The live review limiter returns a friendly 429 with Retry-After when the minute allowance is consumed.
Frontend deep links and the full approval lifecycle pass public HTTP smoke; Python serves the committed React bundle.
Local re-verification: 44 tests pass; rules-only and cached-AI sample reruns each find 17/17 expected code occurrences on the project's own 11 drafts, with zero findings on clean sample 2. This is not general accuracy.

FIELD 2 - TECHNOLOGY AND IMPLEMENTATION

React 19, Vite and Tailwind CSS provide the browser UI; FastAPI, Pydantic v2, SQLAlchemy 2 and SQLite implement the API, validation and versioned data. FastAPI serves the committed React build in one Render Python service. HTTPX calls Groq's OpenAI-compatible chat completions endpoint with openai/gpt-oss-120b as primary, openai/gpt-oss-20b as fallback and qwen/qwen3.8-27b as the configured third choice, followed by rules-only results. The third model has not been verified live; fallback and failure handling are tested with mocks. KB metadata drives deterministic rules, while one compact KB prompt supplies optional AI judgement and wording.

The technically difficult work is the grounding validator: it matches exact draft slices, nulls invented codes, marks unsupported claims unverified, merges overlaps and preserves Reviewer routing. Proposed replacement phrases are re-run through content rules, and applying human decisions creates a version that must be reviewed again. SHA-256 caching includes normalized draft, channel, KB hash and AI flag; precomputed results keep genuine model provenance. Per-model token accounting skips locally busy/exhausted models, supports short Retry-After and safe fallback, and degrades without exposing provider errors. An uncached public check increased daily primary-model usage from 0 to 917 tokens and displayed an AI-suggested unverified finding. Roles are simulated via X-Role, not real authentication. Both sample reruns found 17/17 expected code occurrences on our own 11 drafts; the AI rerun used saved responses, and this is not general accuracy.

FIELD 3 - CHANGES FROM ROUND 1 AND WHY

Compared with the team's supplied Round 1 baseline, Gemini became Groq with a three-model configured chain, token accounting and rules-only fallback, using the available provider setup. Supabase/PostgreSQL became SQLite to reduce deployment dependencies, accepting ephemeral storage on Render Free. pgvector retrieval became the full compact 19-item KB in one prompt, because the supplied knowledge set is small. React is served by FastAPI as one deployment rather than a separate frontend service. Password-backed identity was reduced to simulated roles for the demo, and image/DOCX/PDF ingestion was deferred to Round 3 to finish the text workflow. The delivered implementation includes metadata-driven rules, replacement revalidation and a labelled precomputed demo cache to make review behavior and quota use easier to manage. The original Round 1 document was not independently inspected; this comparison uses the team's supplied plan description.

FIELD 4 - WHAT DOES NOT WORK YET

There is no real authentication, tenant isolation or durable production database; anyone can switch demo roles, and Render Free restarts/redeploys can erase SQLite and local usage counters. Image and DOCX/PDF review, guideline-clarity analytics, human-labelled evaluation metrics in the UI and calibrated confidence are not implemented. The third configured Qwen model has not been verified live, and provider quotas can still force rules-only review. Citation/quote checks do not prove every AI explanation is semantically correct; the original AI sample run had a documented false positive before the terminology validator correction. Replacements are checked as local phrases; full influencer disclosure is checked on mandatory review of the revised draft. KB changes do not automatically re-review existing versions or preserve historical source text. The diff is plain before/after, admin metadata editing is technical, the initial AI chip can briefly show Rules available while loading, and rules-only progress copy still mentions AI. No human usability sessions or independent accuracy evaluation have been recorded. Core tested public workflows passed, including a real provider token increase; no accounting or AI-label fix was needed.

FIELD 5 - IMPROVEMENT 1

Guideline-Clarity Insights will help managers see which brand rules repeatedly confuse creators. It will combine finding history and override reasons into a recurring-issue dashboard with counts, rates and links to the underlying drafts. Versioned guideline snapshots will keep old and new wording separate, and minimum sample counts will prevent weak signals from being presented as conclusions. Managers will use those examples to clarify guidelines while keeping every policy change under human approval. Success will be measured by reproducible aggregates and a future comparison of the time needed to identify recurring problems; AI summaries will be cut first if time is short.

FIELD 6 - IMPROVEMENT 2

Multi-format review will let creators submit images and DOCX/PDF files instead of copying everything into a text box. Document extraction will preserve page or paragraph locations so a finding can be checked against the original source. Image review will cover alt text, measurable contrast, brand palette and logo checks, with vision support used only after the provider capability is verified. Unsupported or unreadable regions will be marked for a human rather than guessed, and the existing decisions, versions and approvals will remain in use. We will measure extraction coverage, source-location correctness and labelled check quality; advanced logo and aesthetic checks will be cut before the basic document workflow.

FIELD 7 - IMPROVEMENT 3

The reliability and evaluation harness will make review quality measurable beyond our own 11 sample drafts. A versioned human-labelled benchmark will test citations, spans, unsupported claims, unsafe replacements, workflow routing and provider failures. Users will be able to report a wrong finding separately from deciding whether to change their draft. The UI will show benchmark-scoped precision and recall with counts and evaluation dates, while model confidence remains labelled as uncalibrated until measured. Success means reproducible metrics and repeatable failure handling; live comparison dashboards and automated calibration will be cut before the fixed benchmark and feedback workflow.
