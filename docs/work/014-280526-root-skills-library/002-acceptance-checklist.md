# Root Skills Library Acceptance Checklist

All items are blocking unless Klim explicitly changes scope.

## Acceptance Checklist

- [x] Root `skills/` is the primary product surface and is flat as `skills/<skill-name>/SKILL.md`.
- [x] The first-wave skills are limited to workflow, setup, diagnose, TDD, report-server, walkthrough, and worktree-stack.
- [x] Tracker, board, triage, and control-plane skills are removed from the first-wave package.
- [x] Each root skill has required `SKILL.md` frontmatter, matching folder/frontmatter names, concise routing descriptions, and optional `references/` or `scripts/` only where useful.
- [x] `klimkit-setup` resolves operator context by checking current request, current repo `.klimkit`, home Klimkit repo `.klimkit`, and user-global config before asking.
- [x] `klimkit-setup` asks the user to clarify among inferred operator folders when discovery is ambiguous and accepts a custom operator name.
- [x] `klimkit-setup` creates `.klimkit/<operator>/` skeletons in the current repo and, for a new operator, in the home Klimkit repo when present.
- [x] `klimkit-setup` proposes two or three agent personality options, accepts a custom name and one-sentence description, and records the choice in config.
- [x] Project-local state uses `.klimkit/<operator>/config.toml`; optional user-global defaults use `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
- [x] Other Klimkit skills route missing or ambiguous `.klimkit/<operator>/` context through `klimkit-setup`.
- [x] The README positions Vercel Skills CLI as the default install/update path and documents operator setup.
- [x] Everything outside root `skills/` is deprecated or moved under `deprecated/`, including the old runtime, `kk`, `klimkit`, `install.sh`, packs, templates, Bash helpers, tests, and plugin prototype.
- [x] README legacy links point to `deprecated/` paths so users can still find Switchboard and the old tools.
- [x] A root skills test validates the expected first-wave skill set, operator/personality setup guidance, README legacy links, and absence of deferred tracker skill names from public skills/README text.
- [x] `npx skills add ./ --list` lists only the intended first-wave skills.
- [x] Root skill validation, unit tests, privacy/path greps, and `git diff --check` pass or are recorded with exact limitations.
- [x] The proof note and `.klimkit/log.md` are updated.
- [x] No subagents are used after Klim's explicit no-subagents instruction.
