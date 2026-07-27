# Troubleshooting

Match the **exact** message. Each documented failure has a distinct one, and guessing costs
a restart cycle. Read the service's own output first:

```bash
sudo journalctl -u claude-rc@myrepo -n 100 --no-pager -o cat | sed 's/\x1b\[[0-9;]*[A-Za-z]//g'
```

The `sed` strips the TUI's ANSI escapes, which otherwise make the journal unreadable. For a
failure that happens before any output, re-run the command by hand as the service user with
`--verbose`.

## Authentication and eligibility

| Message | Cause and fix |
|---|---|
| `Remote Control requires a claude.ai subscription` | Not authenticated with claude.ai, or `ANTHROPIC_API_KEY` is set. API keys are never supported. Unset it and `claude auth login` as the service user. |
| `Remote Control requires a full-scope login token` | Authenticated with `claude setup-token` or `CLAUDE_CODE_OAUTH_TOKEN`. Those can only make model requests. `claude auth login` for a full-scope session token. |
| `Unable to determine your organization for Remote Control eligibility` | Stale cached account info. `claude auth login` to refresh. |
| `Remote Control is not yet enabled for your account` | Rollout gate or stale entitlements. `claude auth logout` then `login`; `claude doctor` shows which check failed. |
| `Couldn't verify Remote Control eligibility` | Could not reach the feature-flag service — offline, or a proxy blocking it. |
| `Remote Control is disabled by your organization's policy` | Four distinct causes: API-key/Console login; Owner has not enabled the Team/Enterprise toggle; a data-retention configuration that is incompatible; or `disableRemoteControl` in managed settings. Run `/status` to see which login is in use. |
| `Remote Control is only available when using Claude via api.anthropic.com` | `ANTHROPIC_BASE_URL` points at a gateway or proxy, or the session runs on Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry. Unset the variable and restart. |
| `Remote credentials fetch failed` | Not signed in, a firewall blocking outbound HTTPS on 443, or a failed session creation. Re-run with `--verbose`. |
| `...device is not enrolled` / `session expired for trusted-device check` | Trusted Devices is on for the organization. Enrol via `/login`; sign-ins older than 18 hours need a biometric step-up on the viewing device. |

A service that restart-loops within seconds of `ExecStart` is almost always one of these,
not a unit-file problem. Fix eligibility before touching `RestartSec`.

## Starts but never becomes Ready

- **Trust dialog.** `WorkingDirectory` is not the project directory, or the directory has
  never been trusted. Run `claude` there once interactively as the service user.
- **Not a git repository** while `--spawn worktree` is set. Use `--spawn same-dir`.
- **Wrong `HOME`.** Without `Environment=HOME=`, credentials are not found and the failure
  reads like an authentication problem.

## Dies after running fine

| Symptom | Cause |
|---|---|
| Exits ~10 minutes after connectivity fails, nothing else affected | The documented network-outage timeout. `Restart=always` reconnects; a new session is created, so find it by **name**. |
| Several unrelated processes die in the same second, tmux included | Global OOM. Do not treat this as a Claude failure — see [oom-and-capacity.md](oom-and-capacity.md). |
| Remote Control drops when a planning session starts | An ultraplan session disconnects Remote Control; both occupy the claude.ai/code interface. |
| Unit is `failed` and will not restart | The start limiter latched. `StartLimitIntervalSec=0` belongs in `[Unit]`; verify with `systemd-analyze verify`, since systemd only warns once about the misplaced key and then ignores it. |

## Session is running but not visible

The session list is keyed by name. After any restart the environment URL changes while the
name does not, so a saved URL points at a dead environment: look up `vps-<project>` at
claude.ai/code or in the mobile app's Code tab instead.

If two servers were installed for the same directory, both appear and steal work from each
other. One unit instance per directory.

## Verifying a fix actually worked

```bash
scripts/healthcheck.sh --instance myrepo --kill-test
```

A restart that returns the **same** PID proves nothing. Assert a new PID, and confirm
`is-enabled` as well as `is-active` — a running service that is not enabled will not
survive the reboot you are claiming to be protected against.
