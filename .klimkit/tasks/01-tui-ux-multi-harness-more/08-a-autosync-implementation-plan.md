# Autosync Implementation Plan

Agent-authored plan for the `07-h-autosync-and-live-apply.md` follow-up.

## Target Behavior

- New Klimkit configs enable daemon autosync by default on every VM.
- The default daemon interval is 5 seconds.
- The watched ref is `origin/main` by default.
- On each interval, the daemon fetches `origin/main`.
- If `origin/main` is unchanged, it does nothing.
- If `origin/main` is ahead and the local checkout is clean, the daemon fast-forwards the checkout.
- After a fast-forward, the daemon applies the current Klimkit plan so harness projections and managed files are updated.
- After applying, the daemon sends a short Telegram notification when Telegram is configured.
- The daemon then requests a managed service restart so Switchboard, supervisor, and client/server code changes become live.
- If the checkout is dirty or the remote is not a fast-forward, autosync refuses the update and logs the reason.

## Implementation Steps

1. Update the single TOML model.

   - Replace the old default-off `live_sync` wording with default-on `auto_sync`.
   - Add `auto_sync_interval_seconds = 5`.
   - Add `auto_sync_ref = "origin/main"`.
   - Keep the internal field name small for now to reduce churn.

2. Update supervisor autosync.

   - Fetch the configured ref.
   - Compare it with local `HEAD`.
   - Require a clean checkout and fast-forward ancestry.
   - Fast-forward with `git merge --ff-only`.
   - Run the updated `klimkit --config <path> apply --defer-service-restart`.
   - Restart the managed service after the apply subprocess returns.

3. Update apply behavior and reporting.

   - Keep normal `kk apply` and `kk pull` restarting services directly.
   - Add a hidden defer flag for daemon autosync so service files can be written before the daemon requests its own restart.
   - Keep live output showing changed files, run service actions, useful URLs, and status commands.

4. Add Telegram notification.

   - Use `[notifications.telegram]` from the single TOML.
   - Send one concise message after a successful fast-forward and apply, before service restart.
   - Include hostname, role, commit range, changed file count, and grouped areas such as Codex pack, Switchboard, Klimkit code, CI, and docs.
   - Do not fail autosync if Telegram delivery fails; log a warning and continue to restart.

5. Verify.

   - Unit-test default config values.
   - Unit-test supervisor config loading overrides.
   - Unit-test fast-forward/apply/restart orchestration.
   - Unit-test Telegram message construction and send request.
   - Run full `unittest` and coverage.
   - Run preview checks for service actions.
   - Get three final reviewer PASS decisions before final response.
