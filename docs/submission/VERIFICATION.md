# Round 2 submission verification

Date: 22 October 2026. Target: https://veribrand.onrender.com. Public verification used fictional test drafts and did not reset shared data. Application source version: main application code preceding this submission-only documentation commit.

## Public features actually exercised

| Feature | Method | Observation |
| --- | --- | --- |
| Guided demo | Live browser button | Created/opened sample 1 as content 10 |
| Sample loading | Live dropdown and Create draft | Sample 2 text and 97-character count loaded, then persisted |
| Rules review | Live browser and public API | Cited findings, exact quotes, Rule-based labels, Verified citation labels |
| Cited code | Live T-02 button | Modal showed real Product name knowledge text |
| Live AI call | Unique public API draft; before/after status | cached=false, primary GPT-OSS, tokens_today 0 to 917 |
| AI labels | Live content 6 browser view | AI-suggested, Unverified, needs a human, Accept disabled |
| Accept/edit/reject | Public decision endpoints | All three saved; reject without reason returned 422 |
| Apply decisions | Public apply endpoint | Version 2 created with both selected changes at correct offsets |
| Versions/diff | Public content + diff endpoints | Three versions and differing before/after strings returned |
| Comments | Public comment endpoint and content readback | Comment and return note both persisted |
| Submit guards | Public submit actions | Unreviewed new version blocked; reviewed/decided version submitted |
| Manager and Reviewer | Public role headers and action endpoints | Creator approve 403; Manager pending_reviewer; Reviewer approved |
| Return and resubmit | Public return/version/review/submit | changes_requested, new version, reviewed, submitted, approved |
| Audit | Public audit endpoint | 20 entries in this tested content, including decisions and sign-off |
| KB and admin editing | Browser edit/save/restore; HTTP temporary item | 19 grouped items; G-01 title change saved then restored; temporary admin item added/edited/deleted |
| Role switcher | Browser Creator to Admin and back | Admin controls appeared; Creator restored |
| AI status chip | Live browser | AI available after asynchronous load |
| Rate limit | Public repeated rules reviews | Friendly 429 and Retry-After 60 observed |
| Length limit | Public creation at boundary | 5,000 accepted, 5,001 rejected with clear 422 |

Exact API evidence: [live-feature-verification.json](evidence/live-feature-verification.json), [console log](evidence/live-feature-verification.txt). Exact AI evidence: [live-ai.json](evidence/live-ai.json). Browser observations: [browser-verification.md](evidence/browser-verification.md) and [AI label screenshot](evidence/live-ai-label.jpg). Recorded audit-entry count should be read from the JSON as the authoritative value.

## AI investigation and rerun results

There was no observed AI accounting or origin-label defect to fix. The unique public request increased daily usage by 917 tokens and produced the correctly labelled AI finding. The exact cause of an earlier zero is not proven; cached responses do not create new usage, and ephemeral SQLite can reset local counters on restart/redeploy.

The required scripts were rerun locally: **44 tests passed**, with one Starlette/AnyIO deprecation warning. Rules-only and AI-mode scripts each detected **17/17 expected code occurrences on our own 11 sample drafts**, with zero findings on clean sample 2. All AI-mode sample entries were cached genuine prior provider responses revalidated by the current code. These are not 11 fresh calls, not general accuracy, and not an independently labelled benchmark. Logs: [pytest.txt](evidence/pytest.txt), [samples-rules.txt](evidence/samples-rules.txt), [samples-ai.txt](evidence/samples-ai.txt).

Historical original live samples included one false positive on the clean draft. The earlier general terminology-policy fix and original/corrected logs are retained in the repository. No application code was changed for the present verification; the new script is verification tooling only.

## What is broken confusing or partial

No blocking core-workflow failure was observed. Initial status briefly says Rules available before AI status loads; rules-only progress copy still mentions AI. Roles have no authentication, data and counters are ephemeral on Render Free, third-model availability is unverified, confidence is uncalibrated, multi-format ingestion and the three Round 3 improvements are not delivered. KB changes do not automatically re-review old versions or snapshot historical citation text. Usability evidence is limited to three informal volunteer sessions; no formal study or independent accuracy evaluation has been done. [KNOWN_ISSUES.md](../KNOWN_ISSUES.md) explains the scope and limitations.

## Reproduction

From the repository root: `.venv/Scripts/python.exe -m backend.scripts.verify_submission`. This intentionally creates test drafts and consumes one real provider review; the final limiter test can temporarily consume that caller's minute allowance. It does not perform a global demo reset. Avoid rerunning unnecessarily against shared judging data.

Qwen third-model check: One minimal JSON-mode call on 22 October 2026 returned HTTP 403 with model_permission_blocked_org: the model is blocked at the organization level; successful live verification remains incomplete. See [evidence](evidence/qwen-live-check.json).
