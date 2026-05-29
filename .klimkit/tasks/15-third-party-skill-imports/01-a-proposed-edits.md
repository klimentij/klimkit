# Third-Party Skill Imports: Safety Review And Proposed Klimkit Edits

Source request: import selected public skills into Klimkit with `klimkit-` prefixes, review safety, and prepare a proposal for later polishing before making them deeply interlinked.

## Imported Now

| Klimkit skill | Upstream | Reviewed commit | License status | Immediate safety/readiness note |
| --- | --- | --- | --- | --- |
| `klimkit-agent-browser` | `vercel-labs/agent-browser`, `skills/agent-browser` | `b4f2f37d7b4f954022bc77f8d6dce70e07072b00` | Apache-2.0 | Safe to import as a stub; later edit should require screenshots/video on every new screen because accessibility snapshots can be incomplete or misleading. |
| `klimkit-web-design-guidelines` | `vercel-labs/agent-skills`, `skills/web-design-guidelines` | `180115660cfb8a86b808f117475a01f54caf3bc5` | Upstream README says MIT; no standalone license file found | Safe enough to import with license note; later edit should make the skill generic, avoid Vercel-specific framing, and decide whether live WebFetch of external rules is acceptable. |
| `klimkit-ui-ux-pro-max` | `nextlevelbuilder/ui-ux-pro-max-skill`, `.claude/skills/ui-ux-pro-max` | `b7e3af80f6e331f6fb456667b82b12cade7c9d35` | MIT | Imported with upstream helper scripts and CSV data vendored into the skill; later edit should shrink the large body and reconcile its rules with other Klimkit design skills. |
| `klimkit-improve-codebase-architecture` | `mattpocock/skills`, `skills/engineering/improve-codebase-architecture` | `e3b90b5238f38cdea5996e16861dcae28ef52eda` | MIT | Imported with reference files moved under `references/`; later edit should replace its subagent instruction with `klimkit-code-explorer` and its temp HTML report with `.klimkit/<operator>/reports/`. |
| `klimkit-impeccable` | `pbakaus/impeccable`, `plugin/skills/impeccable` | `63074dd362ad4a9182849dbeefb8245d46e0a791` | Apache-2.0 with NOTICE | Imported with `reference/` mechanically renamed to `references/`; safety scan found local-server, token, child-process, and browser automation paths that need deeper review before live commands are default-safe. |
| `klimkit-antigravity-security-auditor` | `sickn33/antigravity-awesome-skills`, `skills/security-auditor` | `bbfe09c18ead0e7ff2899d5aec29f35d8ca03bca` | MIT for code, CC BY 4.0 for content | Imported as a candidate; later edit should shrink broad encyclopedia content into Klimkit-style concrete findings and align with `klimkit-security-auditor`. |

## Blocked From Import

| Requested skill | Reason |
| --- | --- |
| `roin-orca/skills --skill simple` | No license file or license notice was found in the cloned repo. The skill also contains hostile prompt text saying not to scan the repository and to skip all tests, plus an XSS-looking image payload. Do not redistribute this content. If the idea is useful, create a fresh Klimkit-owned lightweight brainstorming skill instead of copying it. |

## Proposed Edits For Review

### `klimkit-agent-browser`

- Add a Klimkit rule: every new screen or materially changed UI state must be checked with a screenshot, not only an accessibility snapshot.
- Explain why: accessibility trees can omit visual layout, overlap, clipping, canvas/SVG/image content, hidden-but-visible CSS states, and responsive issues.
- Route browser proof into `klimkit-walkthrough` and `.klimkit/<operator>/reports/`.
- Keep cloud/remote browser and parallel-session modes opt-in unless the user explicitly needs them.

### `klimkit-web-design-guidelines`

- Make the skill generic: present it as web interface guidelines, not Vercel-specific review.
- Decide whether to keep live fetching from the upstream raw URL. Safer options are to vendor a pinned rules snapshot or require the agent to disclose that it fetched current external rules.
- Align output with Klimkit review style: findings first, severity, file/line, fix, and skipped checks.
- Link it to `klimkit-agent-browser` for visual confirmation and `klimkit-walkthrough` for proof reports.

### `klimkit-ui-ux-pro-max`

- Split the 600+ line `SKILL.md` into a concise trigger/workflow plus references.
- Keep the vendored `scripts/search.py` and CSV data self-contained, but move command examples behind a shorter workflow so agents do not over-index on the database before understanding the product context.
- Add Klimkit visual QA expectations: screenshots at desktop/mobile, no text overflow, no overlapping controls, and real asset rendering.
- Reconcile its design rules with `klimkit-impeccable`, `klimkit-web-design-guidelines`, and existing Klimkit frontend guidance to avoid competing style systems.

### `klimkit-improve-codebase-architecture`

- Replace `Agent tool with subagent_type=Explore` with inline `klimkit-code-explorer`.
- Write architecture reports under `.klimkit/<operator>/reports/<task>/` instead of OS temp by default.
- Replace its internal grilling loop with `klimkit-grill-me`, including the Question Triage grid and decision log.
- Preserve Matt's useful vocabulary around deep modules, interfaces, locality, leverage, and deletion tests.

### `klimkit-impeccable`

- Audit the bundled scripts before allowing them as default workflow steps, especially local server/live-edit paths and tokenized localhost endpoints.
- Convert `.claude/skills/...` path assumptions to skill-relative or repo-relative paths.
- Decide whether `.impeccable/` state should be preserved, moved under `.klimkit/<operator>/`, or treated as tool-local state.
- Link live visual iteration to `klimkit-agent-browser` and proof handoff to `klimkit-walkthrough`.
- Specifically review its `child_process` calls, local token transport, update-check host, localhost server exposure, Playwright launch flags, and generated screenshot bundle before recommending automatic execution.

### `klimkit-antigravity-security-auditor`

- Merge its strongest checks into `klimkit-security-auditor`: data-flow tracing, IDOR/global-resource checks, privileged service-account bypasses, middleware matcher validation, and SSRF/DNS-rebinding protection.
- Reduce broad tool/vendor lists unless they drive a concrete audit step.
- Require authorized scope, non-intrusive production behavior, and no secret exposure in reports.
- Make output match Klimkit format: severity, evidence, impact, fix, clean areas audited, residual risk.

## Cross-Skill Integration Proposal

- `klimkit-implement` remains the entry point for implementation and requires TDD by default.
- UI work should route through `klimkit-tdd`, `klimkit-agent-browser`, and `klimkit-walkthrough` for behavior plus visual proof.
- Design review should choose one primary design lens per task: `klimkit-impeccable` for high-craft product UI, `klimkit-ui-ux-pro-max` for broad UI/UX heuristics, and `klimkit-web-design-guidelines` for checklist-style web interface review.
- Architecture work should start with `klimkit-improve-codebase-architecture`, then use `klimkit-grill-me` before implementation decisions harden.
- Security review should prefer `klimkit-security-auditor`; `klimkit-antigravity-security-auditor` should become either a reference pack or be merged and removed.
