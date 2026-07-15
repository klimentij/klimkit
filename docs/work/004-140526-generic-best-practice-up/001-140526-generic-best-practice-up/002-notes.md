# Generic Best-Practice Harness Update

## Review Status

Ready for Klim review. I changed source pack files only, did not commit, did not
push, and did not run `kk apply`, because the request asks for review of the
changes and this analysis first.

Validation run:

```text
uv run python -m unittest tests.test_codex_pack_validation -q
Ran 10 tests in 0.022s
OK

git diff --check
passed
```

## Source Boundary

Read local sources:

- `.klimkit/tasks/04-generic-best-practice-up/01-h-in.md`
- `.klimkit/tasks/04-generic-best-practice-up/image.png`
- `.klimkit/memory.md`
- `.klimkit/log.md`
- `.klimkit/reflection.md`
- `packs/codex/AGENTS.md`
- all `packs/codex/agents/*.toml`
- all first-level `packs/codex/skills/*/SKILL.md`
- `tests/test_codex_pack_validation.py`

Read external sources:

- GitHub page: `https://github.com/mattpocock/skills`
- Local analysis clone: `/tmp/mattpocock-skills`
- Clone commit:
  `e74f0061bb67222181640effa98c675bdb2fdaa7`
- Important files read from that repo: `README.md`, `CLAUDE.md`,
  `CONTEXT.md`, `.claude-plugin/plugin.json`, `docs/adr/0001-...`,
  and representative engineering/productivity/misc `SKILL.md` files.

I treated the article's claimed numbers as context, not as facts to encode into
Klimkit. The useful part is the failure-mode taxonomy, not the percentages.

## Acceptance Checklist

- [x] Exclude token-budget rules.
- [x] Integrate the 12-rule material into `packs/codex/AGENTS.md` instead of
      pasting a raw template block.
- [x] Integrate the image's no-hacks / robust design / fail-loud guidance without
      duplicating the existing quality section.
- [x] Audit subagents and skills for where the guidance should live.
- [x] Update related subagents where the guidance is enforceable.
- [x] Update harness-tuning so future pack changes synthesize external advice
      instead of template-pasting.
- [x] Add validation coverage for the new guidance.
- [x] Deeply analyze `mattpocock/skills` and propose up to 10 Klimkit takeaways.
- [x] Stop before commit/apply/push so Klim can review the changes first.

## What Changed

### `packs/codex/AGENTS.md`

Integrated missing behavioral rules into existing sections:

- Intake now mentions project language and decision docs such as `CONTEXT.md`,
  `CONTEXT-MAP.md`, and `docs/adr/` when relevant.
- Plan/delegate now warns against agent fights by requiring distinct questions or
  disjoint write scopes for parallel agents.
- Implementation now distinguishes production work from throwaway prototypes.
- Shared skills now include a conflict-resolution rule for skill, agent, hook,
  and repository instruction conflicts.
- Engineering quality rules now sharpen:
  - explicit "push back when simpler", "stop when confused", and "loop until
    verified" phrasing from the Karpathy-style rules;
  - success criteria over procedural steps;
  - no features beyond the request;
  - no adjacent code/comment/format cleanup unless required;
  - project language and ADR awareness;
  - no fake support;
  - hook/projection/service/tool failures as first-class task evidence.

### Subagents

- `checklister`: checklists now prefer success criteria and scope boundaries over
  procedural instructions, and prototype tasks must identify the prototype
  question, throwaway location, run command, and deletion/absorption decision.
- `code_explorer`: now uses project language/ADRs when present and surfaces
  contradictory patterns instead of blending them.
- `code_reviewer`: now explicitly flags hacks, fake support, conflict-averaged
  patterns, prototype leakage into production, deterministic decisions delegated
  to model calls, and implementation-coupled tests.
- `debugger`: now stops rather than speculates when no credible feedback loop
  can be built.
- `final_reviewer`: now verifies that skipped checks, unavailable checks,
  projection/service failures, prototypes, and research-only work are reported
  accurately.
- `test_writer`: now prefers behavior tests through public interfaces and
  one-vertical-slice-at-a-time test development.

### Skills

- `harness-tuning`: now explicitly says external guidance must be synthesized
  into the existing pack, with a scan for duplicates/conflicts across
  `AGENTS.md`, subagents, skills, and tests.

I did not change `frontend-design`, `agent-browser`, `manual_tester`,
`security_auditor`, `web_research`, or `reflector` in this pass. Their existing
scope-specific instructions already cover the relevant behavior, or the requested
generic guidance is better enforced from `AGENTS.md` plus the subagents above.

### Tests

`tests/test_codex_pack_validation.py` now asserts:

- the newly integrated AGENTS guidance exists;
- subagents enforce success criteria, prototype handling, contradictory-pattern
  surfacing, no fake support, feedback-loop discipline, final handoff honesty,
  public-interface tests, vertical slices, and synthesized pack tuning.

## Integration Analysis

The pack already had most of the 12-rule material before this task. The safe move
was not to paste another rules section. Pasting would create two sources of truth:
one abstract template and one Klimkit-specific workflow. That would make
conflicts more likely, especially around final review, reflection, reports,
Switchboard/Tailscale proof URLs, and generated projections.

What was missing or weak:

- **Literal coverage of the Karpathy-style baseline:** after re-checking, I made
  the main `AGENTS.md` wording more explicit for "push back when simpler", "stop
  when confused", "loop until verified", "no features beyond asked", and "do not
  improve adjacent code/comments/formatting". These were mostly represented
  before, but too implicit for a shared pack.
