# Matt Pocock Skills And Klimkit Merge Plan

## Initial Request

Klim first asked to clone and analyze `https://github.com/mattpocock/skills/tree/main`, with the specific question: where is the workflow? The concern was that the repo appears to have skills, but no `AGENTS.md`, so it is not obvious what steps an agent follows when it has a job to do.

Follow-up request: write the analysis into a new `.klimkit` task folder, copy Matt's `skills/` folder into the Klimkit repo, and prepare a deeper plan for merging the best parts of Matt's skills with Klimkit's checklist, proof, reflection, and final-review workflow. Klim also wants the resulting Klimkit skills installable through the Vercel `skills` installer.

## Files Created Or Copied

- Task analysis and plan: `.klimkit/tasks/12-matt-skills-merge-plan/01-a-analysis-and-plan.md`
- Upstream snapshot: `third_party/mattpocock-skills/skills/`
- Upstream license: `third_party/mattpocock-skills/LICENSE`
- Upstream metadata note: `third_party/mattpocock-skills/UPSTREAM.md`

The copied snapshot is from upstream commit `b8be62ffacb0118fa3eaa29a0923c87c8c11985c` and should remain unmodified as reference material.

## External Installer Notes

The current Vercel/skills.sh surface is a repository installer:

- Vercel changelog says the CLI installs packages with `npx skills add <package>` and gives `npx skills add vercel-labs/agent-skills` as the example.
- skills.sh CLI docs say to run `npx skills add <skill-name>` and use owner/repo form such as `vercel-labs/agent-skills`.
- Vercel agent skills docs say a full repo can be installed with `npx skills add <owner/repo>`, and an individual skill from a multi-skill repo with `npx skills add <owner/repo> --skill <skill-name>`.
- Matt's README uses `npx skills@latest add mattpocock/skills`.

Implication for Klimkit: a skills.sh-facing package should expose conventional `skills/**/SKILL.md` content at the repository level, not only nested under `plugins/klimkit/skills/`. The Codex plugin and skills.sh package can share source content, but the install surfaces need to be tested independently.

## What Matt's Repo Actually Provides

Matt's repo does not contain a global always-on workflow equivalent to Klimkit's home-level `AGENTS.md`.

Observed structure:

- `.claude-plugin/plugin.json` lists installable skill directories.
- `CLAUDE.md` only documents how to maintain Matt's skills repo.
- There is no repo-level `AGENTS.md`.
- `setup-matt-pocock-skills` creates an `## Agent skills` block in a target repo's `CLAUDE.md` or `AGENTS.md`, plus `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and `docs/agents/domain.md`.
- `docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md` distinguishes hard-dependency skills from soft-dependency skills.

Matt's workflow is therefore compositional:

1. Install skills with skills.sh.
2. Run `/setup-matt-pocock-skills` once in the target repo.
3. Use the appropriate skill for the job:
   - `/grill-with-docs` to align on terminology and decisions.
   - `/to-prd` to turn context into a PRD.
   - `/to-issues` to slice a plan into independently grabbable issues.
   - `/triage` to move issues through triage roles and write agent briefs.
   - `/tdd` to implement with red-green-refactor.
   - `/diagnose` to debug through feedback-loop-first diagnosis.
   - `/improve-codebase-architecture` to find deepening opportunities.
   - `/prototype` to build throwaway learning artifacts.

There is no mandatory global final gate. Each skill carries a local workflow, and the human chooses which skill to invoke.

## Difference From Klimkit

Klimkit's current workflow is a global completion contract:

- Intake reads repo instructions, `.klimkit` memory/log/task context, and relevant docs.
- Implementation work requires a checklister acceptance checklist before coding.
- Work is scoped, verified, and recorded in task proof.
- Non-trivial implementation runs reflection after verification.
- Final handoff requires final-review passes before completion claims.
- Evidence lives under `.klimkit/tasks/`, `.klimkit/reports/`, `.klimkit/log.md`, and `.klimkit/reflection.md`.

Matt's workflow is a skill toolbox:

- Skills are small, sharp, and task-triggered.
- A setup skill adds only the repo-specific context that other skills need.
- Issue tracker and domain glossary docs are first-class.
- TDD and diagnosis skills are stronger than Klimkit's current generic workflow wording.
- Triage creates durable agent briefs, but not Klimkit-style task proof.
- There is less ceremony, but also less enforced completion discipline.

## What Klimkit Should Take From Matt

Adopt these ideas:

