---
name: klimkit-harness-cleanup
description: Audit and clean Codex and Claude Code customization across local computers, SSH hosts, containers, and VMs with a two-phase approval gate. Use when the user asks to inventory, compare, reset, consolidate, quarantine, remove, or troubleshoot agents, skills, instructions, hooks, MCP servers, plugins, worktrees, caches, or harness configuration on one or more machines.
---

# Harness Cleanup

Use a **two-key** process: discovery produces stable action IDs; explicit user approval unlocks only those IDs. Treat each machine as an independent transaction.

## Phase 1 — Discover, Research, Report

1. **Register targets.** List every local machine, SSH host, container, and VM in scope with its transport, OS, user/home, repository roots, and available privilege boundary. Ask only when the target set cannot be inferred safely.
   - Complete when every requested target is reachable or marked blocked with the exact reason.

2. **Refresh the surface map.** Read [references/surface-map.md](references/surface-map.md), detect installed Codex and Claude versions, and verify current discovery/configuration locations against official vendor documentation. Add version-specific or organization-managed surfaces before scanning.
   - Complete when every harness/version has dated source URLs and a search plan covering user, project, system, plugin, and runtime layers.

3. **Collect metadata read-only.** Run `scripts/inventory.py` locally on each target, transferring it ephemerally when necessary. Supplement it with read-only service/scheduler, process, package, environment-name, repository, worktree, symlink, and disk-usage checks. Record names, paths, hashes, ownership, tracking, precedence, and activation evidence; never emit secret values or configuration bodies from sensitive files.
   - Complete when every target and declared repository root is accounted for and scan gaps are explicit.

4. **Classify every row.** Use `authoritative`, `active`, `derived`, `cache`, `evidence`, `state`, `credential`, or `unknown`. Recommend `KEEP`, `QUARANTINE`, `DELETE`, `REMOVE_IN_CANONICAL_REPO`, or `MANUAL_REVIEW`, with reason, risk, rollback, and a stable action ID. Group duplicates by origin and hash; distinguish files that exist from configuration proven active.
   - Complete when every artifact and repository row has one recommendation and every mutation candidate has an action ID.

5. **Report and stop.** Follow [references/report-contract.md](references/report-contract.md). Include the full artifact table, repository census, machine summaries, proposed batches, exact effects, rollback plan, and blocked coverage. Phase 1 may write reports only to the agreed report workspace or temporary directory.
   - Complete when the user receives an approval ledger and the agent has performed no target mutation.

Ask the user to approve exact action or batch IDs. End the turn without executing them.

## Phase 2 — Execute Approved Actions

Start only after the user explicitly approves action or batch IDs from the current report.

1. **Lock scope.** Resolve the approval to the exact ledger rows and reject ambiguous additions. Recheck fingerprints, dirty repositories/worktrees, connectivity, free space, running sessions, and required privileges.
   - Complete when every approved row still matches its Phase 1 evidence; return stale rows to Phase 1.

2. **Stage rollback.** Create a unique private quarantine and append-only manifest on each affected machine. Preserve credentials, authentication, sessions, history, memories, system/admin policy, and built-in skills unless their exact removal was approved. Give every mutation a tested rollback or mark it as explicitly irreversible.
   - Complete when all approved actions have destinations, collision checks, permissions, and rollback instructions.

3. **Execute fail-closed.** Work machine by machine in this order: stop approved writers/synchronizers; quarantine global custom surfaces; edit mixed state surgically; change project configuration once in the canonical repository; perform explicitly approved deletions last. Stop that machine on any mismatch and do not widen scope. Prefer moves into quarantine over deletion.
   - Complete when every approved action is recorded as applied, skipped, stale, or failed—never silently omitted.

4. **Verify the clean state.** Check moved source/destination pairs, preserved state, file permissions, service/scheduler status, repository cleanliness, disk effects, and harness-native runtime views in fresh Codex and Claude sessions. Remove only temporary files created by this run.
   - Complete when every applied row has a passing postcondition or an exact failed check.

5. **Report execution.** Produce the final table, manifest locations, rollback commands, preserved-state evidence, unavailable checks, and actions still awaiting approval. Keep quarantine deletion and unrelated project cleanup behind new approval.

## Approval Contract

Accept approval only when it identifies the current scan and exact action or batch IDs, for example: `Approve scan 2026-07-11T08:00Z batches GLOBAL-QUARANTINE and STOP-WRITERS on devbox and vm-2.` Treat broader language as a request to clarify scope, not permission to mutate.

## Resources

- Read [references/surface-map.md](references/surface-map.md) whenever harness versions, operating systems, configuration layers, or activation checks differ.
- Read [references/report-contract.md](references/report-contract.md) before assigning recommendations, action IDs, approvals, manifests, or verification results.
- Run `python3 scripts/inventory.py --help` for the portable, metadata-only inventory helper. It does not execute cleanup actions.
