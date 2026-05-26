# Symphony, Klimkit, And The Next Autonomy Layer

Date: 2026-05-22
Author: Codex
Task type: research / strategic reflection

## Request

Klim asked for a deeper follow-up to the Symphony reflection: research the recent OpenAI Symphony post, reflect on it against Klim's own agentic-engineering thinking, inspect the `raw/` folder and index material, assess what a really good full-text search could look like, reconstruct Klim's trajectory across the years, and propose a high-level executive vision for moving Klimkit toward a Symphony-like autonomy layer. The specific strategy questions were whether to use Linear, GitHub Issues, GitHub Projects, a single huge issue repo, per-repo boards, or a third-party tracker, and whether GitHub Issues can support blocking dependencies like Symphony needs.

## Source-Read Manifest

External sources checked on 2026-05-22:

- OpenAI Symphony article, published 2026-04-27: https://openai.com/index/open-source-codex-orchestration-symphony/
- OpenAI harness-engineering article, published 2026-02-11: https://openai.com/index/harness-engineering/
- OpenAI Symphony repo: https://github.com/openai/symphony
- Local Symphony clone at `/tmp/openai-symphony`, commit `2c1851830477434100fdb8980fcc1fce1a8af81d`, latest local fetch on 2026-05-22.
- GitHub Issues dependencies docs: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies
- GitHub issue-dependencies REST docs: https://docs.github.com/en/rest/issues/issue-dependencies
- GitHub Projects docs: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- GitHub Projects single-select field docs: https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-single-select-fields
- Linear issue-relations docs: https://linear.app/docs/issue-relations

Klimkit sources read:

- `/home/ubuntu/klimkit/.klimkit/tasks/07-symphony-reflection/01-a-research-reflection.md`
- `/home/ubuntu/klimkit/.klimkit/memory.md`
- `/home/ubuntu/klimkit/.klimkit/log.md`
- `/home/ubuntu/klimkit/.klimkit/reflection.md`
- `/home/ubuntu/klimkit/README.md`
- `/home/ubuntu/klimkit/src/README.md`
- `/home/ubuntu/klimkit/src/klimkit/tools/supervisor/README.md`
- `/home/ubuntu/klimkit/src/klimkit/apps/switchboard/README.md`
- `/home/ubuntu/klimkit/src/klimkit/apps/switchboard/spec.md`

Klimkipedia and Klimki sources read:

- `/home/ubuntu/klimkipedia/raw/README.md`
- `/home/ubuntu/klimkipedia/wiki/index.md`
- `/home/ubuntu/klimkipedia/wiki/log.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/index.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/journey.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/concepts/agent-control-plane.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/concepts/worktree-oriented-supervision.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/concepts/hybrid-code-retrieval.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/summaries/solo-agentic-product-stack-2026.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/syntheses/control-plane-beside-the-ide.md`
- `/home/ubuntu/klimkipedia/wiki/agentic-engineering/questions/same-feature-parallel-agents.md`
- `/home/ubuntu/klimkipedia/wiki/knowledge-bases/summaries/klimkipedia-operating-model.md`
- `/home/ubuntu/klimkipedia/raw/other/2026/04/08/2026-04-08-2026-04-08-agentic-engineering-tooling-journey-memo-2ee25b58.md`
- `/home/ubuntu/klimkipedia/raw/other/2026/04/08/2026-04-08-2026-04-08t23-37-09z-kp-ingest-input-f8333090.md`
- `/home/ubuntu/klimkipedia/raw/other/2026/04/08/2026-04-08-output-7-e91539bf.md`
- `/home/ubuntu/klimkipedia/raw/other/2026/04/08/2026-04-08-output-8500e58d.md`
- `/home/ubuntu/klimki/src/experiments/sqlite_fts/README.md`
- `/home/ubuntu/klimki/src/experiments/qmd/README.md`
- `/home/ubuntu/klimki/src/backend/qmd_service.py`
- `/home/ubuntu/klimki/src/backend/qmd_worker.mjs`
- `/home/ubuntu/klimki/src/site/README.md`

## What Symphony Changes

