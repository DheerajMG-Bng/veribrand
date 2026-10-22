# Changes from the supplied Round 1 plan

This comparison follows the plan summarized in the build brief. The original planning documents were not independently reviewed. The baseline is the team-supplied description; the delivered column was checked against implementation and public workflow on 22 October 2026.

| Planned direction | MVP implementation | Reason |
| --- | --- | --- |
| Gemini | Groq via HTTPX, GPT-OSS primary/fallback and configured Qwen third fallback, then deterministic-only results | Use the supplied provider configuration and constrain failures and token use. Both GPT-OSS models were observed live; the third model was tested only through mocked fallback behavior. |
| Supabase / PostgreSQL | SQLAlchemy 2 + SQLite | Remove external database setup for the hackathon; retain relational versions, findings and audit. Persistence on the free deployment is a known compromise. |
| pgvector retrieval | Whole compact KB in one prompt | The explicitly supplied KB has 19 small items; retrieval infrastructure is unnecessary for this scope and could omit relevant policy. |
| Separate React deployment | Built React bundle committed and served by FastAPI | One service, one origin, no Node build on Render and fewer deployment dependencies. |
| Real user roles | Header-selected simulated roles with backend permission and state guards | Demonstrate the workflow without building identity administration. This provides no real authentication or isolation. |
| Image and DOCX/PDF review | Text only | Keep the core review, decision and approval path testable; multi-format ingestion is committed to Round 3 design. |
| Rule implementation detail not specified in supplied baseline | Data-driven rule metadata on knowledge items | Knowledge changes can affect deterministic checks without a code-specific branch per policy code. |
| Replacement implementation detail not specified in supplied baseline | Replacement revalidation plus mandatory whole-version re-review | Avoid suggesting another banned phrase and prevent unapplied fixes from being submitted as if present in the text. |
| Demo reliability implementation choice | KB-matched precomputed sample response cache, labelled in the UI | Reduce judging latency and provider quota consumption; original provider results and model/time provenance are retained. |

None of these substitutions establishes production readiness. [Known limitations](KNOWN_ISSUES.md) and [verification evidence](BUILD_VERIFICATION.md) describe the actual scope.
