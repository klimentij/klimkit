# Switchboard2 Spec

Author: Codex
Date: 2026-04-17
Status: Draft for review

## Purpose

Build a new Switchboard backend from scratch under `src/klimkit/apps/switchboard2`, while keeping the current visual UI model.

The new system must optimize for:

- ultra-fast local responsiveness
- low steady-state memory usage
- instant reflection of agent state changes in the UI
- explicit rich states beyond `idle` and `working`
- local-first operation on this VM, then clean expansion to other Tailscale VMs

This document is intentionally backend-heavy. The current UI can be kept with a compatibility API first, then upgraded incrementally after the backend is trustworthy.

## Source Checks

This spec is based on three sources of truth checked on 2026-04-17:

1. Official Codex hooks docs:
   `https://developers.openai.com/codex/hooks`

   Relevant constraints confirmed:

   - Codex discovers hooks from `~/.codex/hooks.json` and `<repo>/.codex/hooks.json`.
   - Hooks receive structured JSON input.
   - `Stop` does not use `matcher`.
   - `Stop` is continuation-oriented, not a general live event stream.
   - `Stop` only fires when a turn stops, so it cannot power instant live updates by itself.

2. Real local Codex runtime data on this VM:

   - `~/.codex/sessions/**/rollout-*.jsonl`
   - `~/.codex/session_index.jsonl`
   - `~/.codex/hooks.json`
   - `~/.codex/hooks/stop-notify.sh`
   - `~/.codex/switchboard/events.jsonl`

3. Current Switchboard implementation and failure mode:

   - `src/klimkit/apps/switchboard/`
   - `src/klimkit/tools/switchboard_agent/`

## What Codex Actually Emits Here

The local rollout files are the most important source of truth.

Observed row families:

- `session_meta`
- `turn_context`
- `event_msg`
- `response_item`

Observed useful event kinds:

- `task_started`
- `task_complete`
- `agent_message`
- `user_message`
- `token_count`
- `context_compacted`
- `exec_command_end`
- `web_search_end`

Observed useful response item kinds:

- `message`
- `function_call`
- `function_call_output`
- `reasoning`

Observed state-bearing details:

- `response_item.function_call.name == "request_user_input"` already appears and is enough to model waiting-for-user state.
- `turn_context.approval_policy` appears in historical sessions, so approval mode is visible in raw data.
- Historical Codex traces on this machine include event names such as `exec_approval_request`, `apply_patch_approval_request`, `plan_delta`, and `plan_update`. I have not yet seen those in the current CLI rollout files here, so Switchboard2 must support them as optional event kinds rather than assuming they always exist.

Implication:

- The rollout tail is the live backbone.
- Hooks are auxiliary hints and notification triggers.
- The backend must be version-tolerant because Codex event shapes differ across clients and versions.

## Why Switchboard1 Fails

Current failures are architectural, not cosmetic.

1. It treats the board as a periodically rebuilt snapshot instead of an event system.
2. It depends on fragile cache deserialization and currently crashes on stale cache rows missing `created_at`.
3. It hides stale sync by degrading old `working` sessions to `idle`, which makes the UI lie.
4. Notifications depend on fresh snapshot polling instead of real transitions.
5. It sends large prose-heavy payloads through the hot path.
6. It has no explicit sync health state.
7. The HTTP ingest path accepts a whole JSON blob and fails badly on truncation.

Switchboard2 will remove all of those assumptions.

## Product Goals

### Primary goals

- Show state changes in the board within one second, with a same-VM target much lower than that.
- Keep memory flat with hundreds of tabs and large session histories.
- Preserve correct ordering when a session changes state.
- Separate `planning`, `working`, `needs_input`, `awaiting_approval`, `done`, `idle`, `errored`, and `stale`.
- Support local operation first, then remote VM event forwarding over Tailscale.
- Keep the current UI shape alive behind a compatibility layer.

### Non-goals

- Full-text conversation search in v1.
- Reconstructing every possible Codex-internal semantic detail.
- Rich multi-user auth in v1.
- Browser-only logic for correctness. Correctness must live on the backend.

## Security Baseline

Switchboard2 does not need a full user system in v1, but it also cannot treat tailnet reachability as sufficient protection.

Minimum security baseline:

- `backend.auth_token` is mandatory for any non-loopback or multi-VM deployment
- read and write API endpoints require either loopback access or the configured token
- inbound session payloads must not be trusted to choose arbitrary iframe URLs; the backend derives the workspace URL from `machine_dns` and `cwd`
- request bodies need size limits
- SSE fan-out needs a subscriber cap so one noisy client class cannot pin unbounded threads