The OpenAI Symphony post is not mainly about Linear, Elixir, or a dashboard. It is about changing the scarce resource. Interactive Codex usage makes the human manage sessions; Symphony makes the work item manage sessions. A ticket becomes the durable unit of orchestration, the daemon owns dispatch/retry/restart/handoff, and humans spend attention on task definition and review packets rather than on babysitting terminals.

This matters because Klimkit already solved many of the lower layers:

- reproducible operator repo and managed Codex harness;
- Switchboard as a tailnet control surface for workspaces and reports;
- per-worktree, per-branch, per-code-server workspace discipline;
- `.klimkit/tasks`, memory, log, reflection, proof reports, and final-review culture;
- Telegram/Tailscale attention links and long-run proof practices.

The missing layer is not "more tabs." It is eligibility, claiming, dependency ordering, retries, and review packets around durable work items. Symphony's strongest product insight is that a project board can become a scheduler, but Klimkit's strongest implementation advantage is that it already has the local evidence spine Symphony needs after a run finishes.

## Klim's Trajectory Across The Years

The Klimkipedia journey map shows that this direction did not start with Symphony:

| Period | Operating mode | Main constraint discovered |
| --- | --- | --- |
| circa 2024-04 | Cursor locally on Mac, 1-2 parallel chats, mostly Sonnet 3.5 | local chat was useful, but parallelism was limited |
| circa 2025-10 | more Cursor chats, stronger models, still no worktrees | agents collided in the same checkout |
| circa 2026-01 | OpenCode on a work GCP VM, Mac web UI, worktrees | remote execution helped, but control and observation were still weak |
| circa 2026-02 | Discord to OpenCode via Kimaki, per-worktree stacks, Tailscale, code-server, proof experiments | proof-of-execution remained hard, and messaging was not a canonical cockpit |
| circa 2026-03 | remote OpenCode UI again, long-session slowness, research into bigger IDE/control-plane patterns | one giant agent UI was the wrong abstraction |
| 2026-04 | split stack: local Codex for light wiki work, Telegram Hermes on personal VM, per-tree code-server/Codex sessions for product work | the worktree became the unit of execution, but the human still dispatched and tracked work |
| 2026-05 Klimkit | Switchboard, proof reports, final-review/checklister/reflector harness, Tailscale notifications, 5-7 workspace practice | the control plane sees sessions and workspaces, but not yet an issue-level DAG of work |

The through-line is consistent: every phase externalized one more part of agentic work out of the model's fragile chat context and into a durable system boundary. Worktrees externalized edit isolation. Code-server externalized file access. Tailscale externalized reachability. HTML reports externalized proof. `.klimkit/tasks` externalized plans and checklists. Switchboard externalized session visibility. The Symphony-shaped move is to externalize dispatch and dependency management.

This also reframes the same-feature parallel-agents question. In April, the open question was whether two or three agents should compete on one feature and a boss agent or human should compare outputs. Symphony gives that idea a better operating substrate: a parent planning issue can spawn child experiment issues, encode dependencies, run candidates in separate worktrees, and return a comparison packet rather than making same-feature parallelism a one-off manual trick.

## Raw Folder And Index Findings

Klimkipedia's `raw/` is large enough that "just grep it" remains useful but is no longer enough as the only long-term interface.

Observed local corpus state:

- `raw/`: `3.2G`, `15,841` files total, `9,102` markdown files.
- `raw/chatgpt/`: `6,029` markdown conversation exports from 2023-02-07 through 2026-04-10.
- `raw/codex/`: `3,032` markdown Codex session exports from 2025-10-06 through 2026-05-03.
- `raw/other/`: `40` dated markdown sources from 2026-04-08 through 2026-04-17.
- `raw/telegram/`: `6,738` complete export files, `566M`; `result.json` covers `947` chats and `165,563` messages from 2015-06-24 through 2026-04-10.
- `wiki/`: `89` markdown files, `736K`, the selective compiled layer.

