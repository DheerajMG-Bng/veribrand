# Round 3: three committed improvements

These are proposed technical designs, not completed or verified features.

## 1. Guideline-Clarity Insights

Add policy-revision IDs and immutable policy-text snapshots to findings, with real organisation/user identity and access control. Store override reasons as structured categories plus optional free text, preserving the original wording. Aggregate findings by policy revision, channel, severity, creator cohort and date range. Compute occurrence rate per reviewed draft, rejection/override rate, repeat findings after an edit, and median decision time.

Create `/api/insights/guidelines` and a Manager/Admin dashboard with recurring issues, denominator counts, example decisions and versioned policy links. Flag a guideline for human clarification only when it has a minimum sample count and an unusually high override or repeated-edit rate. An optional summarizer can cluster override reasons and propose clarification questions with links to the exact supporting events; it must not rewrite approved policy automatically.

Privacy controls redact creator text in cross-team aggregates and restrict example access. Test aggregation with fixed event fixtures, report small-sample uncertainty, and compare each insight against the underlying audit events. Acceptance: a reviewer can trace a recurring-issue alert to real findings and overrides, edit a policy revision, and compare the following review period without conflating old/new rules.

## 2. Multi-format review

Introduce `Asset` and `ExtractedSpan` records with MIME type, SHA-256, storage location, page/image coordinates, extraction method and source version. Accept explicit size/page limits and validate file signatures; scan uploads and isolate parsing workers. Keep raw uploads private and apply retention settings.

For images, use OCR plus a vision adapter targeting the requested `qwen/qwen3.8-27b` only after verifying that the selected provider endpoint supports vision for that model; otherwise use a provider-supported vision model behind the same adapter. Check missing/insufficient supplied alt text, palette distance to approved brand colours, logo presence against approved references, and text contrast where foreground/background can be measured reliably. Distinguish measured checks from model judgement and “cannot determine.” Contrast on complex backgrounds should request a human rather than invent a ratio. Every issue should link a KB code and image bounding box or reference region.

For DOCX, extract paragraphs/tables with `python-docx`; map findings back to paragraph IDs while preserving the original file. For PDFs, use `pypdf`/`pdfplumber` for selectable text with page coordinates, then OCR for scanned pages. Treat embedded prompts as untrusted document data. Never claim extraction is complete if pages are unreadable; show extraction coverage before review.

Feed extracted text through the existing deterministic engine and grounding validator, extended to page/asset offsets. Human fixes create an annotated or edited asset version; approval never silently overwrites the upload. Acceptance: labelled image, DOCX and PDF fixtures produce source-located findings; corrupt/scanned files fail clearly; a human can inspect original regions, fix, re-review and approve.

## 3. Reliability and evaluation harness

Build a versioned labelled benchmark of clean drafts, rule violations, ambiguous claims, unsupported endorsements, repeated/overlapping spans, Unicode, prompt injections and provider failures. Human annotators record expected code, span, severity and uncertainty; disagreements require adjudication and remain visible. Split evaluation examples from prompt-development examples.

Pin evaluation records to code commit, KB hash, prompt hash, provider/model and timestamp. Run deterministic tests in CI and opt-in paid/provider evaluations separately. Measure per-code and per-channel precision/recall, span overlap accuracy, unsupported-citation rate, unsafe replacement rate, workflow routing correctness, fallback success, latency and token cost. Store raw results with sensitive text controls and distinguish cached evaluations from new model calls.

Add feedback on each finding: correct/incorrect, wrong source, wrong severity, unsafe wording and optional explanation. Save feedback separately from creator accept/reject decisions; acceptance does not prove correctness. Use adjudicated labels for metrics, not raw overrides. Display benchmark version, counts, confidence intervals and evaluation date with precision/recall in the UI. Retain the present confidence display but label model confidence as uncalibrated until measured; compare confidence bins with labelled correctness before introducing calibrated thresholds.

Acceptance: CI catches regressions on the fixed benchmark, every displayed metric is reproducible from stored labels and results, and provider outage tests still complete the human approval workflow through rules-only mode.
