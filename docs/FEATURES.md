# Finished and verified features

Live FastAPI + React application at https://veribrand.onrender.com with working SPA deep links.

Fictional Acme Hydrate knowledge base with all 19 explicitly supplied items and 11 sample drafts.

Metadata-driven deterministic checks covering the supplied pattern, regex, punctuation, disclosure, hashtag, expiry, price and year rules.

Groq integration through HTTPX, with an actual uncached primary-model response verified on the deployment.

Three-model fallback and rules-only degradation, including mocked failures, timeouts, rate limits and reasoning-parameter retry tests.

Quote grounding, fabricated-code nulling, unsupported-claim labelling, unsafe-replacement removal and overlap merging.

KB-hashed review cache and 11 genuine precomputed sample responses, revalidated on load/use.

Creator accept/edit/reject decisions, required rejection reasons, right-to-left fix application and new versions.

Review-before-submit and unapplied-fix guards, Manager approval, retained medical-risk Reviewer routing and reasoned sign-off.

Return with comment, new version, re-review and resubmission, verified by live HTTP smoke.

Version history and before/after text comparison, checked in the browser and API.

Comments and per-content audit trail with role, action, details, timestamp and AI involvement.

Role-enforced APIs with clear 403s; role switching is simulated and is not authentication.

Admin knowledge add/delete and data-driven rule mutation verified through API tests; editing/reset controls implemented, with reset/usage-preservation tests.

Guided-demo entry, highlighted draft spans, clickable citations, explicit severity labels and human-decision controls checked in the local browser.

Draft length validation, per-IP review limiting and token-budget skipping verified by offline tests.

Single Python deployment using committed frontend assets, verified by fresh-clone boot and production HTTP smoke.
