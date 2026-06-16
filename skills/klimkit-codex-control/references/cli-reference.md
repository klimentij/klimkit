# Codex CLI reference (sessions & orchestration)

Verified against `codex` 0.140 `--help` output and the official command-line
reference (`developers.openai.com/codex/cli/reference`). Run `codex <cmd> --help`
to confirm flags for your installed version.

## Where sessions live

- Rollout transcript (the source of truth for message content):
  `~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<UUID>.jsonl`
  The `<UUID>` is the session/thread id used by every command below.
- Index: `~/.codex/session_index.jsonl`
- Metadata DB (no message content): `~/.codex/state_*.sqlite` (`threads` table)
- App-server sockets: `~/.codex/app-server-control/*.sock`

## `codex exec` — non-interactive, scriptable (alias: `codex e`)

```
codex exec [OPTIONS] [PROMPT]
```
Reads the prompt from the argument or stdin. Key options (all verified):

| Flag | Meaning |
|---|---|
| `-C, --cd <DIR>` | set working directory before running |
| `-m, --model <MODEL>` | override model (e.g. `gpt-5.5`) |
| `-s, --sandbox <MODE>` | `read-only` \| `workspace-write` \| `danger-full-access` |
| `-a <POLICY>` | approval policy: `untrusted` \| `on-failure` \| `on-request` \| `never` |
| `--json` | stream structured JSONL events to stdout |
| `-o, --output-last-message <FILE>` | write the assistant's final message to a file |
| `-i, --image <FILE>...` | attach image(s) |
| `--ephemeral` | do not persist session files |
| `--skip-git-repo-check` | allow running outside a git repo |
| `--dangerously-bypass-approvals-and-sandbox`, `--yolo` | skip approvals + sandbox |
| `-c, --config <key=value>` | override any config.toml value (dotted path, TOML value) |
| `--enable <FEATURE>` / `--disable <FEATURE>` | toggle a feature flag |

### `codex exec resume` — continue a session headlessly
```
codex exec resume [SESSION_ID] [PROMPT]
codex exec resume --last "follow-up"      # most recent session in this cwd
codex exec resume --all <SESSION_ID> ...  # search sessions from any directory
```
Resumes by id (UUID) or thread name; UUID wins if it parses. **Does not appear
live in the desktop app** — for that, use the app-server (see SKILL.md part B).

## `codex resume` — interactive
```
codex resume                # picker (sessions from current cwd)
codex resume --last         # continue most recent
codex resume --all          # include sessions from any directory
```

## `codex fork` — branch a session
```
codex fork [--last] [--all]
```
Forks a previous session into a new thread (picker by default).

## `codex archive` / `codex unarchive` / `codex delete`
```
codex archive <SESSION_ID|name>     # hide from pickers, keep transcript
codex unarchive <SESSION_ID|name>
codex delete <SESSION_ID|name>      # permanently delete a saved session
```
Session ids take precedence over names.

## `codex app-server` — the JSON-RPC backend (experimental)
```
codex app-server [--listen <ENDPOINT>] [--ws-auth ...]
```
- `--listen stdio:// | unix:// | unix://PATH | ws://IP:PORT | off`
- WebSocket auth: `--ws-auth capability-token --ws-token-file <PATH>`
  (or `--ws-token-sha256 <HEX>`), or `--ws-auth signed-bearer-token
  --ws-shared-secret-file <PATH>`; plus `--ws-issuer`, `--ws-audience`,
  `--ws-max-clock-skew-seconds`.

Subcommands:
- `codex app-server proxy [--sock PATH]` — tunnel stdio ↔ a running server's
  socket (carries the WebSocket stream; does not change framing).
- `codex app-server daemon {bootstrap|start|restart|stop|version|enable-remote-control|disable-remote-control}`
  — manage the local managed daemon. `version` prints CLI + running server
  versions as JSON (handy to detect skew).
- `codex app-server generate-ts --out <DIR>` / `generate-json-schema --out <DIR>`
  — emit the exact protocol types for your build.

## `codex remote-control` — shared, externally-drivable daemon (experimental)
```
codex remote-control start [--json]
codex remote-control stop
```
Starts/stops the app-server daemon with remote-control enabled — the blessed way
to run one shared server that multiple clients (and external agents) connect to.

## `codex --remote <ADDR>` — remote TUI
Connect the local TUI to a remote app-server endpoint
(`ws://host:port`, `wss://host:port`, `unix://`, `unix://PATH`).

## Handy inspection one-liners
```bash
# All sessions, newest last:
ls -t ~/.codex/sessions/**/*.jsonl 2>/dev/null | head

# CLI vs running server version (detect skew):
codex app-server daemon version

# Who serves which socket:
ss -xlp | grep -E 'app-server|websocket'
```
