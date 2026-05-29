# Third-Party Skill Imports: Checklist And Proof

## Acceptance Checklist

- [x] `klimkit-implement` makes TDD the default required style for behavior-changing implementation and routes the actual loop through `klimkit-tdd`.
- [x] `klimkit-final-reviewer` and `klimkit-implement` prefer one or two scoped fresh final reviewers, with inline fallback when subagents are unavailable or forbidden.
- [x] `klimkit-setup` checks project, home/global, and contextual `AGENTS.md` files for contradictions with installed Klimkit skills and proposes focused edits.
- [x] Requested third-party skills are imported with `klimkit-` names where redistribution looked acceptable.
- [x] Unsafe or legally unclear requested imports are blocked and documented instead of redistributed.
- [x] Imported skills keep upstream/source/license notes and avoid deeper Klimkit-style rewrites until Klim reviews the proposal.
- [x] README, smoke expectations, and root skill tests include the imported candidate skills.
- [x] Validation covers unit tests, skill quick validation, whitespace checks, and Vercel Skills CLI listing.

## Verification

- `python3 -m unittest discover -s tests -q` passed.
- `for d in skills/*; do python3 /home/ubuntu/sellify-agent-research/repos/codex/codex-rs/skills/src/assets/samples/skill-creator/scripts/quick_validate.py "$d" || exit 1; done` passed.
- `git diff --check` passed.
- `npx skills add ./ --list` passed and listed 19 skills.

## Security And Licensing Notes

- `roin-orca/skills --skill simple` was not imported because no license was found and the skill contains hostile prompt text instructing agents to skip scanning/tests plus an XSS-looking Markdown image payload.
- Imported candidate skills preserve upstream source and license notes in `references/upstream.md` plus license reference files where available.
- `klimkit-impeccable` and `klimkit-ui-ux-pro-max` include bundled scripts; these are imported as candidate resources and should receive deeper workflow/security review before Klimkit makes them default orchestration paths.
- A static keyword safety scan found expected but sensitive surfaces in `klimkit-impeccable`: `child_process`, localhost server/token transport, an update-check host, browser automation, and Playwright launch flags. These are documented for the next hardening pass rather than hidden.

## Inline Final Review

Subagents were not used because Klim requested a simple flow without subagents. Inline review result: READY FOR USER.

The implementation matches the request: TDD is now a contract in `klimkit-implement`, final-review fan-out is reduced with fallback, setup analyzes `AGENTS.md` contradictions, safe third-party candidates are imported with `klimkit-` prefixes, and a separate proposal document captures the requested future edits without applying those deeper edits yet.
