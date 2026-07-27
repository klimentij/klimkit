# The unit files, and why each line is there

Everything the installer writes, reproduced so it can be hand-installed on a machine where
running someone else's script is not acceptable. Paths assume the service user is `ubuntu`;
substitute throughout.

## Two files per project, not one

A template unit is **shared by every instance**, so anything project-specific must live in a
per-instance drop-in. Hardcoding `WorkingDirectory` in the template appears to work with one
project and then silently repoints the first project when you add a second — a failure that
surfaces as sessions landing in the wrong repository.

### The shared template

`/etc/systemd/system/claude-rc@.service` — invariants only, no `ExecStart`:

```ini
[Unit]
Description=Claude Code Remote Control server (%i)
Documentation=https://code.claude.com/docs/en/remote-control
Wants=network-online.target
After=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
# WorkingDirectory, User, Environment and ExecStart come from
# /etc/systemd/system/claude-rc@<instance>.service.d/10-project.conf
# An instance with no drop-in intentionally refuses to start.

UnsetEnvironment=ANTHROPIC_BASE_URL ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN

Restart=always
RestartSec=5

Slice=claude-rc.slice
OOMPolicy=continue
TasksMax=16384
LimitNOFILE=65536

StandardOutput=journal
StandardError=journal
SyslogIdentifier=claude-rc-%i

[Install]
WantedBy=multi-user.target
```

An instance without a drop-in fails with `Service has no ExecStart=. Refusing.` — a loud,
correct failure rather than a server quietly pointed at the wrong tree.

### The per-instance drop-in

`/etc/systemd/system/claude-rc@myrepo.service.d/10-project.conf`:

```ini
[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/myrepo

Environment=HOME=/home/ubuntu
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin

# Reset before setting: a drop-in APPENDS to ExecStart unless cleared first.
ExecStart=
ExecStart=/home/ubuntu/.local/bin/claude remote-control \
    --name vps-myrepo \
    --spawn worktree \
    --capacity 8 \
    --permission-mode auto
```

Line by line, the ones that are load-bearing:

- **`WorkingDirectory`** must be the project directory. Workspace trust is per-directory and
  is never saved for `$HOME`; a server started from home waits forever on a trust dialog.
- **`Environment=HOME=`** is required. A system service does not inherit a login
  environment, and without `HOME` the OAuth credentials at `~/.claude/.credentials.json`
  are not found — which presents as an authentication failure, not a configuration one.
- **`Environment=PATH=`** must contain whatever the binary needs at runtime (a Node
  toolchain for some installs) plus the directory holding `claude` itself.
- **`ExecStart=` on its own line first.** Drop-ins append to list-typed directives; without
  the reset you get two `ExecStart` lines and a startup failure.
- **`ExecStart`** points at the **symlink**, not a version directory, so upgrades do not
  orphan the unit.
- **`UnsetEnvironment=`** clears the three variables that disable Remote Control outright.
  Clear them explicitly rather than trusting the inherited environment to be clean.
- **`Restart=always` + `RestartSec=5`** answers the documented ~10-minute network-outage
  exit as well as crashes and reboots.
- **`StartLimitIntervalSec=0` in `[Unit]`** — not `[Service]`, where systemd ignores it with
  an "Unknown key" warning. Without it, repeated fast restarts latch the unit off in the
  `failed` state, which is precisely when you need it most.
- **`Slice=`** puts the server and every session it spawns under the shared cap.
- **`OOMPolicy=continue`** keeps the server alive when the kernel kills one of its
  sessions. The default would take the whole unit down with the child.
- **`WantedBy=multi-user.target`** starts it at boot with nobody logged in — no login, no
  linger, no tmux.

## The parent slice

`/etc/systemd/system/claude-rc.slice`:

```ini
[Unit]
Description=Claude Code Remote Control servers and their spawned sessions
Before=slices.target

[Slice]
MemoryHigh=6G
MemoryMax=8G
CPUWeight=200
```

The bound belongs here rather than on each service: with several instances and a high
per-instance capacity, a per-instance cap only decides which instance dies first. Size it
to leave room for Docker, databases and the OS.

## The fleet slice and wrapper

`/etc/systemd/system/agent-fleet.slice`:

```ini
[Unit]
Description=Disposable agent fleets
Before=slices.target

[Slice]
MemoryHigh=4G
MemoryMax=5G
CPUWeight=50
```

`/usr/local/bin/fleet-run` — launch every fleet through it so the kernel kills the fleet
instead of the supervisor:

```bash
#!/usr/bin/env bash
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: fleet-run <command> [args...]" >&2; exit 64; }

if sudo -n true 2>/dev/null; then
    exec sudo -n systemd-run --quiet --collect --scope \
        --slice=agent-fleet.slice \
        --uid="$(id -u)" --gid="$(id -g)" \
        --setenv=HOME="$HOME" --setenv=PATH="$PATH" \
        -- choom -n 800 -- "$@"
fi
exec choom -n 800 -- "$@"
```

Note the shape: **scope units accept cgroup properties but not exec properties**, so
`-p OOMScoreAdjust=800` is rejected with `Unknown assignment`. Set the score with `choom`
*inside* the scope instead. The no-sudo fallback still fixes victim ordering, since an
unprivileged process may always make itself more killable.

## Applying and checking

```bash
sudo systemctl daemon-reload
sudo systemd-analyze verify claude-rc@myrepo.service   # the INSTANCE, not the template
sudo systemctl enable --now claude-rc@myrepo
systemctl show claude-rc@myrepo -p Slice -p Restart -p OOMPolicy -p ExecStart --value
systemctl show claude-rc.slice -p MemoryMax --value
```

Verify the **instance**, since the template deliberately has no `ExecStart` of its own.
`systemd-analyze verify` catches misplaced keys — including the `StartLimitIntervalSec`
mistake above — that systemd otherwise only mentions once in the journal and then ignores.

## Without root

A user unit at `~/.config/systemd/user/claude-rc@.service` works with `%h` instead of the
hardcoded home, no `User=`/`Group=`, and `WantedBy=default.target`. It then requires:

```bash
loginctl enable-linger "$USER"
systemctl --user enable --now claude-rc@myrepo
```

`enable-linger` is what makes it survive logout and reboot. Be explicit in the handoff that
this variant is supervised by a manager that is itself a preferred OOM victim: enabled
units do come back when the user manager restarts, but only minutes later and only if the
manager restarts at all.

## Without systemd

On macOS, wrap the same command in a launchd agent with `KeepAlive` and
`RunAtLoad`, and use `WorkingDirectory` and `EnvironmentVariables` for the same reasons.
There is no cgroup equivalent, so memory protection reduces to sizing and to keeping fleets
small. On a container host, run one server per container with a restart policy and a memory
limit — same three ideas, different mechanism.
