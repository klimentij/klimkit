# Codex app-server protocol reference

The app-server is the JSON-RPC 2.0 service that powers every Codex surface
(desktop, mobile, IDE extension, remote TUI). Driving it directly is how you
make a turn appear **live** in all connected clients. Sources: official docs
(`developers.openai.com/codex/app-server`, `codex-rs/app-server/README.md`) and
hands-on verification with `codex` 0.140.

## Table of contents
1. Transports & framing
2. Authentication
3. Handshake
4. Thread methods
5. Turn methods
6. Server → client events (the live stream)
7. Key message shapes
8. Generating exact schemas locally

---

## 1. Transports & framing

Start a server with `codex app-server [--listen <endpoint>]`:

| Endpoint | Framing |
|---|---|
| `stdio://` (default, or `--stdio`) | **newline-delimited JSON (JSONL)** — raw, one object per line |
| `unix://` or `unix://PATH` | **WebSocket** over a unix socket (HTTP Upgrade + frames) |
| `ws://IP:PORT` | **WebSocket** over TCP — "one JSON-RPC message per WebSocket text frame" |
| `off` | disabled |

**The trap:** only `stdio` is raw JSONL. The unix and ws transports require a
real WebSocket handshake; raw bytes are dropped silently. The running
desktop/daemon servers listen on unix sockets under
`~/.codex/app-server-control/` — so you need WebSocket. `codex app-server proxy
[--sock PATH]` is a *dumb byte tunnel* that carries the WebSocket stream; it does
NOT convert framing, so you still must speak WebSocket through it.

Which socket?
- `desktop-ssh-websocket-*.sock` → the instance the **desktop app** is
  subscribed to. Use this to make turns show up in the desktop.
- `app-server-control.sock` → a separate **managed daemon** (`codex app-server
  daemon` / `codex remote-control`). The desktop is usually NOT on this one.

## 2. Authentication

- **Local unix socket:** no token required before `initialize`.
- **`ws://` TCP** you expose: secure it. Flags (verbatim from docs):
  - `--ws-auth capability-token --ws-token-file /absolute/path`
  - `--ws-auth capability-token --ws-token-sha256 HEX`
  - `--ws-auth signed-bearer-token --ws-shared-secret-file /absolute/path`
  - plus `--ws-issuer`, `--ws-audience`, `--ws-max-clock-skew-seconds`
  - Clients present `Authorization: Bearer <token>` during the WS handshake
    (`codex_ws.py --token-file` does this without exposing the token in argv;
    `--token` is only for quick local tests).

Note: some SSH desktop launchers `printf` a few "magic bytes" before starting
the proxy — that is a readiness signal sent to the *client over the SSH channel*,
**not** a socket auth token. Don't try to replay it.

## 3. Handshake

Immediately after the WebSocket connection opens:

```json
{"method":"initialize","id":0,"params":{"clientInfo":{"name":"my-agent","title":"My Agent","version":"1.0.0"}}}
```
then the notification:
```json
{"method":"initialized"}
```

- A request before `initialize` returns a **`Not initialized`** error.
- A second `initialize` on the same connection returns **`Already initialized`**.
- `capabilities` may be omitted; `jsonrpc:"2.0"` is accepted but optional.

## 4. Thread methods (requests)

| Method | Purpose |
|---|---|
| `thread/start` | create a new thread (params: `cwd`, `model?`, `sandbox?`, `approvalPolicy?`, `personality?`, `baseInstructions?`, `ephemeral?`, …) |
| `thread/resume` | load/subscribe an existing thread by `threadId` (also rejoins a running one) |
| `thread/fork` | branch a thread into a new one |
| `thread/read` | read a thread (`threadId`, `includeTurns?`) |
| `thread/list` | list threads (filters: `cwd`, `searchTerm`, `archived`, `sourceKinds`, `limit`, `cursor`, `sortKey`, `useStateDbOnly`) |
| `thread/turns/list` | page through a thread's turns |
| `thread/archive` / `thread/unarchive` | hide/restore in pickers |
| `thread/delete` | delete |
| `thread/name/set` | rename |
| `thread/goal/set` · `thread/goal/get` · `thread/goal/clear` | thread goal |
| `thread/compact/start` | compact history |
| `thread/rollback` | roll back turns |
| `thread/unsubscribe` | stop receiving this thread's events |
| `thread/loaded/list` | thread ids currently loaded in the server's memory |

**Important `thread/list` defaults:** `sourceKinds` defaults to **interactive
sources only**, so `exec`/agent sessions don't show up unless you pass
`sourceKinds: []`. `cwd` filters to exact-match session cwd.

## 5. Turn methods

| Method | Purpose |
|---|---|
| `turn/start` | send user input and run a turn. Params: `threadId`, `input: UserInput[]`, optional per-turn overrides (`model`, `effort`, `cwd`, `approvalPolicy`, `sandboxPolicy`, `outputSchema`, …) |
| `turn/steer` | inject input into the **in-progress** turn (`threadId`, `input`, `expectedTurnId`) |
| `turn/interrupt` | stop the active turn (`threadId`, `turnId`) |

`UserInput` items:
```json
[{"type":"text","text":"hello"}]
```
Other variants: `{"type":"image","url":...}`, `{"type":"localImage","path":...}`,
`{"type":"skill","name":...,"path":...}`, `{"type":"mention","name":...,"path":...}`.
A `text` item may carry `text_elements: []`, but it is optional — omit it for
cross-version compatibility.

## 6. Server → client events (the live stream)

After `turn/start`, the server streams notifications. The important ones:

- `turn/started`, `turn/completed`
- `item/started`, `item/completed`
- `item/agentMessage/delta` — streaming assistant text (concatenate `params.delta`)
- `item/reasoning/textDelta`, `item/reasoning/summaryTextDelta`
- `item/commandExecution/outputDelta`, `item/fileChange/patchUpdated`
- `item/mcpToolCall/progress`, `item/plan/delta`
- `thread/status/changed`, `thread/tokenUsage/updated`
- `thread/started`, `thread/name/updated`, `thread/compacted`
- `error` (params describe the failure), `guardianWarning`, `configWarning`

To capture an assistant reply: accumulate `item/agentMessage/delta.params.delta`
until `turn/completed`. (This is exactly what `codex_ws.py` does.)

## 7. Key message shapes (observed live)

`initialize` result:
```json
{"id":0,"result":{"userAgent":"Codex Desktop/0.139.0 ...","codexHome":"/home/you/.codex","platformOs":"linux"}}
```
`thread/resume` result contains `result.thread` (id, sessionId, preview, status…).
`turn/start` result contains `result.turn` (id, status:"inProgress", …) — grab
`result.turn.id` if you later want to `turn/interrupt`.

## 8. Generating exact schemas locally

The protocol evolves; to get the precise types for your installed version:

```bash
codex app-server generate-ts --out /tmp/cxschema        # TypeScript bindings
codex app-server generate-json-schema --out /tmp/cxjson # JSON Schema
```

Then inspect e.g. `ClientRequest.ts` (all request methods), `ServerNotification.ts`
(all events), `v2/TurnStartParams.ts`, `v2/ThreadStartParams.ts`, etc. This is
the authoritative source for param fields on your exact build.