## Design Principles

1. Event-first, projection-second.
2. Local rollout files are the primary source of truth.
3. Hooks are optional accelerators, never the sole source of truth.
4. No giant state snapshots in the hot path.
5. SQLite in WAL mode for single-node simplicity, durability, and low overhead.
6. Explicit staleness and sync health instead of heuristic relabeling.
7. UI subscriptions via SSE, not poll-diff inference.
8. Backward-compatible API surface first, UI rewrite later if needed.

## High-Level Architecture

Switchboard2 has four runtime parts.

### 1. Local collector

Process that incrementally tails local Codex sources:

- `~/.codex/sessions/**/rollout-*.jsonl`
- `~/.codex/session_index.jsonl`
- `~/.codex/switchboard/events.jsonl`

Responsibilities:

- detect newly appended lines
- parse raw rows incrementally
- normalize into compact event records
- write to the local event store
- update session projections
- publish in-process change notifications to SSE subscribers

This is the latency-critical path.

### 2. Event store

Single SQLite database in WAL mode.

Responsibilities:

- append-only normalized events
- projection tables for current session state
- metadata for archive/pin/local UI state
- source checkpoints per file
- idempotent ingest for remote machines

This is the only durable backend state.

### 3. API server

Lean HTTP server serving:

- current UI assets
- REST compatibility endpoints
- incremental catalog pagination
- SSE stream for instant updates
- remote event ingest for other VMs

The API server should read current projections directly and never rebuild whole-system snapshots on request.

### 4. Optional satellite forwarder

For other VMs later:

- a tiny local collector on each VM
- tails that VM's Codex files
- forwards normalized events to the primary Switchboard2 server on `server` over Tailscale

This keeps remote memory and CPU minimal and avoids shipping giant snapshots across machines.

Topology decision:

- every VM runs the same Switchboard2 daemon
- non-`server` VMs act as collectors/forwarders
- `server` acts as the central backend, projection store, SSE server, and UI host
- v1 does not require automatic leader election or active-active replication

## Storage Model

Use one SQLite file, for example:

- `~/.local/state/klimkit/switchboard2/state.sqlite3`

Tables:

### `sources`

Tracks file-tail progress.

Columns:

- `source_id`
- `machine_id`
- `source_kind` (`rollout`, `session_index`, `hook_events`)
- `path`
- `inode`
- `size`
- `offset`
- `last_line_no`
- `last_seen_at`
- `parser_version`

### `events`

Append-only normalized event log.

Columns:

- `event_id`
- `machine_id`
- `session_id`
- `turn_id`
- `sequence_no`
- `event_at`
- `ingested_at`
- `event_family`
- `event_kind`
- `state_hint`
- `summary`
- `detail_json`
- `raw_ref`

Notes:

- `detail_json` stays intentionally small.
- Do not store giant assistant prose by default in this table.
- `raw_ref` points to a file offset or optional raw-event sidecar if deeper inspection is needed.

### `sessions`

Current projection per session.

Columns:

- `session_id`
- `machine_id`
- `title`
- `cwd`
- `workspace_name`
- `branch`
- `originator`
- `source_client`
- `approval_policy`
- `current_state`
- `state_since`
- `last_event_at`
- `last_attention_at`
- `last_sort_at`
- `latest_event_id`
- `latest_event_kind`
- `latest_event_summary`
- `needs_attention`
- `attention_kind`
- `seen_at`
- `archived`
- `archived_at`
- `sync_health`
- `sync_health_reason`
- `reported_stale_at`
- `ui_rank`

### `session_turns`

Minimal turn index for debugging and mapping.

Columns:

- `turn_id`
- `session_id`
- `machine_id`
- `started_at`
- `completed_at`
- `terminal_state`

### `machine_health`

Columns:

- `machine_id`
- `hostname`
- `last_event_at`
- `last_ingest_at`
- `collector_version`
- `sync_health`
- `sync_health_reason`

### `ui_metadata`

Switchboard-owned metadata only.

Columns:

- `session_id`
- `machine_id`
- `archived`
- `pinned`
- `created_locally`
- `manual_rank`
- `last_viewed_at`

## Session State Model

States:

- `idle`
- `starting`
- `planning`
- `working`
- `needs_input`
- `awaiting_approval`
- `done`
- `errored`
- `stale`
- `archived`

Rules:

