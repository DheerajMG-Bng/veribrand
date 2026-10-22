# Build verification — local and public deployment

Verified by the build agent on 22 October 2026. Human user-testing and contribution records have not been filled in. The public deployment and its Groq connection have passed the checks below; Phase 7 technical documentation has been written to match this evidence.

| Check | Result | Evidence |
| --- | --- | --- |
| Backend tests | PASS: 44 tests, no failures | `test-results.txt`; one Starlette/AnyIO deprecation warning |
| Deterministic sample code recall | PASS: 17/17 expected sample-code occurrences, 100% | `sample-results-rules.txt` |
| Clean sample 2, rules only | PASS: zero findings | `sample-results-rules.txt` |
| Live AI sample run | PASS: actual Groq responses from both configured GPT-OSS models; 17/17 code recall | `sample-results-ai.txt` |
| Original AI clean-sample result | One false positive observed | Raw result retained in `sample-results-ai.txt` |
| Clean sample after validator correction | PASS: zero findings; no second live sample run | Saved provider responses revalidated offline: `sample-results-ai-validated.txt` |
| Unsupported endorsement sample 11 | PASS: one unverified AI finding | Validated results and precomputed-cache test |
| Precomputed reviews | PASS: 11 genuine saved sample responses, KB hash checked on load | `backend/seed/precomputed_reviews.json`; offline cache tests |
| Frontend build | PASS: Vite production build | `npm run build --prefix frontend`; committed assets in `backend/app/static` |
| Browser workflow | PASS: guided sample → review → accept and edit → apply → rules re-review → reasoned overrides → submit → Manager → Reviewer → Approved | `screenshots/approved-audit.jpg` |
| Browser secondary screens | PASS: version history, before/after comparison, grouped KB | Observed in the in-app browser; not human usability testing |
| HTTP smoke | PASS: full workflow including return/resubmit, comments, audit, diff, role rejection, SPA fallback | `smoke-local.txt` |
| Fresh clone | PASS: remote main cloned inside ignored `.verification/fresh`, separate venv, requirements installed, no copied `.env`, app boots without Node | Source tested at commit `8603b3e`; `smoke-fresh-clone.txt` |
| Fresh clone AI option | PASS: cached AI sample response works without a secret | `cached=True` in fresh-clone smoke log; this is not a fresh provider call |
| Python runtime tested | 3.11.0 on Windows; deployed service boot and HTTP workflow pass | Render requests 3.11.9; exact running remote patch version was not introspected |
| Repository public | PASS | GitHub repository metadata returned `visibility: public` |
| Commit times | PASS: initial commit at 12:51:43 IST on 22 Oct 2026, subsequent code commits later | Actual `git log` timestamps; no backdating |
| Secret checks | PASS: provider-key marker scan empty, `.env` untracked and ignored before pushes | `python -m backend.scripts.safe_push` |
| Public live URL smoke | PASS: https://veribrand.onrender.com | `smoke-live.txt`: full lifecycle, role rejection, return/resubmit, comments, diff, audit and SPA deep links |
| Deployed AI cache | PASS: cached sample response returned successfully | `smoke-live.txt`, `cached=True` |
| Deployed Groq connection | PASS: separate uncached review, primary model, zero findings on the submitted clean draft | `ai-live-deployment.json`: enabled=true, ai_status=ok, cached=false |

The supplied knowledge list contains **19 items**, despite the brief saying 22. All 19 explicitly listed items are seeded; no missing knowledge was invented. Additional supporting citation codes are intentionally returned for medical and environmental findings and are not counted as false positives.

The original 11-sample AI run was performed once. Cache export reused those stored results and did not call the provider again. After deployment, a separate unique clean draft made one uncached provider review to verify server configuration. Fallback exhaustion, invalid JSON, timeouts, 429 responses, short Retry-After, parameter retry, unsafe replacements, fabricated citations, repeated quotes, delimiter injection, and reviewer-risk propagation were tested offline with mocks. The third configured model was not exercised live.

This evidence establishes the tested sample workflows, not general-purpose factual accuracy or production readiness. Phrase replacements are rechecked for local content violations; influencer disclosure is checked on the entire new draft during mandatory re-review. The submitted draft may retain rejected findings with explicit override reasons; retained medical risks must receive Reviewer sign-off. That is an intentional human-governance workflow.

Deployment instructions and limitations: [DEPLOYMENT.md](DEPLOYMENT.md).
