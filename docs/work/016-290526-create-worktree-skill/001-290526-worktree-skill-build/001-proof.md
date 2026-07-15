# Klimkit Create Worktree Skill Proof

## Request

Rename and replace the worktree-stack skill with a clearer `klimkit-create-worktree` skill. Preserve the proven main/dev/feature worktree flow as a generalized deterministic script that can also create simple worktrees.

## Acceptance Checklist

- [x] Rename the skill to `klimkit-create-worktree`.
- [x] Add a bundled script that creates simple worktrees and synced-base worktrees.
- [x] Support the `dev` updated from `main` flow, including optional push of the synced base.
- [x] Default worktrees to `${KLIMKIT_WORKTREE_ROOT:-$HOME/wt}`.
- [x] Make ambiguous invocation behavior explicit with examples and clarification guidance.
- [x] Update package references and tests from `klimkit-worktree-stack` to `klimkit-create-worktree`.
- [x] Run automated validation.

## Implementation Notes

- Replaced `skills/klimkit-worktree-stack/` with `skills/klimkit-create-worktree/`.
- Added `scripts/create_worktree.sh` for deterministic worktree creation.
- Added `scripts/worktree_lib.sh` for branch slugging, worktree folder naming, ref resolution, and push target inference.
- Added `references/create-worktree.md` for script usage, defaults, dev-sync pattern, handoff fields, and cleanup rules.
- Updated `README.md`, `skills/klimkit-setup/SKILL.md`, `skills/klimkit-implement/SKILL.md`, `tests/test_root_skills.py`, and the fresh Codex smoke test expected skill list.

## Validation

- `bash -n skills/klimkit-create-worktree/scripts/create_worktree.sh skills/klimkit-create-worktree/scripts/worktree_lib.sh`
- `skills/klimkit-create-worktree/scripts/create_worktree.sh --branch "Feature Sync" --base dev --sync-from main --dry-run --repo-root <repo-root> --worktree-root /tmp/klimkit-wt-test`
- `python3 -m unittest discover -s tests -q`
- `python3 -m unittest deprecated.runtime.tests.test_codex_stop_hook -q`
- `npx skills add ./ --list`
- `git diff --check`
- Temporary bare-origin integration check: created `main`, `dev`, a new main commit, then ran `create_worktree.sh --branch "Feature Test" --base dev --sync-from main --push-base`; verified the new worktree contained the main update and `origin/main` was an ancestor of pushed `origin/dev`.
- Public-surface scrub: `rg` and `git grep` found no remaining private project names, old private tailnet suffixes, private machine names, or local absolute home paths in tracked/package-visible files.

The local `quick_validate.py` helper was not present under `<codex-home>`; the Vercel Skills CLI list check validated package discovery instead.
`deprecated.runtime.tests.test_docs_static` was attempted as a legacy sanity check but is not runnable from the current deprecated layout because it expects `deprecated/runtime/README.md`, `deprecated/runtime/SECURITY.md`, and `deprecated/runtime/.gitignore`.
