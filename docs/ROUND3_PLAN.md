# Round 3 committed improvements

These are proposed designs and acceptance measures, not delivered features or measured user outcomes.

## 1. Guideline-Clarity Insights

User problem: Managers cannot currently see which guidelines repeatedly cause confusion, revisions or overrides. A single draft view hides recurring policy problems.

Technical design: Snapshot policy revision/text on each finding. Store structured override categories alongside original reasons. Aggregate issue frequency, override rate, repeat edits and decision time by policy revision, channel and date, with denominators. Add a Manager/Admin insights endpoint and dashboard linking every alert to permission-checked source findings. Require minimum sample counts; suggested clarifications remain human proposals.

Milestones:

- M1: add policy revision snapshots, override categories and fixture-based aggregation tests.
- M2: deliver counts, rates, date filters and drill-down to real evidence.
- M3: add ambiguity signals and optional grounded summaries; test small-sample and access-control cases.

How success will be measured: Proposed acceptance measures: all displayed aggregates exactly match event fixtures; every alert links to its supporting findings; no alerts below the declared sample threshold. In a future human study, compare task completion time for identifying a recurring guideline problem against the draft-by-draft baseline. No improvement percentage is claimed before measurement.

Cut first if time is short: Cut AI clustering/summaries first, then advanced cohort filters. Keep policy revisions, counts with denominators, override reasons and evidence drill-down.

## 2. Multi-format review of images and DOCX/PDF

User problem: Creators currently must paste text; they cannot submit an image, brochure or document and inspect a finding at its original page or image region.

Technical design: Add private Asset and ExtractedSpan records with file hash, MIME type, extraction coverage, page/paragraph coordinates and version. Validate file signatures and size/page limits; isolate parsing. Extract DOCX paragraphs/tables with python-docx and PDF text with pypdf/pdfplumber; use OCR for scanned pages. For images, check supplied alt text, measurable contrast, palette and logo presence with OCR/vision assistance. Evaluate the requested qwen/qwen3.8-27b only after confirming provider vision support, otherwise select a supported vision model behind an adapter. Reuse rules, grounding, decisions and approval; show cannot determine when evidence or extraction is inadequate.

Milestones:

- M1: implement validated uploads and DOCX/selectable-PDF extraction with source locations and coverage warnings.
- M2: add image/OCR ingestion, alt-text review and measured palette/contrast checks.
- M3: add supported vision/logo checks and scanned-PDF OCR; integrate asset versions and source-region review.

How success will be measured: Proposed acceptance measures: every retained finding maps to an original paragraph, page or image region; fixture tests detect corrupt/oversize files and unreadable pages without claiming complete extraction. Measure extraction coverage and per-check precision/recall on labelled format fixtures, then have a human complete review-to-approval on each supported format. Complex contrast must return cannot determine instead of an invented ratio.

Cut first if time is short: Cut custom logo detection and broad visual aesthetics first, then scanned-PDF OCR if needed. Keep DOCX/selectable-PDF extraction, basic image/alt-text checks, coverage warnings and source-located findings; do not advertise an unsupported format as complete.

## 3. Reliability and evaluation harness

User problem: The current 11-draft sample set is too small to establish general accuracy, and accepting a suggestion does not prove that it was correct. Users need clearer evidence of what a review system can reliably detect.

Technical design: Build a versioned human-labelled benchmark with separate development/evaluation splits, uncertain cases and adjudication. Record expected code, span, severity and safety labels. Pin results to code commit, KB/prompt hash, provider/model and timestamp; separate cache replays from new calls. Add finding-level correctness/source/severity/safety feedback distinct from accept/reject. Report per-code/channel precision and recall, span quality, fabricated-citation and unsafe-replacement rates, latency, token cost and fallback behavior. Display benchmark date, counts and uncertainty next to metrics; confidence remains uncalibrated until evaluated.

Milestones:

- M1: define labels, annotation guide, split and deterministic CI runner with failure injection.
- M2: store reproducible model runs and finding-level feedback; adjudicate disagreements.
- M3: publish benchmark-scoped metrics in the UI, add confidence-bin analysis and compare model/prompt revisions.

How success will be measured: Proposed acceptance measures: 100% of displayed metrics reproduce from stored labels/results; all provider-failure fixtures complete via a documented fallback or rules-only result; no known fabricated citation or rule-violating replacement passes the safety fixtures. Set quality release thresholds only after a labelled baseline exists and show sample counts and uncertainty. Confidence calibration and independent human evaluation are future measurements, not current claims.

Cut first if time is short: Cut live model-comparison dashboards, automated calibration and continuous paid evaluations first. Keep a fixed labelled benchmark, reproducible offline runner, failure fixtures, feedback records and honest metric scope.
