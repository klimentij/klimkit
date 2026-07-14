# AGENTS.md

Repository-local instructions for Klimkit. These supplement the shared home-level agent instructions.

## Work log (docs/work)

Substantial human+agent work is journaled live in `docs/work/<NNN-DDMMYY-slug>/` (see
[docs/work/README.md](docs/work/README.md)). While working on such a piece: keep the
current phase folder's `LOG.md` updated as beats happen (timestamp, one-liner, who drove,
file links), preserve **every human message verbatim in exactly one** fitting markdown of
the work folder, and open a new `NNN-DDMMYY-slug/` phase folder when the work enters a new
logical iteration. Never bulk-load `docs/work/` into context — read a `LOG.md`, descend
selectively.

## Agent state (docs/agents)

Project-level agent state lives in `docs/agents/`:

- `docs/agents/memory.md` — durable preferences, corrections, and process rules.
- `docs/agents/log.md` — timestamped action history.
- `docs/agents/reflection.md` — append-only cross-task synthesis.

## Main Release Reminder

After every commit that lands on `main`, create a GitHub release for that commit and mark it as the latest release. Use the next patch version tag unless Klim specifies another version.
