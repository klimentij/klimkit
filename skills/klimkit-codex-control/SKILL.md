---
name: klimkit-codex-control
description: Drive OpenAI Codex through the `codex` CLI and Codex desktop app from any agent or script. Use when Codex needs to spawn sessions, resume or connect to existing sessions, send live desktop messages, read transcripts, orchestrate many Codex agents, use the Codex app-server WebSocket protocol, or find active Codex sessions.
---

# Controlling & orchestrating Codex sessions

This skill lets any agent talk to OpenAI **Codex** (the `codex` CLI and the
Codex desktop app): start sessions, continue existing ones, stream replies,
read history, and run fleets of Codex agents. It bundles a working WebSocket
client so messages appear **live** in the desktop, plus reference docs and
ground-truth tooling.

> Verified against the official Codex docs (developers.openai.com/codex,
> `codex-rs/app-server/README.md`) AND against real hands-on use of the
> `codex` 0.140 CLI and a live app-server. Commands here are tested, not guessed.

## Operational safety

Treat thread ids, rollout excerpts, `thread/read` output, and `find_active.py`
output as potentially sensitive because they can reveal prompts, replies, cwd
paths, and repo names. Redact before pasting into tickets, reports, or chats.
Prefer the local unix socket. For TCP WebSocket auth, prefer `--token-file`;
`--token` is supported for quick local testing but can appear in shell history
and process listings.

## The one mental model that explains everything

A Codex **session** (a.k.a. **thread**) is a conversation. Its message content
lives **only** in a rollout file on disk:
`~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<UUID>.jsonl`.
The `<UUID>` in that filename IS the session/thread id you pass to every command.

There are **two completely different ways** to talk to a session, and picking
the wrong one is the #1 source of confusion:

| | **A. Headless CLI** (`codex exec`) | **B. Live app-server** (WebSocket) |
|---|---|---|
| How | spawns a fresh `codex` process | connects to the already-running app-server |
| Appears live in desktop app? | **No** — desktop stays stale until restart | **Yes** — streams to every connected client |
| Best for | batch jobs, fan-out fleets, CI, cron | interactive control, demos, nudging a session a human is watching |
| Tooling here | plain `codex` commands | `scripts/codex_ws.py` |

**Why B is needed:** the desktop app keeps each conversation in the memory of a
long-running `app-server` process. `codex exec` writes to the rollout file on
disk but never notifies that process, so the desktop doesn't update until it
restarts. To make a turn show up live, you must drive the **same app-server the
desktop is subscribed to**. That is exactly what `scripts/codex_ws.py` does.

Decision rule: **want a human to see it in the desktop in real time → use B.
Just need work done / automation → use A.**

---

## A. Headless CLI (`codex exec`)

Run a one-shot, non-interactive turn. Great for automation and orchestration.

```bash
# New session, non-interactive. Prints the agent's final message.
codex exec "Summarize README.md in 3 bullets"

# Useful flags (all verified):
codex exec \
  -C /path/to/repo \                 # --cd: working directory
  -m gpt-5.5 \                       # --model
  -s workspace-write \              # --sandbox: read-only|workspace-write|danger-full-access
  -a never \                        # approval policy: untrusted|on-failure|on-request|never
  --json \                          # stream structured JSONL events (for parsing)
  -o /tmp/last_message.txt \        # --output-last-message: write final reply to a file
  --skip-git-repo-check \           # allow running outside a git repo
  "Do the task"

# Continue an EXISTING session by id (or --last for the most recent in this cwd):
codex exec resume <SESSION_ID> "follow-up message"
codex exec resume --last "keep going"
codex exec resume --all <SESSION_ID> "..."   # search sessions from any directory
```

`codex exec resume` is the simplest way to continue a session **but it will NOT
show up live in the desktop** (see the mental model). Use B for that.

