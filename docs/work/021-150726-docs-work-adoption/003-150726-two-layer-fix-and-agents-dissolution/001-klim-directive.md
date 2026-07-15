# Klim's directive — two-layer folders, dissolve docs/agents

Received 2026-07-15, verbatim:

> i deisgned originally in sellify 2 layer folders under root, not one! with 1 it's too wide and flat; fix migration and instructions everywhere
>
>
> ---
>
> Project-level agent state lives in `docs/agents/`:
>
> - `docs/agents/memory.md` — durable preferences, corrections, and process rules.
> - `docs/agents/log.md` — timestamped action history.
> - `docs/agents/reflection.md` — append-only cross-task synthesis.
>
>
> no need for old memory log reflections - migrate them to new /work structure. log merrged smartly; memory and reflections can be transformed into notes under related work or subwork folders
>
> --

Two rulings:

1. **Always two folder layers under `docs/work/`** — work folder → phase folders →
   artifacts. Flat work folders (files directly inside) are wrong; the migrated legacy
   folders must be restructured into phases, and the instructions must say so everywhere.
2. **`docs/agents/` is retired.** No separate memory/log/reflection state files: the
   action log merges into the work/phase `LOG.md` files, and memories/reflections become
   numbered notes under their related work or phase folders.