The root `wiki/index.md` is already doing the right job: it is a content map, not an evidence dump. It routes into topic indexes, canonical pages, journeys, summaries, comparisons, and questions. The Agentic Engineering section is especially relevant because it already contains the trajectory, control-plane, retrieval, worktree, proof, and same-feature-parallelism pages needed for this Symphony reflection.

The search experiments already point to a practical answer:

- SQLite FTS5 over the full 2026 raw markdown corpus indexed `567` files into `32,838` chunks in `4.30s`, with an `86.73 MB` DB. Its failure modes were legible: sibling confusion, abstract paraphrases, and noisy transcript chunks.
- QMD lexical indexing over full `raw/` indexed `6,058` markdown files in `31.99s`, producing about a `500 MB` local index. It was strong on exact titles and mechanism-heavy queries, weak on short abstract paraphrases and generic vocabulary.
- MemPalace was not a good default for this corpus: after roughly 18 minutes, it had only indexed `33` March 2026 sources in the tested run.
- Klimki already has a QMD service wrapper with BM25, semantic, and hybrid modes, but its default collection is wiki-oriented. That is good for a reading/search UI, but the raw corpus needs a separate, explicitly designed evidence index.

## What A Really Good Full-Text Search Should Be

The best next search layer is not a pure vector database. It should be a staged retrieval system with the compiled wiki in front and raw evidence behind it:

1. **Canonical-first routing.** Query `wiki/index.md`, topic indexes, and canonical wiki pages first so the user or agent sees Klim's maintained interpretation before raw transcript noise. Return raw evidence only as support or as a "dig deeper" path.
2. **SQLite FTS5 as the raw workhorse.** Build a first-class all-raw SQLite FTS index, not just the 2026 experiment. Keep it local, cheap to rebuild, inspectable, and scriptable. Use field weighting for title/path/frontmatter/body and coverage-aware reranking, because that beat generic BM25 on this corpus.
3. **Turn-aware chunking.** Chunk ChatGPT and Codex markdown by conversation turn/message boundaries where possible, not by fixed characters only. Store source, year, title, role, model, date, message number, and original path so a result can be opened and cited.
4. **Transcript-noise controls.** Index assistant/user/tool/thought sections separately. Default user-facing search should demote thoughts, raw tool dumps, and repetitive web captures; forensic search can opt into them.
5. **Telegram extraction.** Do not index Telegram HTML dumps or `__MACOSX` files as raw text. Parse `result.json` into message-level records with chat, date, sender, reply/media metadata, and privacy filters. Media OCR/transcription can be a later opt-in layer.
6. **Hybrid recall, not vector mysticism.** Add QMD/sqlite-vec embeddings for wiki pages and selected raw chunks after lexical candidate generation. Use semantic retrieval for paraphrase recall and rerank the top candidates, not as the only source of truth.
7. **Agent context packs.** For Symphony-like work items, the orchestrator should query Klimkipedia before dispatch and attach a small context pack to the `.klimkit/tasks/<item>/` folder: canonical pages, relevant raw snippets, prior related tasks, and known preferences.
8. **Search observability.** Record queries, selected hits, opened files, and misses into a local search log. The current wiki log already shows that misses are valuable: they reveal when canonical pages, indexes, or search ranking need maintenance.

Concrete implementation path:

- In `~/klimki`, promote the SQLite FTS experiment into maintained backend code first.
- Add `kp search` / HTTP search endpoints that search `wiki` and `raw-md` collections separately.
- Add a Telegram `result.json` extractor into a private, local-only `raw-telegram` index.
- Keep Hugo/Pagefind-style static search for the small public `wiki/` surface only; do not ship the full raw private corpus into a static browser index.
- Once lexical search is stable, layer QMD hybrid search or `sqlite-vec` over candidate sets for paraphrase and "what was my old thinking on X?" queries.

## Tracker And Board Strategy

### Linear

Linear is the cleanest match to Symphony as published. It has project-centric boards, states, priority, branch metadata, strong issue relations, GitHub PR attachments, polished mobile entry, and a workflow shape that non-engineering collaborators can use. Symphony's reference workflow is built around Linear states such as `Todo`, `In Progress`, `Human Review`, `Merging`, and `Rework`, plus a persistent Linear workpad comment.

