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

## HTML reports and explainers — hosted, auth-protected

Any HTML meant for the human driver to view — explainers, proof reports, dashboards,
anything HTML in `docs/work/` — is deployed by default through the harness's native
hosted surface, not just left as a file:

- **Claude Code**: publish with the built-in Artifact tool (a claude.ai artifact —
  authenticated, private to the author by default; republishing updates the same URL).
- **Codex**: deploy with Codex Sites (OpenAI-hosted, workspace-authenticated, private
  by default; save a version, then deploy).

Always keep the default authenticated visibility — private or workspace-only. Never
enable public link sharing unless Klim explicitly asks. Record the deployed URL in the
phase `LOG.md` next to the file link. The git-tracked HTML in `docs/work/` remains the
source of truth; the hosted page is the viewing surface.

## Agent state (docs/agents)

Project-level agent state lives in `docs/agents/`:

- `docs/agents/memory.md` — durable preferences, corrections, and process rules.
- `docs/agents/log.md` — timestamped action history.
- `docs/agents/reflection.md` — append-only cross-task synthesis.

## Main Release Reminder

After every commit that lands on `main`, create a GitHub release for that commit and mark it as the latest release. Use the next patch version tag unless Klim specifies another version.