- `archived` is an overlay, not the core runtime state.
- `stale` is explicit and must never be silently rewritten to `idle`.
- `needs_input` and `awaiting_approval` outrank `working`.
- `planning` is distinct from `working` when Codex is producing or updating a plan without execution yet.
- `done` is attention-worthy until the user opens the tab.
- opening the tab marks the latest completion as seen, but does not rewrite the session's true terminal state.
- a seen completion may still render as `done`, but without the hot attention treatment.

### Attention overlay model

Attention is separate from runtime state.

Overlay fields:

- `needs_attention`
- `attention_kind`
- `seen_at`

Allowed `attention_kind` values:

- `completion_unseen`
- `needs_input`
- `awaiting_approval`
- `error`

Rules:

- `done` creates `attention_kind = completion_unseen` until the user clicks into that session.
- clicking the tab records `seen_at` for the current latest event and clears `needs_attention` for that completion.
- a later completion creates a new unseen completion attention event.
- `needs_input`, `awaiting_approval`, and `error` remain attention-worthy until resolved, not merely seen.
- tab ordering uses `needs_attention` first, so an unseen completion still moves left.

### State derivation priority

Highest to lowest:

1. `errored`
2. `awaiting_approval`
3. `needs_input`
4. `planning`
5. `working`
6. `done`
7. `stale`
8. `starting`
9. `idle`

### Transition examples

- `task_started` -> `starting`
- first execution or active reasoning after start -> `working`
- `plan_update` or `plan_delta` without waiting/approval -> `planning`
- `function_call(request_user_input)` -> `needs_input`
- `exec_approval_request` or `apply_patch_approval_request` -> `awaiting_approval`
- `task_complete` -> `done`
- no fresh events past machine/session freshness threshold -> `stale`

### Sorting rule

Tabs reorder on every meaningful transition using:

- `needs_attention` first
- then current state priority
- then `last_sort_at`

`last_sort_at` updates when:

- the state changes
- the session receives a new attention-worthy event
- archive status changes

This is the direct fix for "move left when state changes".

## Live Update Model

Polling is not the primary mechanism.

Switchboard2 exposes:

- `GET /switchboard2/api/state`
- `GET /switchboard2/api/catalog?limit=20&cursor=...`
- `GET /switchboard2/api/active?limit=20&cursor=...`
- `GET /switchboard2/api/stream`
- `POST /switchboard2/api/archive`
- `POST /switchboard2/api/unarchive`
- `POST /switchboard2/api/events`

### SSE stream

`/api/stream` emits compact events such as:

- `session_upsert`
- `session_archive_changed`
- `session_removed`
- `machine_health`
- `notification`

Payloads contain only projection deltas, not full snapshots.

Expected behavior:

- local file append
- collector normalizes event
- projection updates
- SSE message emitted
- tab moves left instantly if sort key changed

### Active tab window

To keep boot fast with hundreds of sessions, the backend provides an active-window endpoint.

Rules:

- initial load returns only the first `N` active sessions by `ui_rank`
- default `N` is `20`
- response includes `next_cursor`
- UI can request more only when the user scrolls or asks for more
- SSE events may insert a newly important session into the active window immediately

This keeps first paint fast without sacrificing correctness.

## Notifications

Notifications move to server-owned transition logic.

Notification-worthy transitions:

- `working -> needs_input`
- `working -> awaiting_approval`
- `working/planning -> done`
- `any -> errored`

Do not infer notifications from front-end polling gaps.

Sources:

- rollout-derived transitions
- optional hook hints

Hooks remain useful for out-of-band delivery, but the board must not depend on them for correctness.

## Ingestion Strategy

### Local rollout ingestion

Use incremental file tailing with persistent checkpoints.

Requirements:

- never reread multi-megabyte rollout files from the top on every tick
- tolerate partial final lines
- commit checkpoints only after a line parses cleanly
- handle file rotation and compaction
- process only appended bytes

Preferred approach:

- watch active directories
- on change, read from saved offset
- buffer incomplete trailing line until next append
- normalize line-by-line

### Hook event ingestion

Treat `~/.codex/switchboard/events.jsonl` as a low-latency hint stream.

Use it for:

- faster `done`
- faster `needs_input`
- mobile/Telegram notification fanout

Do not let hook-only data override newer rollout truth.

### Remote VM ingestion

Remote satellites send compact normalized events to:

- `POST /switchboard2/api/events`

Requirements:

