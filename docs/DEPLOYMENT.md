# Render deployment handoff

Local build, HTTP smoke, and browser approval checks have passed. A public live URL has **not** been deployed or verified yet.

## Dashboard steps

1. Open https://dashboard.render.com/ and sign in.
2. Select **New → Blueprint**. Connect **DheerajMG-Bng/veribrand** from GitHub and select branch **main**. Use the root `render.yaml`.
3. Review the `veribrand` web service: Python runtime, **Free** instance, build `pip install -r requirements.txt`, start `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`, health check `/api/health`. Leave Root Directory blank.
4. Render prompts for these four values (the API key must be entered privately, never sent to chat):

| Variable | Value |
| --- | --- |
| `GROQ_API_KEY` | Your existing key from `backend/.env` |
| `GROQ_MODEL_PRIMARY` | `openai/gpt-oss-120b` |
| `GROQ_MODEL_FALLBACK` | `openai/gpt-oss-20b` |
| `GROQ_MODEL_THIRD` | `qwen/qwen3.8-27b` |

`PYTHON_VERSION=3.11.9` is included in the blueprint. The key is not committed. The third model is configured as requested but has not been tested live; it safely degrades to deterministic rules if unavailable.

5. Select **Deploy Blueprint** and wait for the service to report **Live**. Copy its public HTTPS URL.
6. Reply to the build chat with `deployed: https://YOUR-SERVICE.onrender.com` so the agent can run the live smoke test and finish the verified documentation.

If Blueprint is unavailable, use **New → Web Service**, connect the same repository, and enter the settings and environment variables above manually. No Node build is needed on Render: the production React bundle is committed under `backend/app/static`.

## Verification after deployment

From the repository root:

```powershell
.venv/Scripts/python.exe -m backend.scripts.smoke_test https://YOUR-SERVICE.onrender.com --ai
```

The smoke test creates clearly titled fictional test content, exercises the approval workflow, checks SPA deep links, and optionally checks a cached AI review. It is not a load test or an authentication audit.

## Free-tier behavior

Render's free services spin down after 15 minutes of inactivity; a cold start can take about a minute. SQLite data, including the audit trail and daily AI usage counters, is lost on restart, redeploy, or spin-down. Startup reseeds the three demo contents and loads the matching precomputed sample cache. Provider-side limits still apply even when local counters reset. Open the live link before judging and allow it to finish waking up.

This is a shared demo with header-selected roles and no authentication. Use fictional, non-confidential content only. The demo's approve/return actions do not publish content externally.

Sources checked on 22 October 2026: [Render FastAPI guide](https://render.com/docs/deploy-fastapi), [Blueprint reference](https://render.com/docs/blueprint-spec), [free-tier behavior](https://render.com/docs/free).
