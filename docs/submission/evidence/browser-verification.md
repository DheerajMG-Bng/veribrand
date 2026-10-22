# Public browser verification

Performed by the build agent on 22 October 2026 against https://veribrand.onrender.com. These are machine-operated checks, not human usability sessions.

- Guided demo button created and opened content #10. The page displayed the supplied sample #1 and the guided instructions.
- AI toggle was switched off; Run review displayed rule findings, Rule-based labels and Verified citation labels.
- Clicking T-02 opened Product name with the actual knowledge text, “Product name must be Acme Hydrate.”
- Dashboard sample selector #2 populated the new-draft modal with the exact clean announcement and its character count. Create draft opened the persisted Sample 2 draft.
- Content #6, created by the separate uncached HTTP check, displayed “AI-suggested · 90% confidence” and “Unverified, needs a human”. Accept was disabled. `live-ai-label.jpg` records the view.
- The header's AI status changed from its initial loading/default display to AI available after the status response arrived.
- The role selector was changed to Admin. On the grouped Knowledge Base page, G-01 Edit opened the metadata/title form. Its title was changed to “Voice submission verification”, saved and observed, then changed back to “Voice”, saved and observed. No policy text changed. The page again displayed 19 items.
- Role was returned to Creator and the dashboard reopened.

Full accept/edit/reject, version application, submission, Manager/Reviewer approval, return, comments, diff, audit, admin mutation, input boundaries and rate-limit behavior were exercised separately over the actual public HTTP API; see `live-feature-verification.json`. They were not all repeated as browser clicks in this session. The earlier local-browser journey is additional historical evidence, not a substitute for these public HTTP checks.

Confusing/partial behavior observed: initial status briefly says Rules available while status data loads; the generic rules-only progress message still mentions AI grounding. These did not block the tested workflows. The UI is a simulated shared-role demo, not authentication.
