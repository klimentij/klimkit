---
name: klimkit-remote-control
description: Set up Claude Code Remote Control on a VM or server so a project folder stays drivable from claude.ai/code and the Claude mobile app after the laptop closes. Use when asked to install, supervise, harden, resize, or debug remote control, keep agent sessions alive across disconnects and reboots, or diagnose why a long-running session or agent fleet died.
---

# Remote Control on a VM

Make one folder on a machine permanently drivable from a phone or browser. The work
executes on that machine — its filesystem, its credentials, its MCP servers — while
claude.ai/code is only a window onto it.

**The single most common failure is not what people expect.** Sessions usually die because
the machine ran out of memory and the kernel killed the *supervisor*, not because the
network dropped. Diagnose before you design: a session dying at a memory ceiling and a
session dying at a network timeout need different fixes, and only one of them is fixed by
`Restart=always`. See [references/oom-and-capacity.md](references/oom-and-capacity.md).

Work through the phases in order. Do not install anything before Phase 1 passes — an
ineligible account produces a service that restart-loops forever and looks like a bug in
your unit file.

## Phase 0 — Is this the right tool?

Remote Control drives a session **running on this machine**. Reach for something else when:

| Want | Use instead |
|---|---|
| Work on a repo without local setup, or many parallel cloud tasks | Claude Code on the web |
| Fire work from a chat app (Telegram, Discord, iMessage) on push events | Channels |
| Message a task from the phone and let it spawn a session | Dispatch (Desktop) |
| Run something on a schedule with no session open | Scheduled tasks, or cloud routines |

Choose Remote Control when execution must stay on this machine — local secrets, a VPC, a
database, a GPU, an interactively authenticated CLI — or the job outlives a cloud session.

## Phase 1 — Preflight, before installing anything

Run [scripts/preflight.sh](scripts/preflight.sh). It exits non-zero with a specific reason
and prints a summary of the machine. Every check exists because it silently breaks the
service otherwise; the full rationale is in [references/preflight.md](references/preflight.md).

```bash
scripts/preflight.sh --dir /home/ubuntu/myrepo
```

It verifies, in order: `claude` is installed and supports `remote-control`; the login is a
claude.ai OAuth session, not an API key and not a `setup-token`; `ANTHROPIC_BASE_URL` is
unset or `api.anthropic.com`; the target directory exists, is a git repo if you want
worktree spawning, and has accepted workspace trust; and the machine's memory, swap and
prior OOM history.

**Do not skip the headless probe.** Server mode is a TUI, and whether it runs without a
controlling terminal decides the whole design. It works on current versions — verified on
v2.1.220 — but confirm on the version in front of you rather than trusting either this
skill or the stale GitHub issues claiming a hard TTY requirement:

```bash
scripts/preflight.sh --dir /path/to/repo --headless-probe
```

If the probe fails, stop and supervise a terminal multiplexer instead (`tmux new -d -s rc`
under a systemd unit). Do not fake a TTY without saying so in the handoff.

## Phase 2 — Protect memory before adding a long-running agent

An agent host is a memory-hungry host: each session is hundreds of MB to a few GB, and
agent fleets multiply that. Do this **before** installing the service, or the first busy
day repeats the failure you are trying to prevent.

1. **Add swap if there is none.** Zero swap turns a transient spike into an instant kill.
2. **Cap collectively, not per server.** Put every remote-control instance in one parent
   slice with the memory bound on the slice. A per-instance cap only relocates the OOM.
3. **Make disposable work the preferred victim.** Fleets get `oom_score_adj=800` and their
   own capped slice, so the kernel kills the fleet and not the supervisor.

The installer does all three. Sizing guidance and the arithmetic are in
[references/oom-and-capacity.md](references/oom-and-capacity.md).

## Phase 3 — Install the supervised service

```bash
sudo scripts/install_remote_control.sh --dir /home/ubuntu/myrepo --name vps-myrepo
```

Defaults: `--spawn worktree`, `--capacity 8`, `--permission-mode auto`, 8 GB swap if the
machine has none, an 8 GB cap on the parent slice. All are flags; run with `--dry-run`
first to print what it would write. It is idempotent — re-running updates the units in
place. Every unit file it installs is reproduced and explained in
[references/systemd-units.md](references/systemd-units.md), so you can write them by hand
on a machine where running an installer is not acceptable.

