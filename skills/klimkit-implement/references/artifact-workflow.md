# Klimkit Artifact Workflow

Use these paths unless the repository has more specific instructions.

## Evidence Files

Klimkit's skills-first default is a docs-first layout:

- `docs/work/<NNN-DDMMYY-slug>/`: one folder per piece of work, journaled live per
  `docs/work/README.md` — phases inside as `<NNN-DDMMYY-slug>/` subfolders, `LOG.md` at
  both levels, plain numbered artifacts (`001-…`) with no authorship prefixes.
- `docs/agents/memory.md`: durable preferences, corrections, and process rules.
- `docs/agents/log.md`: timestamped action history.
- `docs/agents/reflection.md`: append-only cross-task synthesis.

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