Other interactive/management commands: `codex resume` (interactive picker),
`codex fork` (branch a session), `codex archive` / `codex unarchive`,
`codex delete`. Full flag tables: `references/cli-reference.md`.

---

## B. Live app-server (appears instantly in the desktop)

Use the bundled client `scripts/codex_ws.py` (Python stdlib only — no installs).
It auto-discovers the desktop's socket under `~/.codex/app-server-control/` and
speaks the JSON-RPC protocol over WebSocket.

```bash
cd /path/to/klimkit-codex-control/scripts

# List sessions the app-server knows about:
python3 codex_ws.py list

# Send a message to an existing session — appears LIVE in the desktop, streams reply:
python3 codex_ws.py send --thread <SESSION_ID> -t "Give me a joke about the ocean"

# Start a NEW session (prints its id), optionally with a first message:
python3 codex_ws.py new --cwd /home/me/proj -m gpt-5.5 -t "Summarize the repo"

# Read a session's full history (metadata + turns):
python3 codex_ws.py read --thread <SESSION_ID>

# Watch a session's events live without sending anything (Ctrl-C to stop):
python3 codex_ws.py watch --thread <SESSION_ID>

# Interrupt the active turn:
python3 codex_ws.py interrupt --thread <SESSION_ID> --turn <TURN_ID>

# Remote / TCP app-server with auth:
python3 codex_ws.py --ws ws://127.0.0.1:4500 --token-file /path/token list
```

Under the hood every call does: WebSocket `Upgrade` handshake → `initialize` →
`initialized` → `thread/resume` (or `thread/start`) → `turn/start` → read
`item/agentMessage/delta` until `turn/completed`. Protocol details, all methods,
and event types are in `references/app-server-protocol.md`.

### Creating a brand-new session that shows up in the desktop

`codex_ws.py new` calls `thread/start` on the running app-server, so the new
session appears **live in the desktop sidebar** (verified: a session created this
way from the VM showed up immediately in the Mac desktop app connected to it).
This is the way to spin up a fresh Codex conversation another human can then take
over in the GUI.

```bash
# Minimal: new session in a repo, with a first message. Prints the new id, then streams the reply.
python3 codex_ws.py new --cwd /home/me/proj -t "Read README.md and propose 3 improvements"

# Full control of the new session's defaults:
python3 codex_ws.py new \
  --cwd /home/me/proj \
  -m gpt-5.5 \                       # model
  --sandbox workspace-write \        # read-only | workspace-write | danger-full-access
  --approval never \                 # untrusted | on-failure | on-request | never
  -t "Kick off the task"

# Create an empty session WITHOUT sending a turn (just get an id to drive later):
python3 codex_ws.py new --cwd /home/me/proj            # omit -t

# Capture just the new id for scripting:
TID=$(python3 codex_ws.py new --cwd /home/me/proj --no-wait 2>/dev/null)
python3 codex_ws.py send --thread "$TID" -t "now do the next step"
```

Notes:
- The new session inherits config defaults (`~/.codex/config.toml`) unless you
  override `--cwd` / `-m` / `--sandbox` / `--approval`.
- Codex auto-generates a human title from the conversation (e.g. it named one
  "Socket Garden"); until then the sidebar shows the first-message preview. The
  stable handle is always the printed thread id.
- Headless alternative (does NOT appear live in the desktop): a bare
  `codex exec "..."` also creates a new session — use it for automation, not for
  something a human is watching. See part A.

### Critical: the transport is WebSocket, not raw JSON

The `unix://` and `ws://` transports speak **WebSocket** (HTTP Upgrade + one
JSON-RPC message per text frame). Only `stdio` is raw newline-delimited JSON.
**Sending raw JSONL to the socket — even via `codex app-server proxy` — is
silently dropped** (the server just closes the connection with no error). This
is the single biggest gotcha and the reason `codex_ws.py` exists. Don't try to
reinvent it with `nc`, `socat`, or a bare socket write.

---

