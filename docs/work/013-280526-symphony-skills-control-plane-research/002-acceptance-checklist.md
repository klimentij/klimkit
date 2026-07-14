# Symphony Skills Control Plane Research Acceptance Checklist

Task: planning-only research for comparing local OpenAI Symphony, prior Matt Pocock skills analysis, Klimkit workflow, Klim's GitHub tracker/control-plane versus full Symphony comparison, and private candidate skills, without implementing adapted skills yet.

## Acceptance Checklist

### Scope And Privacy Boundaries

- [ ] The work remains planning/research only: no adapted Klimkit skills are implemented, no production code is changed, and no new installable skill content is added under tracked public paths such as `skills/`, `packs/codex/skills/`, `plugins/klimkit/skills/`, or `third_party/`.
- [ ] Public task artifacts under `.klimkit/tasks/13-symphony-skills-control-plane-research/`, the final response, and `.klimkit/log.md` do not mention the private repository name, private remote URL, private organization/account, private branch name if identifying, private file paths outside this machine, or copied private source text.
- [ ] Private candidate-skill copies, if needed for inspection, are stored only under an ignored private/local path such as `.klimkit/local/13-symphony-skills-control-plane-research/`, or another task-local path proven ignored by `git check-ignore -v`, before any private files are copied there.
- [ ] No private code, private prompts, private config, secrets, tokens, or identifying repo metadata are copied into tracked public paths unless Klim gives explicit approval during the task and that approval is recorded.
- [ ] Public analysis may summarize private candidate-skill patterns at a conceptual level, but does not quote or paraphrase distinctive private implementation text closely enough to reconstruct it.
- [ ] Source attribution is preserved for OpenAI Symphony and Matt Pocock's third-party skills, including source paths, upstream repository names, license or snapshot notes where available, and the inspected local commit or branch state when discoverable.
- [ ] Any private source attribution required for the agent's own audit trail is recorded only in the ignored private/local task path, not in public docs.

### Required Task Artifacts

- [ ] A sanitized human-request note exists with an `-h-` filename in `.klimkit/tasks/13-symphony-skills-control-plane-research/` and excludes the private repository name and other private identifiers.
- [ ] A deep analysis note exists under `.klimkit/tasks/13-symphony-skills-control-plane-research/` with an `-a-` filename and includes source manifest, analysis, tradeoffs, recommendation, risks, and explicit non-goals.
- [ ] A one-page executive brief exists under `.klimkit/tasks/13-symphony-skills-control-plane-research/` with an `-a-` filename, is written for fast human decision-making, and stays under 1,000 words.
- [ ] Any private inspection notes, raw candidate-skill copies, branch identifiers, or source manifests that would reveal the private repository are stored only under the ignored private/local path and are not required to be committed.
- [ ] `.klimkit/log.md` receives an ISO-timestamped entry summarizing the completed research artifacts without naming the private repository.

### Source Intake

- [ ] The researcher reads repository instructions, `.klimkit/memory.md`, `.klimkit/log.md`, the sanitized request note, this acceptance checklist, and relevant prior task artifacts before writing the analysis.
- [ ] The researcher reads the prior Symphony task artifacts, especially `.klimkit/tasks/07-symphony-reflection/01-a-research-reflection.md` and `.klimkit/tasks/07-symphony-reflection/02-a-expanded-strategy.md`, and distinguishes reused prior conclusions from new analysis.
- [ ] The researcher reads the prior Matt Pocock skills analysis at `.klimkit/tasks/12-matt-skills-merge-plan/01-a-analysis-and-plan.md` and relevant copied third-party Matt skills metadata under `third_party/mattpocock-skills/`.
- [ ] The researcher inspects local OpenAI Symphony at `<symphony-repo>`, records the inspected branch/commit/status when discoverable, and reads enough of its README/spec/workflow/skills/implementation files to ground the comparison.
- [ ] The researcher reads current Klimkit workflow surfaces relevant to this comparison, including the active Klimkit workflow skill and/or Codex harness workflow docs, plus any current package/distribution notes needed to avoid stale assumptions.
- [ ] The researcher incorporates Klim's provided GitHub tracker/control-plane versus full Symphony comparison. If that comparison is not available in the visible task context, the researcher stops and asks Klim for it instead of inventing it.
- [ ] The researcher inspects the private candidate-skills branch only within the privacy boundary above, records private branch/source details only in ignored local notes, and extracts only public-safe conceptual findings into public analysis.

