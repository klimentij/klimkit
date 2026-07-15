# Klimkit Artifact Workflow

Use these paths unless the repository has more specific instructions.

## Evidence Files

Klimkit's skills-first default is a docs-first work journal:

- `docs/work/<NNN-DDMMYY-slug>/`: one folder per piece of work, journaled live per
  `docs/work/README.md` — phase subfolders `<NNN-DDMMYY-slug>/` per logical human+agent
  iteration, `LOG.md` at both levels, plain numbered artifacts (`001-…`) with no
  authorship prefixes.
- **Always two layers**: artifacts live inside phase folders, never directly in a work
  folder. A work folder holds only its `LOG.md` and phases.

There are no separate memory/log/reflection state files: action history lives in the
`LOG.md` files, reflections and durable decisions are numbered notes inside the fitting
work phase, and rules that must bind every future session graduate into the repo's
`AGENTS.md`.

When `docs/work/README.md` is missing, use `klimkit-setup` to create the layout. Legacy
`.klimkit/` paths are readable historical context, not the default write target for new
skill-based work.

## Work Notes

- Record every human message verbatim into exactly one fitting note of the current work
  folder; the phase `LOG.md` carries who drove each beat (human / joint / agent-only).
- Open a new phase folder when the work enters a new logical iteration; a few short
  related turns share one.
- Keep implementation proof close to the phase that drove the work: name changed files,
  checks run, important outputs, skipped checks, and remaining risk.

## Local State

Do not commit machine-local runtime state, secrets, tokens, logs, or backups. Keep those
under `${XDG_STATE_HOME:-~/.local/state}/klimkit/` or a gitignored `.local/` folder
inside the relevant work folder.

## Reports

For UI or workflow proof, write self-contained single-file HTML reports as numbered
artifacts inside the phase folder. Keep large screenshots and videos in the gitignored
`.local/` folder unless they are irreproducible evidence. Render media full-width so it
can be inspected without opening thumbnails.

Deploy human-facing HTML through the harness's native hosted surface by default —
Claude Code's Artifact tool or Codex Sites, both authentication-protected and private
by default. Never enable public link sharing unless the user explicitly asks. Record
the deployed URL in the phase `LOG.md` next to the file link; use
`klimkit-report-server` only as the fallback when native hosting is unavailable.
