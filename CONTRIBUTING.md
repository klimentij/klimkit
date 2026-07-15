# Contributing

Keep changes small, previewable, and easy to verify. For non-trivial work, journal it in the docs-first work layout: one `docs/work/<NNN-DDMMYY-slug>/` folder per piece of work, phase subfolders per logical human+agent iteration (artifacts always inside a phase — two folder layers under `docs/work/`, never flat), `LOG.md` at both levels, and plain numbered artifacts (`001-…`) with no authorship prefixes — the LOG carries who drove each beat. See [docs/work/README.md](docs/work/README.md) for the one-page convention and [AGENTS.md](AGENTS.md) for the live-journaling rules.

There are no separate memory/log/reflection state files: action history lives in the `LOG.md` files, reflections and durable decisions are numbered notes inside the fitting work phase, and rules that must bind every future session graduate into [AGENTS.md](AGENTS.md).

Use the repo's existing stdlib test harness:

```bash
python3 -m unittest discover -s tests -q
```

Optional Codex smoke validation is skipped unless explicitly enabled:

```bash
KLIMKIT_RUN_CODEX_SMOKE=1 python3 -m unittest tests.test_codex_smoke -q
```

Keep work notes, agent state files, and Git-trackable self-contained report HTML tracked when they explain a task, plan, proof, or decision. Do not commit anything under a `.local/` folder, raw transcripts, build artifacts, or large report media unless a change explicitly needs a sanitized fixture; the soft budget is ≈300 KB per work folder.

Legacy runtime instructions (`kk`, Switchboard, `packs/codex/`, team-workflow migration) apply only to the code under `deprecated/runtime/` and are kept there for reference. Do not route new work through them.