- idempotent by `(machine_id, event_id)`
- signed or restricted by Tailscale network boundary in v1
- append-only
- projection updated on ingest
- expected default target is the Switchboard2 backend running on `server`

Do not accept giant remote snapshots.

## Performance Targets

### Latency

- Same-VM file append to visible UI update: p95 under 250 ms, target under 100 ms
- Remote VM ingest to visible UI update: p95 under 750 ms
- Initial state endpoint for 200 sessions: p95 under 120 ms server time

### Memory

- API + collector combined RSS under 80 MB at 500 sessions and 100k normalized events
- steady idle memory growth must be near-flat over time
- no in-memory full-history reconstruction per request

### CPU

- idle collector CPU effectively near zero between file changes
- no periodic whole-database rescans

## API Compatibility Layer

First implementation goal is not a new frontend. It is a new backend that can feed the current UI.

Therefore Switchboard2 should expose a compatibility shape matching the current board as closely as possible:

- top active sessions
- catalog pagination
- archive/unarchive
- latest event summary
- current status
- unseen completion / seen state
- machine info

New fields can be additive:

- `sync_health`
- `state_since`
- `awaiting_approval`
- `planning`
- `stale_reason`
- `needs_attention`
- `attention_kind`
- `seen_at`

The UI can ignore them until we wire them in.

## UI Contract Changes Needed Later

The current UI should eventually change in these ways:

1. subscribe to SSE instead of relying on frequent full-state polling
2. sort by backend-provided rank, not frontend heuristics
3. render richer states directly
4. stop rewriting stale sessions to `idle`
5. render `done` with a strong completion color and indicator while `attention_kind = completion_unseen`
6. clear completion attention when the user clicks the tab
7. request more active tabs on demand from the active-window endpoint
8. request more catalog pages on demand

But those are phase-two UI changes. The backend must be correct before they matter.

## Archive Model

Archive is Switchboard metadata, not a mutation of Codex source files.

Rules:

- archiving updates `ui_metadata.archived`
- archived sessions disappear from active tabs
- catalog can show archived entries separately
- archive state is sticky across restarts
- remote events for an archived session still update its projection, but the UI keeps it archived unless explicitly unarchived

## Failure Handling

### Parse failures

- keep source checkpoint before the bad line
- quarantine malformed lines in a side log
- expose parse error counters via health endpoint
- do not poison the whole collector process

### Staleness

Machine health and session health are explicit.

Examples:

- `healthy`
- `lagging`
- `offline`
- `parse_error`
- `replaying`

If local collector stops receiving events but active sessions exist, mark them `stale`, never `idle`.

### Version tolerance

Normalize unknown event kinds into:

- `event_family = "unknown"`
- `event_kind = raw kind`

Store them without crashing, then let projection ignore or later learn them.

## Observability

Expose:

- `GET /switchboard2/api/health`
- `GET /switchboard2/api/debug/session/<id>`
- `GET /switchboard2/api/debug/machine/<id>`

Metrics to surface:

- collector lag in ms
- SSE subscriber count
- parse errors by source
- events ingested per minute
- projection update latency
- SQLite size and WAL size

## Proposed Code Layout

Initial layout under `src/klimkit/apps/switchboard2`:

- `spec.md`
- `README.md`
- `server.py`
- `collector.py`
- `normalize.py`
- `projector.py`
- `storage.py`
- `api.py`
- `sse.py`
- `models.py`
- `config.py`
- `notifications.py`
- `tests/`

Optional later:

- `satellite.py`
- `migrations/`

## Build Phases

### Phase 1: local single-machine correctness

- new SQLite store
- rollout tailer
- session projection
- compatibility API
- SSE updates
- archive persistence
- explicit stale state

Acceptance:

- this VM alone works correctly
- no same-origin helper required for correctness
- status changes appear immediately

### Phase 2: richer states and notifications

- `planning`
- `awaiting_approval`
- server-side notification transitions
- debug endpoints

### Phase 3: remote satellites

- remote event ingest
- multi-machine catalog
- machine health model
- hub-and-spoke deployment with `server` as the central backend

## Test Plan

### Unit tests

- line parser tolerance for partial JSONL lines
- normalization of known row families
- projection transitions for every state
- archive metadata behavior
- sort rank updates on state change

### Integration tests

- append lines to a fake rollout and assert SSE delta order
- simulate `request_user_input` and confirm `needs_input`
- simulate approval request event and confirm `awaiting_approval`
- simulate `task_complete` and confirm `done`
- simulate collector silence and confirm `stale`

