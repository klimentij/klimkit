# Codex Stop Thread Deeplink

## Request

Add a `codex://threads/<raw-session-id>` deep link to Codex Telegram stop notifications, using the raw `session_id` from the hook payload so Klim can open the thread in Codex apps. Keep pack changes under `packs/codex`, test the hook, commit and push to `main`, and let autosync consume `origin/main`.

## Acceptance Checklist

- [x] Codex Telegram stop notifications include a visible Codex app thread link exactly of the form `codex://threads/<raw-session-id>` whenever the hook payload includes a non-empty `session_id`.
- [x] The deep link is built from the raw hook payload `session_id`, not from `turn_id`, the Switchboard event id, a rollout filename, a thread title, or a URL-encoded/normalized session value; Telegram HTML escaping is only applied at the render boundary.
- [x] Stop notifications with an empty or missing `session_id` omit the Codex app link entirely and never emit a broken `codex://threads/` placeholder.
- [x] Existing stop-hook behavior remains intact: fail-open output is still `{"continue":true}`, skip rules still suppress notifications, subagent sessions are still ignored, and Switchboard remains the primary open option when a Tailscale URL is available.
- [x] Existing direct code-server links remain secondary, still require Tailscale DNS plus folder data, and are not replaced by the new Codex app link.
- [x] The production change is limited to the source-controlled Codex pack hook at `packs/codex/hooks/stop-notify.sh`; generated `~/.codex/hooks/stop-notify.sh` is not edited by hand.
- [x] `tests/test_codex_stop_hook.py` covers the runtime hook path with fake `curl` and `tailscale`, including Codex app link presence, raw session id usage, link omission without `session_id`, and continued Switchboard/code-server behavior.
- [x] Focused verification passes: `bash -n packs/codex/hooks/stop-notify.sh` and `uv run python -m unittest tests.test_codex_stop_hook -q`.
- [x] Pack/regression verification passes at minimum: `uv run python -m unittest tests.test_codex_pack_validation tests.test_codex_stop_hook -q` and `git diff --check`, or any unavailable check is recorded with the reason.
- [x] If the change is projected locally before handoff, projection uses Klimkit (`./klimkit apply --skip-services` or an explicitly justified safer variant) and the projected hook is verified; otherwise the proof note states that propagation is through autosync from `origin/main`.
- [x] A task proof note under `.klimkit/tasks/08-codex-stop-thread-deeplink/` records changed files, verification commands, notable outputs, skipped/unavailable checks, the pushed commit SHA, and the GitHub release tag.
- [x] The final implementation commit is on `main`, pushed to `origin/main`, and `origin/main` is verified to contain the pushed SHA so configured autosync workers can apply it.
- [x] After the commit lands on `main`, a next patch GitHub release is created for that commit and marked as the latest release, per the repository-local `AGENTS.md` instruction.
- [x] Reflection Gate is completed after verification and before final review: read `.klimkit/reflection.md`, append a full UTC timestamped session with `Observations`, `Derived Pattern`, `Insight`, and `Next Probe`, reconsider the result, and rerun impacted checks if reflection exposes a gap.
- [x] Final Review Gate is completed before any completion claim: draft the final response, run 3 parallel `final_reviewer` passes with this checklist, changed files, verification evidence, reflection entry, release/push evidence, and the exact draft response, and require all 3 to return PASS / READY FOR USER.
