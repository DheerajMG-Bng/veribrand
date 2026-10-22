# AI disclosure

## Development assistance

Codex wrote most implementation code, tests and technical documentation under Team 27's direction in this chat. The team requested the attribution “Codex with GPT-6.1 Sol”; the exact underlying session model identifier was not independently inspectable and is not asserted as verified here. Git commits use the human's preconfigured identity; commit authorship alone should not be interpreted as a per-person contribution record.

The build brief states that Claude helped with planning documents. Those documents and that assistance were not independently inspected. The human-fill [CONTRIBUTIONS.md](CONTRIBUTIONS.md) remains empty; no claims have been invented about which team member completed which task.

The UI and code were written for this project. Vite, React and Tailwind tooling were used; no external website template or design kit was copied. Lucide supplies the interface icons. Prettier was used as a development formatting tool (MIT licence). The exact dependency inventory is in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## AI inside the product

The backend sends draft text, channel, compact fictional brand knowledge and deterministic finding summaries to Groq's OpenAI-compatible chat endpoint when AI analysis is enabled and a suitable cache entry is unavailable. The API key remains server-side; the project excludes `.env` from version control. Users are told not to enter confidential content.

Configured model order:

1. `openai/gpt-oss-120b` — observed in the original live sample run and a separate uncached request on the deployed service.
2. `openai/gpt-oss-20b` — observed in the original live sample run and cached deployment smoke output.
3. `qwen/qwen3.8-27b` — configured as requested; not verified live. Mocked tests cover the fallback chain. If it is unavailable, the app continues with deterministic rules.

Provider/model terms are separate from the open-source library licences. Model names and configured budgets do not promise provider availability or a particular service quota.

Rules always run. AI proposes additional findings and wording; the validator checks literal quotes, source code existence, unsupported-claim handling and replacement rules. Suggestions never automatically modify a draft. Creator decisions, Manager approval and Reviewer sign-off are human-controlled demo-role operations and recorded in audit history.

## Evaluation transparency

The 11 supplied examples were reviewed live with AI once during the build. Actual saved responses, model provenance and KB hash are committed in `backend/seed/precomputed_reviews.json`. Export reused the live-run cache. Saved responses are revalidated when used, and precomputed results are labelled in the UI.

The original run produced one false positive on the clean sample. The validator was corrected and the original provider responses replayed offline, yielding zero findings on that sample. The raw result was retained. A separate low-volume uncached deployed review returned `ai_status=ok`, `cached=false` and the primary model; see [ai-live-deployment.json](ai-live-deployment.json). The public smoke test's optional AI review used a cached sample and is not presented as another live provider request.

Human testing and per-person contributions are not inferred from automated checks. Further model accuracy, prompt-injection resistance and confidence calibration remain evaluation work for Round 3.
