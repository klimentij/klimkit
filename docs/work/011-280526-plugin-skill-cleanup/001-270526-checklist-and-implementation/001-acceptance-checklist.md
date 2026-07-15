# Plugin Skill Cleanup Acceptance Checklist

Task: recreate and improve the Klimkit Codex plugin skills on branch `codex-plugin-skill-cleanup` according to `skill-creator` best practices, without editing production code before this checklist.

## Current Status

All implementation, proof, validation, and reflection items are complete. The plugin install/cache validation item is not triggered because this branch did not change the plugin manifest version, marketplace source, or installed cache behavior; the proof explicitly avoids claiming these source changes are live in `~/.codex/plugins/cache`. Final Review Gate is pending.

## Acceptance Checklist

### Scope And Source Boundaries

- [ ] The implementation is limited to the Klimkit Codex plugin skill package, its plugin-facing docs, and tests/validation that protect that package; unrelated `src/`, service, Switchboard, installer, or production runtime behavior is unchanged.
- [ ] The implementer reads the current task note, repository `AGENTS.md`, `.klimkit/memory.md`, `.klimkit/log.md`, `.klimkit/reflection.md`, the `skill-creator` guidance, and the current plugin files under `plugins/klimkit/` before editing.
- [ ] The implementer records any intentional deviation from `skill-creator` guidance in task proof, with the reason and the exact affected skill path.

### Skill Structure And Trigger Quality

- [ ] Every installable skill under `plugins/klimkit/skills/*/` has a valid `SKILL.md` whose YAML frontmatter contains only `name` and `description`, with `name` matching the skill folder slug.
- [ ] Every frontmatter `description` is a concise paragraph, stays within the existing Codex CLI description limit, and clearly states both what the skill does and when Codex should invoke it.
- [ ] Invocation guidance is present in frontmatter descriptions rather than depending on body-only "when to use" sections.
- [ ] Each `SKILL.md` body starts with a proper human-facing title, such as `# Klimkit Workflow`, `# Harness Tuning`, `# Frontend Design`, `# Grill Me`, and `# Agent Browser`, not a raw folder slug when a title would be better.
- [ ] Each skill body is lean, directly usable by a future Codex agent, and free of stale setup history, process notes, generated placeholders, generic README-style prose, and duplicated reference content.
- [ ] Detailed workflow material that is still useful for the plugin is moved into the owning skill body or one-level-deep files under that skill's `references/` directory, with every reference file linked directly from the owning `SKILL.md`.
- [ ] No skill depends on the plugin root `reference/AGENTS.md` as its primary workflow instructions.

### Klimkit Workflow Skill Content

- [ ] `plugins/klimkit/skills/klimkit-workflow/` is the plugin-first home for Klimkit workflow guidance: intake, acceptance checklist, scoped implementation, verification, task proof, reflection, final review, and handoff expectations are usable from the skill itself and/or its own references.
- [ ] The workflow skill clearly distinguishes the public plugin path from the repo-managed `kk apply` path, including that machine-level Codex config, hooks, subagents, Switchboard, code-server profile projection, Tailscale Serve, and service restarts are not installed by the plugin alone.
- [ ] The workflow skill preserves the current solo `.klimkit/` evidence layout for this repo while still explaining team-workflow attribution only where it is necessary and not stale.
- [ ] The workflow skill gives enough practical guidance for task notes, proof, reflection, and final review that removing stale root reference packaging does not reduce plugin usability.

### UI Metadata

- [ ] Every installable skill under `plugins/klimkit/skills/*/` has `agents/openai.yaml`.
- [ ] Each `agents/openai.yaml` uses quoted string values and includes `interface.display_name`, `interface.short_description`, and `interface.default_prompt`.
- [ ] Each `display_name` is a proper human-facing title, not a lowercase slug.
- [ ] Each `short_description` is a concise UI blurb suitable for quick scanning, roughly within the 25-64 character guidance from `skill-creator`.
- [ ] Each `default_prompt` is a short realistic invocation and explicitly mentions the skill with `$skill-name`.
- [ ] Optional UI fields such as icons, brand colors, dependencies, or policy are absent unless they are intentionally supported and validated for that skill.