- Skill descriptions should be strong enough to route the agent into the right workflow without global instructions.
- Per-repo setup should record issue tracker, triage labels, and domain docs in a small, editable config area.
- `CONTEXT.md` and `docs/adr/` should be explicit inputs to planning, diagnosis, TDD, architecture review, and issue creation.
- The `diagnose` feedback-loop-first phases are excellent and should be integrated almost directly.
- The `tdd` vertical-slice red-green-refactor guidance is better than generic "write tests".
- `to-issues` tracer-bullet slicing is useful for converting plans into AFK-ready work.
- `triage` agent briefs are a good public issue-facing companion to Klimkit's private/repo-local task proof.
- `prototype` clearly separates throwaway learning from production claims.

Avoid importing these as-is:

- Do not make `CLAUDE.md` the primary Klimkit surface; Klimkit uses Codex, plugins, and `.klimkit` artifacts.
- Do not rely on optional skill invocation alone for completion discipline.
- Do not copy personal, deprecated, or in-progress skills into the default Klimkit package.
- Do not let issue tracker state replace `.klimkit/tasks/` proof.
- Do not put broad harness guidance into root reference files that Codex does not actually load.

## Proposed Merge Architecture

Use three layers.

### Layer 1: Klimkit Workflow Kernel

Keep `klimkit-workflow` as the always-recommended entry point for implementation and proof discipline.

It should define the invariant gates:

1. Intake.
2. Acceptance checklist.
3. Plan/delegate.
4. Implement with a task-specific method.
5. Verify.
6. Proof.
7. Reflection.
8. Final review.
9. Handoff.

This skill should remain concise and refer to one-level-deep references for artifact layout, repo-managed mode, and skill composition.

### Layer 2: Task-Specific Expert Skills

Create Klimkit-adapted versions of Matt's best engineering skills. Recommended initial set:

- `klimkit-diagnose`
- `klimkit-tdd`
- `klimkit-grill-with-docs`
- `klimkit-to-prd`
- `klimkit-to-issues`
- `klimkit-triage`
- `klimkit-improve-codebase-architecture`
- `klimkit-prototype`
- `klimkit-handoff`

Use `klimkit-` prefixes for adapted variants so users can install Matt's originals and Klimkit's variants side by side without name collisions.

Each adapted skill should keep Matt's task-specific process, but add a small Klimkit wrapper:

- For implementation work, create or update a `.klimkit/tasks/<feature>/` checklist before code changes.
- Use `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/` when present.
- Record changed files, commands, outputs, skipped checks, and residual risk in task proof.
- For non-trivial work, append reflection before final handoff.
- For release or user-visible claims, do not claim publication/live cache state without concrete proof.

The wrapper must be short. Detailed artifact rules should live in skill-local `references/` files or the `klimkit-workflow` references.

### Layer 3: Repo Setup Skill

Create `klimkit-setup-skills` from Matt's setup skill, adapted for Klimkit.

It should write a small `## Klimkit skills` block into the target repo's existing `AGENTS.md` or equivalent, and create:

- `.klimkit/skills/issue-tracker.md` or `docs/agents/issue-tracker.md`
- `.klimkit/skills/triage-labels.md` or `docs/agents/triage-labels.md`
- `.klimkit/skills/domain.md` or `docs/agents/domain.md`

Recommendation: keep public, shareable repo instructions in `docs/agents/`; keep task evidence in `.klimkit/`. That preserves Matt's readable config docs without turning `.klimkit` into a dumping ground for stable docs.

## Mapping Matt Concepts To Klimkit

| Matt concept | Klimkit equivalent | Merge decision |
| --- | --- | --- |
| `setup-matt-pocock-skills` | setup skill plus repo-local skill config | Adapt into `klimkit-setup-skills`. |
| `CONTEXT.md` | project language docs already mentioned in Klimkit AGENTS | Keep and make more prominent. |
| `docs/adr/` | decision docs already mentioned in Klimkit AGENTS | Keep and cross-link from adapted skills. |
| Issue tracker | optional public work queue | Support GitHub/local first; do not require for all tasks. |
| Triage labels | issue workflow state | Map to labels when issue tracker exists; otherwise map to `.klimkit/tasks` status. |
| Agent brief | public issue contract | Use as issue-facing spec; pair with Klimkit checklist/proof. |
| PRD | issue-tracker planning artifact | Keep for larger tasks; store linked proof in `.klimkit/tasks`. |
| TDD red-green-refactor | implementation method | Embed inside Klimkit checklist/proof gates. |
| Diagnose phases | debugging method | Embed inside Klimkit checklist/proof gates. |
| Architecture review HTML report | proof/report artifact | Store generated report under `.klimkit/reports/` for Klimkit, not OS temp, when it is part of task proof. |
| Prototype | throwaway learning artifact | Keep, but require explicit delete/absorb/proof outcome. |

## Packaging Plan For Vercel skills.sh

Goal: users can run:

```bash
npx skills add klimentij/klimkit
```

and optionally:

```bash
npx skills add klimentij/klimkit --skill klimkit-tdd
```

Recommended repo layout:

```text
skills/
  engineering/
    klimkit-diagnose/
    klimkit-tdd/
    klimkit-grill-with-docs/
    klimkit-to-prd/
    klimkit-to-issues/
    klimkit-triage/
    klimkit-improve-codebase-architecture/
    klimkit-prototype/
  productivity/
    klimkit-handoff/
    klimkit-workflow/
plugins/
  klimkit/
    .codex-plugin/plugin.json
    skills/
      ...
third_party/
  mattpocock-skills/
    skills/
    LICENSE
    UPSTREAM.md
```

Open design choice: avoid hand-maintaining two copies of each Klimkit-adapted skill.

Best option:

- Create a source-of-truth directory, for example `skills/`.
- Add a deterministic sync script that copies or flattens selected skills into `plugins/klimkit/skills/` for the Codex plugin.
- Tests assert that the Codex plugin and skills.sh package expose the same intended skill set.

Alternative:

- Keep Codex plugin as source of truth and generate root `skills/` from it.
- This is weaker if skills.sh expects nested category organization and Codex plugin prefers flat names.

## Skill Adaptation Rules

For each adapted Matt skill:

1. Keep frontmatter to `name` and `description` unless the target installer requires otherwise.
2. Make the description a concise trigger paragraph with explicit "Use when..." guidance.
3. Add `agents/openai.yaml` for Codex UI metadata.
4. Preserve Matt's strongest domain-specific workflow.
5. Add only the minimum Klimkit wrapper needed for checklist, proof, reflection, and final review.
6. Move long examples and templates into skill-local `references/`.
7. Keep references one level deep.
8. Include Matt attribution in each adapted skill reference or package notice if substantial text is reused.
9. Validate both as skills and as Codex plugin contents.

## Recommended First Implementation Wave

Do not port everything in one pass. Start with the skills that directly improve Klimkit's implementation loop.

Wave 1:

- `klimkit-diagnose`
- `klimkit-tdd`
- `klimkit-grill-with-docs`
- `klimkit-workflow` updates to explain skill composition
- skills.sh package skeleton at repo root

Wave 2:

- `klimkit-to-prd`
- `klimkit-to-issues`
- `klimkit-triage`
- `klimkit-setup-skills`

Wave 3:

- `klimkit-improve-codebase-architecture`
- `klimkit-prototype`
- `klimkit-handoff`

Skip by default:

- Matt's `personal/`
- Matt's `deprecated/`
- Matt's `in-progress/`
- Misc skills unless Klim explicitly wants them.

## Validation Plan

Add or extend tests to assert:

- Root `skills/**/SKILL.md` exists for every skills.sh-exported skill.
- Plugin `plugins/klimkit/skills/*/SKILL.md` exists for every Codex-exported skill.
- Frontmatter uses allowed keys and strong descriptions.
- `agents/openai.yaml` exists for Codex-exposed skills.
- No copied upstream snapshot file is treated as an installable Klimkit skill.
- `third_party/mattpocock-skills` keeps MIT license and upstream metadata.
- README install docs include `npx skills add klimentij/klimkit` and `--skill`.
- Codex plugin install docs remain separate from skills.sh docs.
- Adapted skills contain Klimkit gates without duplicating the full AGENTS workflow in every skill.

Manual checks:

- Run skill quick validation over root exported skills.
- Run Codex plugin validation.
- Run existing unit tests.
- Test `npx skills add` against a branch or local repo before claiming skills.sh installability.

## Open Questions For Klim

1. Should adapted skill names use `klimkit-` prefixes, or should they keep Matt's original names where the behavior is similar?
2. Should `.klimkit/tasks` remain the canonical work ledger even when GitHub Issues are used, or should issue-first workflows become primary for public/open-source projects?
3. For skills.sh, should the root `skills/` package install all recommended skills by default, or should README recommend installing only `klimkit-workflow`, `klimkit-tdd`, and `klimkit-diagnose` first?
4. Should architecture reports from `klimkit-improve-codebase-architecture` go into `.klimkit/reports/` by default, even though Matt writes them to OS temp?
5. Do we want a sync script that makes `skills/` the source of truth and regenerates `plugins/klimkit/skills/`, or should the Codex plugin remain hand-authored?

## Proposed Decision

Use Klimkit as the workflow spine and Matt's skills as task-specific muscles.

The merged system should not become a giant always-loaded manual. The right shape is:

- A small `klimkit-workflow` skill that defines completion gates.
- Focused adapted skills for diagnosis, TDD, planning, triage, and architecture.
- A setup skill that writes small repo-local context docs.
- A root `skills/` package for Vercel skills.sh.
- A Codex plugin package generated from the same adapted skill source.
- Tests that prevent the install surfaces from drifting.

This preserves Matt's composability while keeping Klimkit's proof discipline.