### Load tests

- 200 sessions cold start
- 500 sessions projection query
- large active rollout file with append bursts

### Manual proof later

Before replacing the current board:

- cold boot on this VM
- live status transitions while Codex runs
- `done` renders as unseen attention until clicked
- clicking the tab clears the completion attention state
- archive/unarchive
- restart persistence
- notifications
- multi-VM ingest over Tailscale

## Key Decisions

1. SQLite + WAL is the right first datastore.
   It gives durability, transactions, tiny operational overhead, and small memory use.

2. SSE is the right first realtime transport.
   It is simpler than WebSockets, perfectly adequate for one-way board updates, and easy to proxy.

3. Rollout tailing is the real backbone.
   Hooks are too sparse and too stop-oriented to power a live board.

4. Projection tables are mandatory.
   The UI must never force a whole-history reparse or a giant snapshot rebuild.

5. Staleness must be explicit.
   Silent fallback to `idle` is unacceptable because it destroys trust.

## Open Questions For Review

1. After a user clicks a completed tab, should it render as a muted `done` state or as a distinct `seen` state?
2. What exactly marks a completion as seen: selecting the tab, focusing the app with that tab active, or keeping it open for a minimum dwell time?
3. Should `needs_input` and `awaiting_approval` stay hot even after you click them, until the underlying condition is actually resolved?
4. Should archived sessions still raise notifications for `done`, `needs_input`, and `awaiting_approval`, or should archive suppress all attention behavior?
5. For `planning`, should it apply only while Codex is actively building or updating a plan, or also while it is paused waiting for plan approval?
6. For approvals, do you want one combined `awaiting_approval` state, or separate `tool_approval` and `patch_approval` states?
7. Is `server` allowed to be the only primary backend in v1 with no failover, as long as every other VM buffers and retries delivery while it is unavailable?
8. Roughly how many VMs do you expect, and what is the upper bound for simultaneously active Codex sessions across all of them?
9. How long should normalized event history be retained on `server`: 7 days, 30 days, 90 days, or until manual cleanup?
10. Should non-`server` daemons persist an outbound queue locally so no events are lost if `server` is temporarily unreachable?
11. Should clicking a tab also clear desktop or Telegram notification state, or only the visual hot state inside Switchboard?
12. Do you want branch and path metadata to update live in the hot path too, or should the hot path focus only on title, state, and attention?
13. Is fastest delivery inside this repo the top priority, or are you willing to accept more implementation complexity for a lower-RSS compiled daemon?

## Recommended Stack

Current recommendation unless your answers change the constraints:

- language: `Python 3.12+`
- package and task runner: `uv`
- service model: `systemd --user`
- HTTP stack: `Starlette` + `uvicorn`
- realtime transport: `SSE`
- storage: stdlib `sqlite3` in `WAL` mode
- file watching: `watchfiles`
- data modeling: `dataclasses` and `TypedDict`
- tests: `pytest`
- remote ingress security: Tailscale reachability plus shared token or HMAC
- frontend: keep current vanilla JS/CSS UI and switch it to SSE plus backend ranking

### Why this stack

- `Python` fits the current repo, current operational model, and the actual workload, which is JSONL parsing, SQLite projections, and streaming HTTP.
- The biggest wins here come from incremental ingestion and projection design, not from a lower-level language.
- Avoiding an ORM and avoiding heavyweight validation libraries keeps memory lower and the hot path simpler.
- `SSE` is enough for one-way board updates and is simpler than WebSockets.
- SQLite in `WAL` mode is the simplest durable store that still performs well for this shape of write-heavy local event ingestion plus read-heavy projection queries.

### Stack alternatives

- If the absolute top priority becomes smallest RSS and easiest static deployment, the strongest alternative is `Go`.
- I do not currently recommend `Rust` for v1 because it will slow delivery materially without solving the core architectural problems better than a disciplined Python implementation.

## Recommended Next Build Order

After spec approval, I recommend building in this order:

1. storage + migrations
2. rollout collector with checkpoints
3. normalizer + projector
4. compatibility API
5. SSE stream
6. local UI hookup
7. notification layer
8. remote satellite ingest

## Review Summary

This design replaces snapshot syncing with a compact event pipeline:

- rollout tailer as source of truth
- SQLite projection store
- SSE for instant UI updates
- explicit rich states
- archive as metadata
- remote VMs sending normalized events, not bulky snapshots

That is the shortest path to a board that feels fast, uses little memory, and stops lying about agent state.