### Analysis Content

- [ ] The deep analysis clearly compares at least three options: GitHub tracker/control-plane only, a fuller Symphony-style orchestrator, and a staged or hybrid Klimkit path.
- [ ] The analysis explains how each option would interact with `.klimkit/tasks`, proof reports, memory/log/reflection, Switchboard, worktrees, Codex sessions, GitHub Issues/Projects, and future Linear compatibility.
- [ ] The analysis maps relevant Symphony concepts into Klimkit terms, including work items, tracker adapters, scheduler/runner responsibilities, workpad/status updates, dependency blocking, retries, workspace isolation, and human-review handoff.
- [ ] The analysis maps relevant Matt skills concepts into Klimkit terms, including setup, diagnosis, TDD, PRD/issues/triage, prototype boundaries, and how task-specific skills should compose with Klimkit's checklist/proof/reflection/final-review gates.
- [ ] The analysis identifies candidate skills or skill patterns from the private branch using neutral labels, explains why each is or is not suitable for Klimkit adaptation, and avoids naming the private source.
- [ ] The analysis separates immediate recommendations from later possibilities, and explicitly states that no adapted skill implementation is part of this task.
- [ ] The analysis includes concrete next-step recommendations for any future implementation task, including what should be checked or approved before copying, adapting, or publishing any private-derived skill content.
- [ ] The one-page executive brief gives Klim a concise decision summary: recommended direction, why it beats alternatives, major privacy/IP risks, first implementation wave if approved later, and open questions.

### Verification

- [ ] `git check-ignore -v` proves the private/local path used for copied private candidate-skill material is ignored before any private files are copied there.
- [ ] `git status --short` is reviewed to confirm the only tracked/public files changed by this planning task are expected task artifacts and `.klimkit/log.md`, with no accidental skill implementation or private-source files staged in public paths.
- [ ] `git diff --check` passes for the tracked planning artifacts.
- [ ] A privacy grep or equivalent manual check is run over public task artifacts and `.klimkit/log.md` using the known private identifiers, and no private repository name, private branch identifier, private URL, private path, or copied private text is present.
- [ ] The public analysis and executive brief are reviewed for attribution: OpenAI Symphony and Matt Pocock skills are credited, while the private candidate source is described only with neutral, non-identifying language.
- [ ] No UI proof report, browser video, backend tests, or production test suite is required because this is planning-only and has no UI/backend/runtime behavior change; if implementation scope is added later, a new checklist must add the relevant verification gates.

### Reflection And Final Review

- [ ] Because this is a non-trivial cross-task research/planning task, the researcher reads `.klimkit/reflection.md` after verification and before final review.
- [ ] If the research produces durable cross-task workflow learning, a full UTC-timestamped reflection session is appended to `.klimkit/reflection.md` using `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` by default; otherwise the task note records why reflection is not applicable despite the non-code scope.
- [ ] After the reflection decision, the researcher reconsiders the analysis, brief, privacy checks, and final response; any material gap found is fixed and impacted verification is rerun.
- [ ] The exact final response is drafted before final review and does not mention the private repository name or other private identifiers.
- [ ] Three `final_reviewer` subagents run in parallel and receive the original request or sanitized request note, this acceptance checklist, public changed files, private-boundary summary without private names, verification evidence, reflection entry or explicit not-applicable note, and the exact draft response.
- [ ] All three final reviewers return PASS / READY FOR USER before the research task is claimed complete.
