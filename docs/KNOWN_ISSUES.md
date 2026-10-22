# Known issues and limitations

- **Simulated roles, no authentication or tenant isolation.** Anyone can select Creator, Manager, Reviewer or Admin; data is shared. Role guards exercise the workflow, not identity security.
- **Ephemeral SQLite on Render Free.** Restart, redeploy or spin-down loses drafts, knowledge edits, findings, comments, audit history and local daily usage counters. Startup reseeds the demo; provider quotas do not reset with SQLite. See [Render's free service behavior](https://render.com/docs/free).
- **Cold starts.** Render Free can spin down after inactivity; the first request may wait for startup. No uptime, latency or load guarantee has been measured.
- **Free provider quotas and model availability.** Local token accounting uses response usage, not a preflight tokenizer. An in-flight call can cross a local threshold; other applications sharing the same key are invisible to these counters. Minute accounting and the IP limiter are per process. The configured third model has not been verified live.
- **AI is fallible.** The first live sample run falsely flagged the clean product variant. A general terminology-policy validation fix removed that finding on saved-response replay; both results are retained. Existing code/quote validation cannot prove every generated explanation is semantically supported by a citation. Displayed AI confidence is model output, not calibrated probability.
- **Small evaluation set.** 17/17 expected sample-code occurrences and zero clean-sample findings are results on the supplied examples, not population accuracy. Usability evidence is limited to three informal volunteer sessions; no formal study or independent accuracy evaluation has been done.
- **Local replacement scope.** Proposed phrases are checked for content rules using the social channel. Channel-wide disclosure is checked on the new full draft at mandatory re-review. Humans can write unsafe edits; the subsequent review is required before submission.
- **Explicit overrides can remain.** A reasoned rejection leaves wording unchanged; Manager approval is possible after decisions. Retained medical risk additionally requires Reviewer sign-off. Other high-risk overrides do not require the Reviewer under this MVP's supplied workflow.
- **KB edits do not automatically revisit already reviewed content.** Hashing invalidates future cache lookup, but existing version findings retain their original citations. Historical citation text is not snapshotted; removed items are shown as historical/unavailable. Re-review a new version after policy changes.
- **Text only.** Images, DOCX and PDF ingestion are deferred. No content is posted to external publishing systems.
- **Basic comparison and audit presentation.** Diff uses plain before/after text; audit details include structured JSON. Formal WCAG conformance, all device breakpoints and all admin UI controls have not been audited in a browser.
- **One dependency warning.** The test suite emits a Starlette/AnyIO BlockingPortal deprecation warning; all 44 tests pass.
- **Python verification scope.** Fresh-clone testing used local Windows Python 3.11.0. The Render configuration requests 3.11.9; the live service passed HTTP checks, but its exact running patch version was not introspected.
- **Demo reset is destructive within the shared demo.** Admin reset removes previous contents and audit history, reseeds three examples and records a reset event. It is not a backup/recovery facility.

## Submission re-verification findings

No blocking failure was observed in the tested public core workflow. The live UI briefly displayed Rules available before status data arrived, then AI available. Its rules-only progress sentence still mentioned AI grounding. These are confusing loading/copy states, not a failure of the verified AI-origin labels. Usability evidence is limited to three informal volunteer sessions; no formal study or independent accuracy evaluation has been done.

The usage investigation measured primary-model tokens_today increasing from 0 to 917 after one unique uncached public review. The browser correctly showed AI-suggested and Unverified, needs a human. No accounting/label fix or application redeployment was needed. Earlier zero alone did not prove a bug: cached samples do not add provider usage and ephemeral SQLite can reset counters. The exact cause of the earlier zero was not independently established.

Evidence: [live AI before/after](submission/evidence/live-ai.json), [live feature checks](submission/evidence/live-feature-verification.json), [browser checks](submission/evidence/browser-verification.md).

Qwen third-model check: One minimal JSON-mode call on 22 October 2026 returned HTTP 403 with model_permission_blocked_org: the model is blocked at the organization level; successful live verification remains incomplete. See [evidence](submission/evidence/qwen-live-check.json).
