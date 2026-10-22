# Verified Round 2 features

Verified on 22 October 2026 against https://veribrand.onrender.com by public HTTP actions and browser use. Methods and results: [submission/VERIFICATION.md](submission/VERIFICATION.md). These are automated checks, not human user tests.

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