- **Prototype mode:** the existing simplicity rule could incorrectly reject
  useful throwaway exploration. The pack now says prototypes are allowed, but must
  be marked throwaway, answer a question, avoid production claims, and be deleted
  or absorbed.
- **Agent coordination:** the existing workflow said to prefer small waves of
  subagents, but did not explicitly warn against agent fights and answer
  averaging.
- **Project language:** Matt's repo makes shared language a first-class artifact.
  Klimkit had memory/log/reflection/task notes, but not a general rule to prefer
  domain language and ADRs where present.
- **No fake support:** the image's no-hacks guidance was mostly present, but the
  concrete "do not fake support" wording helps block brittle shims.
- **Tool/projection failures:** Klimkit repeatedly hits live-system edges:
  `kk apply`, systemd user bus, Tailscale Serve, generated projections. Those
  failures need to be classified and reported, not treated as incidental command
  noise.
- **Tests as intent:** the pack already said tests must verify intent, but
  `test_writer` now enforces public-interface tests and vertical slices directly.

## Matt Pocock Skills Compared To Klimkit

Matt's repo is a library of small, composable skills. Its center of gravity is
human-agent alignment inside a project: shared language, ADRs, issue tracker
setup, grilling, TDD, diagnosis, architecture review, prototypes, triage, and
handoffs.

Klimkit is a machine and harness operating system. Its center of gravity is
reproducible VMs, Codex home projection, Switchboard, multi-agent tabs,
Tailscale-served proof reports, reflection, and release-grade final review.

The useful contrast:

- Matt optimizes for reusable per-repo skills that agents can invoke on demand.
- Klimkit optimizes for a default always-on workflow and synced operator
  environment.
- Matt has better domain language and issue lifecycle primitives.
- Klimkit has stronger projection, proof, browser QA, multi-machine, and final
  review machinery.
- Matt's best pieces should mostly be adapted as optional skills or checklist
  modes, not merged wholesale into the global AGENTS file.

## Up To 10 Things Klimkit Should Take Or Adapt

1. **Per-repo domain glossary convention.**
   Add optional `CONTEXT.md` / `CONTEXT-MAP.md` reading rules and maybe a future
   setup skill. This is the strongest direct idea from Matt's repo.

2. **ADR discipline for hard-to-reverse decisions.**
   Klimkit task notes and reflection are good, but ADRs are better for durable
   architectural decisions. Adopt lazily, not for every decision.

   Klim: more on this pls, how exactly 
   

3. **Setup skill for repo-specific agent context.**
   Matt's setup skill asks about issue tracker, label vocabulary, and domain docs.
   Klimkit could add a `project-setup` skill that writes a small
   `.klimkit/project.md` or `docs/agents/*.md` instead of hardcoding assumptions.

4. **Grilling before PRDs or risky plans.**
   The current `checklister` can catch acceptance gaps, but a dedicated
   "grill-with-docs" mode would be better for ambiguous product/architecture
   work before implementation starts.

5. **Diagnose as a stricter debugger loop.**
   Matt's `diagnose` skill is stronger than Klimkit's current debugger prompt
   around building a fast feedback loop first. I partially integrated this by
   requiring the debugger to stop when no credible loop exists.

6. **TDD as a vertical-slice skill.**
   Klimkit has `test_writer`, but Matt's TDD guidance is more precise about
   red-green-refactor, public interfaces, and avoiding horizontal test batches.
   I adapted the core of this into `test_writer`; a fuller `tdd` skill could be
   useful later.

7. **Throwaway prototype workflow.**
   Matt's prototype skill cleanly separates production work from learning
   artifacts. I integrated the global rule and checklist hooks; a future Klimkit
   prototype skill could give runnable terminal/UI prototype conventions.

8. **Architecture deepening / zoom-out.**
   Klimkit has `code_explorer`, but not a focused architecture-improvement skill.
   A future skill could combine Matt's deep-module vocabulary with Klimkit's
   reflection log to find recurring design friction.

9. **Durable agent briefs and vertical-slice issue splitting.**
   Switchboard already runs parallel agents, but the task specs often live in
   ad-hoc notes. Matt's agent-brief and vertical-slice issue format would make
   Switchboard worktrees easier to hand off and less file-path brittle.

10. **Skill registry hygiene and maturity buckets.**
   Matt separates engineering/productivity/misc/personal/in-progress/deprecated
   and validates what is published. Klimkit could add a pack manifest/linter so
   projected skills, README docs, and available skills stay in sync.

Not recommended as a direct default: Matt's git guardrail skill blocks `git push`
and force-like operations. That conflicts with Klimkit's trusted-VM operator
workflow where agents are often explicitly asked to push and release. It could be
useful as an optional non-yolo profile, not in the default pack.

## Files Changed For Review

- `packs/codex/AGENTS.md`
- `packs/codex/agents/checklister.toml`
- `packs/codex/agents/code-explorer.toml`
- `packs/codex/agents/code-reviewer.toml`
- `packs/codex/agents/debugger.toml`
- `packs/codex/agents/final-reviewer.toml`
- `packs/codex/agents/test-writer.toml`
- `packs/codex/skills/harness-tuning/SKILL.md`
- `tests/test_codex_pack_validation.py`
- `.klimkit/tasks/04-generic-best-practice-up/02-a.md`

## Review Notes

- I did not run `kk apply`, because applying projected home-level Codex changes
  before your review would make the unreviewed pack live on this VM.
- I did not commit or release.
- If you approve this direction, the next step is `kk preview`, `kk apply`, a
  reflection entry, final reviewers, then commit/release if you want it synced.