### Root Reference And Plugin Packaging Cleanup

- [ ] The stale plugin root `plugins/klimkit/reference/AGENTS.md` is removed from the installable plugin package, or the implementer documents a concrete, current reason it remains and proves no skill relies on it as workflow source.
- [ ] Any retained files under `plugins/klimkit/reference/` are narrow, current, public-safe plugin references; stale broad workflow packaging and clutter are removed.
- [ ] `plugins/klimkit/reference/README.md`, if retained, accurately documents only the files that still exist and does not advertise root `AGENTS.md` as the plugin workflow surface.
- [ ] `plugins/klimkit/README.md` accurately describes the new plugin skill structure, skill-owned references, install/upgrade commands, and the boundary between installable plugin skills and repo-managed harness projection.
- [ ] `plugins/klimkit/.codex-plugin/plugin.json` still points at `./skills/`, remains public-safe, and its interface text still matches the plugin's actual installed surfaces.
- [ ] The plugin package contains no private/local tokens, generated placeholders, stale operator names, or references to unavailable machine-local paths.

### Tests And Validation

- [ ] `tests/test_codex_pack_validation.py` is updated to assert the new plugin structure, including skill-owned workflow content, absence or justified retention of root reference packaging, public-safe plugin content, and required `agents/openai.yaml` metadata for every plugin skill.
- [ ] Any docs/static tests that mention plugin surfaces or root references are updated to match the new public plugin contract.
- [ ] Skill validation is run for every plugin skill with `<codex-home>/skills/.system/skill-creator/scripts/quick_validate.py plugins/klimkit/skills/<skill-name>` or an equivalent validator, and all results pass.
- [ ] `uv run python -m unittest tests.test_codex_pack_validation -q` passes.
- [ ] `uv run python -m unittest tests.test_docs_static -q` passes.
- [ ] `uv run python -m unittest tests.test_klimkit_install -q` passes unless the implementer records a concrete reason it is unaffected and unavailable or intentionally skipped.
- [ ] `uv run python -m unittest discover -q` passes, or any failure is proven unrelated with exact failing test names and supporting evidence.
- [ ] If plugin manifest version, marketplace behavior, or installation cache behavior changes, the implementer also validates the relevant Codex plugin install/upgrade path and records the exact commands and observed version/cache evidence.

### Task Proof, Log, And Release Boundary

- [ ] A task proof note is written under `.klimkit/tasks/11-plugin-skill-cleanup/` with changed files, source boundary, validation commands, command outcomes, skipped checks, and any residual risk.
- [ ] `.klimkit/log.md` receives an ISO-timestamped entry summarizing the completed plugin skill cleanup and verification.
- [ ] No claim is made that plugin changes are live in a user's installed Codex plugin cache unless that cache was actually refreshed and verified.
- [ ] No claim is made that changes are released unless they have landed on `main` and the repository-local release rule has been satisfied with a latest GitHub release for that commit.

### Reflection Gate

- [ ] Before final review, the implementer reads `.klimkit/reflection.md` and relevant prior task artifacts, especially the plugin-first task under `.klimkit/tasks/10-codex-plugin-first/` and recent plugin/cache reflection entries.
- [ ] A fresh reflection session is appended to `.klimkit/reflection.md` with a full UTC timestamp heading.
- [ ] The reflection entry uses `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` by default, with up to ten named sections only if the synthesis needs them.
- [ ] The reflection connects the current skill cleanup to the broader plugin-first distribution boundary, skill best-practice guidance, and prior plugin cache/release evidence without rewriting older reflection entries.
- [ ] After reading the new reflection entry, the implementer reconsiders the implementation, tests, proof, and final response; any material gap found by reflection is fixed and impacted validation is rerun before final review.

### Final Review Gate

- [ ] The implementer drafts the exact final response before final review.
- [ ] Three `final_reviewer` subagents run in parallel and receive the original request or this checklist, changed files, verification evidence, task proof path, reflection entry, and exact draft response.
- [ ] All three final reviewers return PASS / READY FOR USER before any completion claim is sent to Klim.
- [ ] The final response names what changed, which validation passed, any unavailable checks or residual risk, and how Klim can inspect the plugin skill cleanup locally.
