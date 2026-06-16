# Troubleshooting & FAQ

A symptom → fix table plus answers to the questions that come up most. Every item
here reflects something actually hit and resolved while driving Codex.

## Symptom → fix

| Symptom | Cause | Fix |
|---|---|---|
| WS connects then closes immediately, no response | Sent raw JSONL to a WebSocket transport | Use `codex_ws.py` (real WS handshake + text frames). `unix://`/`ws://` are NOT raw JSONL. |
| `codex exec resume` reply never shows in the desktop | `exec` is a separate process; the desktop's app-server isn't notified | Use `codex_ws.py send` (app-server) — or restart the app to force a disk re-read |
| My exec agents aren't in `thread/list` | `thread/list` defaults to interactive sources | `codex_ws.py list --all-sources`, or use `find_active.py` |
| `thread/list` says `active` but nothing's happening | "active" = loaded in memory, not running a turn | Trust `find_active.py` (rollout mtimes + `codex exec` procs) instead |
| Sent to a socket but the desktop didn't update | Wrong socket (managed daemon, not the desktop's) | Target `desktop-ssh-websocket-*.sock` (the script default) |
| `codex app-server --listen unix:///tmp/x.sock` → "Operation not permitted" | app-server self-sandbox blocks `/tmp` | Listen under `~/.codex/...` instead |
| `Not initialized` error | Sent a request before the handshake | Send `initialize` then the `initialized` notification first |
| `Already initialized` error | Second `initialize` on one connection | Open a fresh connection per client |
| Handshake fails and you suspect versions | Usually NOT the cause | Check framing (WebSocket) and socket choice first; `codex app-server daemon version` to confirm |
| `turn/start` rejected / no events | Thread not loaded on this connection | `thread/resume` (or `thread/start`) before `turn/start` — `codex_ws.py send` does both |

## FAQ

**Q: How do I make a message appear in the Codex desktop app, live?**
Use the app-server, not `codex exec`:
`python3 scripts/codex_ws.py send --thread <ID> -t "..."`. It connects to the
exact app-server instance the desktop is subscribed to, so the user sees the user
message and the streamed reply in real time.

**Q: How do I get the session id?**
It's the `<UUID>` in the rollout filename
(`~/.codex/sessions/.../rollout-<ts>-<UUID>.jsonl`), and the `id` field from
`codex_ws.py list`. For CLI resume you can also use `--last`.

**Q: Can I run many Codex agents at once?**
Yes. Fan out `codex exec` processes (one per working dir), each with
`-o last_message.txt` to capture results. See SKILL.md "Orchestrating multiple
sessions". Monitor with `find_active.py`.

**Q: Do I need an auth token?**
Not for the local unix socket. Only for `ws://` TCP servers you secure with
`--ws-auth` — then pass `--token-file` to `codex_ws.py` where possible.
Avoid `--token` on shared machines because command-line arguments can appear in
shell history and process listings.

**Q: Will external `codex exec` writes corrupt a session the desktop has open?**
No corruption — both append to the rollout on disk. The only issue is the
desktop's in-memory view going stale (it reconciles on restart). Prefer driving
an actively-watched session through the app-server.

**Q: How do I read what a session said without changing it?**
`codex_ws.py read --thread <ID>` (via app-server), or parse the rollout JSONL
directly (filter `event_msg` payloads of type `user_message`/`agent_message`).

**Q: How do I watch a session live without sending anything?**
`codex_ws.py watch --thread <ID>` — it resumes (subscribes) and prints the event
stream until you Ctrl-C.

**Q: How do I stop a runaway turn?**
`codex_ws.py interrupt --thread <ID> --turn <TURN_ID>`. Get the turn id from the
`turn/start` result or a `turn/started` event.

**Q: How do I confirm the exact protocol fields for my Codex version?**
`codex app-server generate-ts --out /tmp/cxschema` and read the generated types
(`ClientRequest.ts`, `ServerNotification.ts`, `v2/*Params.ts`). Authoritative for
your build.

**Q: stdio vs unix vs ws — which transport should I use?**
- Talking to the **already-running** desktop/daemon server → its unix socket
  (WebSocket) via `codex_ws.py`.
- Spinning up your **own** server for a tool to drive → `--listen ws://IP:PORT`
  with auth, or `--stdio` (raw JSONL) if you control both ends in one process.

**Q: What's the difference between `desktop-ssh-websocket-*.sock` and
`app-server-control.sock`?**
The former is the instance the desktop app is connected to (use it to affect the
desktop). The latter is a separate managed daemon (`codex app-server daemon` /
`codex remote-control`) that the desktop is typically not subscribed to.