But Linear should not be Klimkit's required default. Klimkit's public model is fork-first, repo-local, GitHub-adjacent, and evidence-driven. Requiring Linear would add another account, token, API, billing surface, and sync boundary before the core product has proven its own orchestration loop.

Recommendation: keep Linear as a first-class future adapter, not the first dependency.

### GitHub Issues And GitHub Projects

GitHub is feasible. As of the docs checked on 2026-05-22, GitHub Issues supports sub-issues, issue dependencies, issue dependencies are available on Free/Pro/Team/Enterprise Cloud, and GitHub has REST endpoints to list/add/remove `blocked_by` and `blocking` relationships. GitHub Projects supports table/board/roadmap views, custom fields, single-select fields, automation, and GraphQL API automation.

The practical gap is not blocking dependencies. The gap is workflow-state ergonomics:

- a GitHub issue is basically open/closed, so Symphony states need Projects fields, labels, issue fields, or a `.klimkit` state mirror;
- issue numbers are repo-scoped, so the orchestrator needs canonical IDs like `owner/repo#123`;
- Projects API mapping is more complex than a Linear project query;
- GitHub has PR/CI/review context natively, but agent-visible project metadata needs careful adapter code.

Recommendation: use GitHub Issues as the default work-item system, GitHub Projects as the optional board/state layer, and labels as the fallback for simple repos.

### Single Huge Issue Repo

Do not make one giant repo with issues for all work across all companies and products. It centralizes visibility at the cost of code adjacency, permissions, PR linking, CI context, company boundaries, and future contributor clarity. It also makes private cross-company work dangerously easy to mix.

A small "operator hub" repo can exist for meta-work that genuinely has no code home, but code changes should live as issues in the repo that owns the code.

### One Board Per Repo

One board per repo is also too fragmented as the default. It makes local execution simple, but it hides cross-repo dependencies, portfolio priorities, and "what should run next?" visibility. It also turns orchestration into dozens of little cockpits.

The better shape is repo-local canonical issues plus aggregated views:

- each code repo owns its implementation issues and `.klimkit/tasks` evidence;
- each product/company/org has an aggregate GitHub Project or Linear board;
- Klimkit can poll multiple repos/projects and normalize items into one scheduler view;
- Switchboard shows the scheduler view, worktree/session state, PR/proof links, and blockers;
- repo-local Project views are optional convenience views, not the main source of truth.

For Klim personally, split aggregate boards by trust boundary:

- one personal/Klim operator board for Klimkit, Klimkipedia, personal systems, and experiments;
- one board per company/product group where access and confidentiality differ;
- no cross-company board unless it stores only links or intentionally public/meta tasks.

### Third-Party Tracker

A third-party tracker is worth it only when the planning surface matters more than the code adjacency: product/design collaborators, roadmap reporting, non-GitHub users, or cross-company task intake. For the next Klimkit rewrite, that is premature. Design the adapter boundary so Linear or another tracker can be added cleanly, but make GitHub/local `.klimkit` the path that works out of the box.

## Proposed Klimkit Architecture

Build a `Klimkit Orchestrator` layer above Switchboard, not a replacement for Switchboard.

Core components:

- `WorkItem` adapter contract: `local-klimkit`, `github-issues`, `github-projects`, later `linear`.
- `Scheduler`: polls eligible items, checks blocked dependencies, owns claims, retries, backoff, cancellation, and stale-run recovery.
- `Workspace manager`: creates one worktree per work item, maps item ID to path, branch, code-server URL, app ports, and proof/report paths.
- `Agent runner`: launches Codex app-server or terminal/IDE-mode sessions with the repo harness and a generated work-item prompt.
- `Evidence writer`: creates/updates `.klimkit/tasks/<item>/` with prompt, checklist, status, run log, proof links, PR links, and final handoff packet.
- `Context packer`: queries Klimkipedia/repo docs/GitHub history and writes a bounded context bundle before agent dispatch.
- `Switchboard integration`: adds an orchestration view beside current workspace tabs: queued, running, blocked, human-review, rework, merging, done.
- `Safety boundary`: starts with Human Review as the terminal success state. Merge automation comes later, after the dispatch/retry/proof loop is boring.