Two decisions inside it are worth knowing, because getting them wrong is the difference
between a service that survives the bad day and one that does not:

- **System unit, not `systemctl --user` + linger.** The per-user systemd manager carries
  `OOMScoreAdjust=100` by design, so under a global OOM the kernel kills the user manager
  *before* the workload — and `Restart=always` cannot fire when the supervisor is the
  corpse. A system unit is supervised by PID 1, which cannot be killed, and
  `WantedBy=multi-user.target` starts it at boot with nobody logged in. Use a user unit
  only when you have no root; then `loginctl enable-linger` is mandatory, and say plainly
  in the handoff that the supervisor is itself killable.
- **`WorkingDirectory` is the project directory.** Workspace trust is per-directory and is
  never saved for `$HOME`, so a server started from the home directory prompts for trust
  and never becomes ready.

For a second project, run the installer again with a different `--dir`. The unit is a
template: one instance per project, all sharing the parent slice's memory bound.

## Phase 4 — Verify, and prove it

Claiming durability without testing it is the whole failure mode. Run
[scripts/healthcheck.sh](scripts/healthcheck.sh), which asserts rather than prints:

```bash
scripts/healthcheck.sh --instance myrepo --kill-test
```

- `is-active` and `is-enabled` — running now, and comes back at boot.
- The journal reaches `Ready` and shows the expected capacity and spawn mode.
- `--kill-test` sends `SIGKILL` to the main PID and asserts a **new** PID within 30 s.
  A restart that does not change the PID means you tested nothing.
- Swap is on and in `/etc/fstab`; the slice caps are applied; no `oom-kill` in the last
  24 h of kernel log.

Report the session's **name**, not its URL. After any restart the environment URL changes
while the name does not, so a bookmarked URL breaks exactly when the service does its job.
Find the session by name at claude.ai/code or in the mobile app's Code tab.

## Phase 5 — Supervision is not durability

A supervised service protects the *process*. It does not protect the *work*. When a session
dies, the transcript survives — it is stored server-side while Remote Control is connected,
which is what lets a session reconnect — but in-flight uncommitted work does not.

Make session death cheap:

- One worktree per task, so a lost session never blocks another.
- Commit and push per **decision**, not per session. A decision that exists only in the
  conversation is lost with the process.
- Write approved decisions into a file in the repo as they are approved. Questions asked
  and answers received belong on disk before the next question is asked. `klimkit-grill-me`
  produces exactly this artifact; keep the phase `LOG.md` current as beats happen.

The test of a good setup is not that sessions never die. It is that a death costs a
reconnect instead of an archaeology session.

## Permission mode

`auto` is the default and the right one for unattended work: tool calls are auto-approved
with a classifier holding back the genuinely dangerous ones. `bypassPermissions` approves
everything unconditionally — on a host with production credentials that is a materially
different exposure, so set it only on explicit instruction, and record it in the handoff.

When a specific recurring call keeps being blocked, allowlist that call in the project's
`.claude/settings.json` rather than widening the mode.

## Troubleshooting

Match the exact error text to a cause in
[references/troubleshooting.md](references/troubleshooting.md) — every documented failure
has a distinct message, and guessing wastes a restart cycle. The most common:

| Symptom | Cause |
|---|---|
| Unit restart-loops within seconds | Ineligible auth; run Phase 1 rather than tuning `RestartSec` |
| "requires a full-scope login token" | A `setup-token`/`CLAUDE_CODE_OAUTH_TOKEN` can only make model requests |
| "only available when using Claude via api.anthropic.com" | Gateway/proxy `ANTHROPIC_BASE_URL`, or Bedrock/Vertex/Foundry |
| Never reaches Ready, no error | Trust dialog waiting — `WorkingDirectory` is not the project dir |
| Dies after ~10 idle minutes offline | Documented network-outage exit; `Restart=always` is the answer |
| Everything died at once, including tmux | Global OOM took the supervisor — [references/oom-and-capacity.md](references/oom-and-capacity.md) |

## Handoff

State: the session name for each project, the unit names, permission mode, capacity, swap
and slice caps, whether the kill test passed, and anything the human must do themselves.
If you set a mode more permissive than `auto`, say so in its own sentence.