## Orchestrating multiple sessions

**Fan-out (headless, the workhorse):** launch N `codex exec` processes, each in
its own working directory, writing its final message to a file. This is how
real Codex experiment harnesses run (e.g. parallel solver arms).

```bash
for arm in raw raw_plus_substrate substrate_only; do
  dir="/tmp/run/agents/solve-$arm"
  mkdir -p "$dir"
  codex exec -C "$dir" -a never -s workspace-write --json \
    -o "$dir/last_message.txt" \
    "You are solving task X under arm: $arm. Write solution.md." \
    > "$dir/events.jsonl" 2>&1 &
done
wait
```

**Monitor what's actually running.** The app-server's `thread/list` marks a
thread `active` when it's merely *loaded*, and `exec` agents don't appear there
at all. For ground truth use the bundled finder:

```bash
python3 scripts/find_active.py --minutes 5
```

It reports rollout files written this minute (real work) and running
`codex exec` processes — the reliable signal for "what is Codex doing right now".

**Coordinator pattern:** one driver session (often a desktop session you watch
via B) spawns and supervises worker `exec` agents (A), polling their
`last_message.txt` / rollouts. Keep the human-facing driver on the app-server so
you can nudge or interrupt it live; keep the workers headless for throughput.

---

## Gotchas / "speed bumps" (read before debugging)

These are the traps that cost real time — each one was hit and resolved in
practice:

1. **Raw JSON to the socket does nothing.** `unix://`/`ws://` are WebSocket. Use
   `codex_ws.py` (or any real WS client). Symptom: connection accepted, then
   silently closed, no response. (Not a version or auth problem.)
2. **`codex exec resume` doesn't update the desktop.** Different process; the
   desktop's in-memory copy isn't notified. Use B, or restart the app to force a
   disk re-read.
3. **`thread/list` "active" is misleading** — it means *loaded*, not *running a
   turn*. And it defaults to **interactive sources only**, so `exec` agents are
   invisible. Use `find_active.py` for truth, or `list --all-sources`.
4. **Pick the right socket.** `desktop-ssh-websocket-*.sock` is the instance the
   desktop is subscribed to; `app-server-control.sock` is a *different* managed
   daemon the desktop is NOT on. To appear in the desktop, use the desktop
   socket (the script defaults to it).
5. **The app-server won't bind a socket under `/tmp`** ("Operation not
   permitted" — its self-sandbox). If you spin up your own server, listen under
   `~/.codex/...`.
6. **Version skew is usually a red herring.** A 0.139 server happily served a
   0.140 client. If a handshake fails, suspect framing (gotcha #1) or the wrong
   socket (#4), not the version.
7. **Local unix socket needs no auth token.** The "magic bytes" some desktop
   launchers print go to the SSH channel as a readiness signal, not the socket.
   Tokens (`--ws-auth`) only apply to `ws://` TCP transports you secure yourself.
8. **`thread/resume` then `turn/start` — not `turn/start` alone.** A turn needs
   the thread loaded/subscribed on that connection first. `codex_ws.py send`
   does both for you.

More Q&A in `references/troubleshooting.md`.

---

## Reference files

- `references/app-server-protocol.md` — JSON-RPC handshake, transports & auth,
  the full thread/* and turn/* method list, the live event stream, exact message
  shapes. Read this to extend `codex_ws.py` or speak the protocol yourself.
- `references/cli-reference.md` — every `codex` subcommand and flag for sessions
  (exec, resume, fork, archive, app-server, remote-control).
- `references/troubleshooting.md` — FAQ and a symptom → fix table.

## Bundled scripts

- `scripts/codex_ws.py` — the live WebSocket client (list/send/new/read/watch/
  interrupt). Stdlib only. This is the heart of the skill.
- `scripts/find_active.py` — ground-truth "what Codex sessions are doing work
  right now" (rollout mtimes + `codex exec` processes).