Likely first implementation stack:

- Python stdlib plus `sqlite3` for scheduler state, matching Klimkit's current implementation style.
- `gh` CLI plus GitHub REST/GraphQL APIs for issues, PRs, checks, Projects, and dependencies.
- Git worktrees and existing `examples/create-worktree.sh` logic as the workspace creation base.
- Codex app-server mode where available; otherwise Switchboard-launched Codex/code-server sessions as the first runner.
- `.klimkit/state/orchestrator.sqlite3` for ignored runtime state.
- `.klimkit/tasks/<work-item>/` for durable evidence.
- `WORKFLOW.md` or `.klimkit/orchestrator/workflow.md` per repo for the agent policy layer.
- Tailscale Serve and existing Switchboard report serving for proof handoff.
- `agent-browser`/Playwright/browser proof where UI work is involved.

Milestones:

1. Local queue: `.klimkit/tasks/**` items can be marked eligible and launched into worktrees from Switchboard.
2. GitHub Issues adapter: labels or issue fields drive `kk:queued`, `kk:running`, `kk:human-review`, `kk:blocked`, `kk:done`.
3. GitHub Projects adapter: board status/priority fields become the richer workflow-state source.
4. Dependency gating: GitHub issue dependencies and/or local `.klimkit` blockers prevent dispatch until blockers are terminal.
5. Review packet: every completed run returns branch, PR, test evidence, screenshots/videos when relevant, and a concise task note.
6. Rework loop: review comments or `kk:rework` put the issue back into a fresh attempt.
7. Merge shepherding: only after the above works, add CI watch/rebase/retry/merge loops.

## Executive Vision Paragraph

Klimkit should become the operator-owned Symphony for a solo builder and small trusted teams: a local-first orchestration layer where GitHub issues, repo-local `.klimkit` tasks, and eventually Linear tickets become runnable work items; Klimkit claims eligible work, creates isolated worktrees and app surfaces, launches Codex with repo-specific harnesses and Klimkipedia context packs, tracks blocker DAGs and run state in Switchboard, and returns proof-rich human-review packets instead of asking Klim to babysit sessions. The implementation should start with GitHub Issues plus optional GitHub Projects because that keeps work beside code, PRs, CI, permissions, and fork-first open-source adoption, while preserving an adapter boundary for Linear where its project-management ergonomics are genuinely useful. The structural bet is not one giant issue repo or dozens of isolated Kanban boards, but repo-local canonical issues aggregated into company/product-level orchestration views, with `.klimkit/tasks` remaining the durable evidence spine and Human Review as the first autonomy ceiling.

## Decision Recommendation

Default now:

- GitHub Issues as canonical work items.
- GitHub Projects for aggregate board/state where useful.
- Labels as fallback state for small repos.
- GitHub issue dependencies as the first blocker mechanism.
- `.klimkit/tasks` as local durable evidence and recovery state.
- Switchboard as the human control surface.

Avoid now:

- one global issue repo for all work;
- mandatory Linear;
- fully autonomous merge-to-main;
- raw-corpus vector search as the first retrieval layer;
- per-repo boards as the only orchestration surface.

Keep open:

- Linear adapter once the core orchestrator works;
- same-feature parallel issue trees for broad solution-space tasks;
- semantic/reranked search after a maintained FTS base exists;
- merge shepherding after Human Review handoffs are consistently reliable.

## Next Concrete Spec

The next useful artifact should be a small implementation spec, not code:

- define `WorkItem` fields and state transitions;
- define the `.klimkit/tasks/<item>/` evidence schema;
- define GitHub label/Project/issue-field mappings;
- define dependency-read behavior for GitHub REST issue dependencies;
- define claim/retry/cancel semantics;
- define first Switchboard orchestration UI states;
- define the local queue milestone separately from the GitHub adapter milestone;
- explicitly state that `Done` means "ready for human review" until merge automation is proven.
