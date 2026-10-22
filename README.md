# VeriBrand

Team 27 — DHEERAJ M G and Charan Teja Arangi.

Pre-publication brand governance for fictional Acme Hydrate: review a draft, inspect cited findings, make human decisions, create a new version, and obtain Manager approval and Reviewer sign-off for retained medical risks.

The repository was initialized during this build on 22 October 2026. Commit timestamps are the actual system timestamps; no claim about an earlier empty repository has been independently verified.

**Live demo: [veribrand.onrender.com](https://veribrand.onrender.com)** · [Public repository](https://github.com/DheerajMG-Bng/veribrand)

The live HTTP smoke test and a separate uncached Groq request passed on 22 October 2026. [Verification evidence](docs/BUILD_VERIFICATION.md) distinguishes local browser checks, cached AI results, and actual provider calls. This is a shared hackathon demo, not a production service.

## Try it

1. Click **Try the guided demo**, then **Run review**. Inspect a cited knowledge code.
2. **Accept**, **Edit**, or **Reject with reason** on findings. Nothing changes automatically.
3. **Apply fixes** creates a version; review that version before submitting. You can also edit the whole draft.
4. Decide every high-severity finding and **Submit for approval**.
5. Switch the simulated role to **Manager** and approve or return. If medical-risk findings remain, switch to **Reviewer** and sign off with a reason or return the draft.
6. Inspect **Versions and diff**, **Comments**, and **Audit trail**.

A fully corrected draft can be approved by the Manager directly. Reviewer routing is required when a finding marked `requires_reviewer` remains in the latest review, including a finding the creator rejected with an override reason. Approval is an internal state; the product does not publish content to social networks.

## Quick start — Windows, from repository root

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
# Only if you do not already have backend/.env:
Copy-Item backend/.env.example backend/.env
# Privately edit backend/.env to configure Groq. Never commit it.
.venv/Scripts/python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open [localhost:8000](http://127.0.0.1:8000). The committed React bundle is served by FastAPI, so Node is unnecessary for this boot. Without a key, deterministic reviews and matching precomputed AI sample reviews remain available. Live AI requires your own Groq key; see [.env.example](backend/.env.example) for variable names.

For frontend changes (Node 23.6.0 was tested):

```powershell
npm ci --prefix frontend
npm run dev --prefix frontend
# Production build and copy into the committed static directory:
npm run build --prefix frontend
.venv/Scripts/python.exe -m backend.scripts.publish_frontend
```

Vite development proxies `/api` to the backend on port 8000. Commit updated `backend/app/static` when changing frontend source. Render builds Python only.

## Tests and evaluation

```powershell
.venv/Scripts/python.exe -m pytest backend/tests -q
.venv/Scripts/python.exe -m backend.scripts.run_samples
# Replay the saved real AI responses without new network requests:
.venv/Scripts/python.exe -m backend.scripts.run_samples --ai --cached-only
.venv/Scripts/python.exe -m backend.scripts.smoke_test http://127.0.0.1:8000 --ai
```

The smoke test creates clearly titled fictional test contents. The verified suite has **44 passing tests**. Rule-based sample code recall is **17/17**, with zero findings on clean sample #2. The original live AI run produced a false positive on #2; a general terminology-policy validator correction removed it when the saved responses were revalidated. Raw and corrected results are retained in `docs/`. These small sample results are not a general accuracy estimate.

`run_samples --ai` can make real provider calls on cache misses. `warm_cache` exports real results, including model, timestamp and KB hash; unavailable responses are never loaded as successful precomputed AI results. Avoid repeatedly warming the cache against a free account.

## Architecture and decisions

React + Vite + Tailwind → FastAPI → SQLAlchemy 2 + SQLite. A metadata-driven deterministic engine runs first; optional Groq analysis adds judgement findings and proposed wording. A validator grounds exact quotes, verifies code existence, limits unsupported findings, rechecks replacements, and merges overlaps. Versioned findings and explicit human decisions drive the approval workflow and audit history.

The supplied seed list contains **19 knowledge items**, despite a brief referring to 22. Only the explicitly supplied items were seeded. The implementation uses one compact KB prompt, no vector retrieval, and a three-model fallback ending in rules-only results. Model availability is external; the configured third model has not been verified live.

See [architecture](docs/ARCHITECTURE.md), [changes from plan](docs/CHANGES_FROM_PLAN.md), [verified features](docs/FEATURES.md), [known issues](docs/KNOWN_ISSUES.md), and [Round 3 designs](docs/ROUND3_PLAN.md).

## AI disclosure and demo limits

Roles are simulated via `X-Role`; **there is no authentication or tenant isolation**. Anyone using the shared demo can switch roles, change knowledge, or reset demo data. Use fictional, non-confidential content only. With AI enabled, drafts are sent to Groq; the key stays on the backend. AI suggestions are fallible, and a verified citation means a real KB code exists, not proof that every generated explanation is correct. Humans decide.

Render Free may cold-start and loses SQLite state on restart, redeploy, or spin-down; startup reseeds the demo. This also resets local daily token counters, while provider limits remain in effect. [Deployment guide](docs/DEPLOYMENT.md).

The code was generated by Codex (GPT-6.1 Sol) under Dheeraj's direction, as confirmed by the team. [AI disclosure](docs/AI_DISCLOSURE.md) and [dependency/licence inventory](docs/THIRD_PARTY_LICENSES.md). [Contributions](docs/CONTRIBUTIONS.md) records Dheeraj's team-confirmed work and leaves Charan's description for him. [User testing](docs/USER_TESTING.md) has a five-task session sheet with empty results.

Round 2 submission: [ready-to-paste form answers](docs/FORM_ANSWERS.md), [updated PDF](docs/submission/VeriBrand_Round2_Update.pdf), [editable Word report](docs/submission/VeriBrand_Round2_Update.docx), and [latest live verification](docs/submission/VERIFICATION.md). The latest uncached public AI check increased primary-model usage from 0 to 917 tokens and showed correct AI/unverified labels. Both sample reruns used the project's own 11 drafts; AI entries were saved-response cache hits, not a new independent evaluation.
