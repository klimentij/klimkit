# Preflight — why each check exists

Every check here corresponds to a way the service fails *after* installation, usually as a
silent restart loop that looks like a broken unit file. Run them first; the diagnosis is
minutes of reading versus hours of tuning the wrong thing.

## 1. Binary and subcommand

```bash
command -v claude
claude --version
claude remote-control --help
```

Server mode (`claude remote-control` as a persistent multi-session server) is newer than
the single-session `claude --remote-control` flag. If `--help` does not list `--spawn` and
`--capacity`, the installed version predates server mode: upgrade, or install a
single-session unit and accept one session per process.

Resolve the binary through its stable path. A version-managed install is typically a
symlink such as `~/.local/bin/claude` → `~/.local/share/claude/versions/<version>`. Point
`ExecStart` at the **symlink**, so an upgrade does not leave the unit pointing at a
deleted version.

## 2. Authentication — the check that causes the most wasted time

Remote Control requires an interactive claude.ai OAuth session on a Pro, Max, Team or
Enterprise plan.

```bash
python3 - <<'PY'
import json, os
p = os.path.expanduser("~/.claude/.credentials.json")
d = json.load(open(p))["claudeAiOauth"]
print("subscription:", d.get("subscriptionType"))
print("scopes:", " ".join(d.get("scopes", [])))
PY
```

Expect a subscription type and a scope list containing `user:sessions:claude_code`. Then:

- **API keys are not supported at all.** If `ANTHROPIC_API_KEY` is set in the environment
  the service inherits, unset it in the unit.
- **A `setup-token` / `CLAUDE_CODE_OAUTH_TOKEN` is not enough.** Those long-lived tokens
  can only make model requests, so they cannot establish a Remote Control session, and the
  error says exactly that. Fix with an interactive `claude auth login` (or `/login`) as the
  **service user** — not as root, not as your own account, since credentials are per-home.
- On Team and Enterprise an Owner must enable the Remote Control toggle in Claude Code
  admin settings, and Trusted Devices — if enabled — requires each viewing device to
  enrol. Neither is fixable from the VM.

Interactive login cannot be done by a service. If the target user has never logged in, stop
and hand that step to the human; it is a browser flow.

## 3. API endpoint

```bash
echo "${ANTHROPIC_BASE_URL:-<unset>}"
```

Must be unset or `api.anthropic.com`. Remote Control is disabled when it points at an LLM
gateway or proxy, and on Amazon Bedrock, Google Cloud's Agent Platform and Microsoft
Foundry — there is no claude.ai backend to pair with. This bites hardest on machines whose
whole purpose is a cloud integration: keep **model traffic** direct to Anthropic and let
the cloud be the target of the work, not the transport for it.

The unit should clear all three variables explicitly rather than assume a clean
environment, since a system service inherits from the system manager, not from a shell.

## 4. Working directory and trust

```bash
test -d "$DIR/.git"          # required for --spawn worktree
python3 - <<'PY'
import json, os, sys
d = json.load(open(os.path.expanduser("~/.claude.json"))).get("projects", {})
p = sys.argv[1] if len(sys.argv) > 1 else ""
print("trusted:", bool(d.get(p, {}).get("hasTrustDialogAccepted")))
PY
```

The startup trust dialog never saves trust for the home directory, so the unit must set
`WorkingDirectory` to the project directory. An untrusted directory produces a server that
starts, waits for a dialog nobody can answer, and never reaches Ready — with no error.

Fix by running `claude` once interactively in that directory as the service user and
accepting the dialog.

`--spawn worktree` needs a git repository. Without one, use `--spawn same-dir` and accept
that concurrent sessions share a working tree.

## 5. Machine capacity

```bash
free -h; swapon --show; nproc
journalctl -k --since "30 days ago" | grep -ci "oom-kill"
df -h /
```

Record all of it. Zero swap on an agent host is a defect, and a non-zero OOM count means
you are about to install a long-running process onto a machine with a known memory
ceiling — fix that first, and read
[oom-and-capacity.md](oom-and-capacity.md) before choosing `--capacity`.

Disk matters for `--spawn worktree`: each session is a checkout.

## 6. Headless probe

The decisive test, because server mode is a TUI:

```bash
setsid claude remote-control --name probe-$$ --capacity 1 </dev/null >/tmp/probe.log 2>&1 &
sleep 25; grep -qi "ready" /tmp/probe.log && echo HEADLESS-OK; pkill -f "probe-$$"
```

`Ready` with no controlling terminal means a plain systemd unit works. A TTY error means
supervise `tmux new -d -s rc claude remote-control ...` instead — still supervised, still
restartable, one more moving part.

Run the probe from the real project directory: it doubles as a trust and eligibility test,
and its failure message is more specific than anything the unit's journal will show you.
