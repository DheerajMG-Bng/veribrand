# Changes from our Round 1 plan (Team 27)

Our Round 1 plan (Team 27) specified the Gemini API; Supabase/PostgreSQL with pgvector retrieval; a React frontend deployed separately; real user roles; image and DOCX/PDF review in scope; and Guideline-Clarity Insights, multi-format review and an evaluation harness as improvements.

| Our Round 1 plan (Team 27) | Round 2 implementation | Reason |
| --- | --- | --- |
| Gemini API | Groq via HTTPX, configured primary/fallback/third model chain and rules-only fallback | Use the existing Groq setup and handle provider failures without blocking review. |
| Supabase/PostgreSQL | SQLAlchemy 2 and SQLite | Reduce external database setup; keep relational versions, findings and audit, accepting free-tier persistence limits. |
| pgvector retrieval | Complete compact 19-item KB in one prompt | The supplied knowledge set is small; avoid retrieval infrastructure and omission of relevant rules. |
| React frontend deployed separately | React build served by FastAPI | One origin and one Python deployment; no Node build on Render. |
| Real user roles | Simulated X-Role roles and state/permission guards | Demonstrate the workflow without production identity administration; no authentication or tenant isolation. |
| Image and DOCX/PDF review in scope | Text review delivered; formats deferred to Round 3 | Finish the complete text workflow and human decisions before expanding ingestion. |
| Guideline-Clarity Insights, multi-format review and evaluation harness as improvements | Retained as the three Round 3 designs | Preserve the planned improvements with concrete milestones, measures and cut order. |

Additional Round 2 implementation decisions: metadata-driven rules let knowledge data drive checks; replacement revalidation rejects newly prohibited wording; a labelled KB-matched precomputed cache reduces demo latency and provider use. These complement our Round 1 plan (Team 27).

The third model remains not verified live: one minimal JSON-mode call on 22 October 2026 returned HTTP 403, model_permission_blocked_org (blocked at the organization level). The application code was not changed. [Evidence](submission/evidence/qwen-live-check.json).

[Known limitations](KNOWN_ISSUES.md) and [verification evidence](BUILD_VERIFICATION.md) describe the delivered scope.
