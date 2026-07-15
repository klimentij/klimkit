# Klimkit Artifact Workflow

Use these paths unless the repository has more specific instructions.

## Evidence Files

Klimkit's skills-first default is a docs-first work journal that any human or agent can browse:

- `docs/work/<NNN-DDMMYY-slug>/`: one folder per piece of work, journaled live — the
  original ask, decisions, proof, and reports. Governed by `docs/work/README.md`
  (create it from the template in this skill when missing).
- `docs/work/<work>/<NNN-DDMMYY-slug>/`: phase folders — one per logical human+agent
  iteration (design, grilling, build, review…), each with its own `LOG.md`.
- **Always two layers**: a work folder contains only its `LOG.md` and phase folders;
  artifacts never sit directly in a work folder. Even single-sitting work gets one phase.
- `LOG.md` at both levels: the work LOG has one entry per phase; the phase LOG has
  timestamped entries with a one-liner, who drove (human / joint / agent-only), and
  links to the exact files.
- Numbered artifacts (`001-…`, `002-…`) inside phases: distilled prose, verbatim human
  prompts, and self-contained HTML reports. No authorship prefixes in file names — the
  LOG carries who did what.

There are no separate memory/log/reflection state files. Action history lives in the
`LOG.md` files; reflections and durable decisions are numbered notes inside the fitting
work phase; preferences or process rules that must bind every future session graduate
into the repo's `AGENTS.md`.

Legacy `.klimkit/` layouts (flat or operator-scoped) may be read as historical context,
but new skills-first setup should not create them; offer to migrate them into
`docs/work/` instead.

## Work Journal Rules

- Record each human message verbatim into exactly one fitting note of the current work
  folder, and log every meaningful beat in the phase `LOG.md` — live, not after the fact.
- Raw transcripts, build artifacts, regenerable renders, and asset folders never enter
  git; soft budget ≈300 KB per work folder. Screenshots are tracked only when they are
  irreproducible evidence.
- Heavy, moment-useful material goes in a gitignored `.local/` folder inside the work
  folder (add `**/.local/` to `docs/work/.gitignore`).
- Deploy human-facing HTML (explainers, reports, dashboards) through the harness's
  native hosted surface by default — Claude Code's Artifact tool or Codex Sites, both
  authentication-protected and private/workspace-only by default. Never enable public
  link sharing unless the user explicitly asks; record the deployed URL in the phase
  `LOG.md` next to the file link.
- Never bulk-load `docs/work/` into context — read a `LOG.md`, descend selectively.

## Templates

Work-level LOG.md:

```markdown
# LOG — <NNN-DDMMYY-slug>

<one-paragraph summary of the piece of work>

- **MM-DD** [<NNN-DDMMYY-phase-slug>](<NNN-DDMMYY-phase-slug>/) — one-liner of the phase.
```

Phase-level LOG.md:

```markdown
# LOG — <NNN-DDMMYY-phase-slug>

- **YYYY-MM-DD HH:MM** (human|joint|agent) [001-note.md](001-note.md) — one-liner of the beat.
```

## Local State

Do not commit machine-local runtime state, secrets, tokens, logs, or backups. Keep those
under `${XDG_STATE_HOME:-~/.local/state}/klimkit/` or a gitignored `.local/` folder
inside the relevant work folder.
