# Report and approval contract

## Phase 1 report

Create one machine register and two exhaustive tables: artifacts and repositories/worktrees. Keep secret contents out of every report.

### Machine register

| Field | Requirement |
|---|---|
| Machine | Stable user-facing label and hostname/instance identifier. |
| Transport | Local, SSH target, container/provider command, or blocked. |
| Platform | OS, architecture, home, effective user, harness versions. |
| Search roots | Home, repository roots, system/admin roots, mounted volumes. |
| Coverage | Complete, partial with exact exclusions, or blocked with reason. |

### Artifact rows

Include: machine, path, harness, layer/scope, artifact type, classification, repository/origin, tracked state, symlink target, owner/mode, size/mtime, non-sensitive hash, sensitive flag, activation evidence, recommendation, risk, reason, rollback, and action ID.

### Repository/worktree rows

Include: machine, path, origin, branch/HEAD, dirty state, ahead/behind or merged evidence, artifact count, duplicate group, recommendation, reason, and action ID when mutation is proposed.

### Stable action IDs

Set `scan_id` to the UTC scan timestamp plus a short report hash. Generate each action ID from the first 12 hex characters of:

```text
sha256(scan_id + NUL + machine + NUL + canonical_path + NUL + recommendation)
```

Prefix artifact actions with `A-`, repository actions with `R-`, and service/writer actions with `S-`. Never reuse an ID after its row evidence changes.

### Recommendations

- `KEEP`: preserve authoritative, built-in, managed, required, or valuable state.
- `QUARANTINE`: reversible removal from discovery/activation with a private dated destination.
- `DELETE`: irreversible removal justified by reproducibility or retention policy; require row-level approval.
- `REMOVE_IN_CANONICAL_REPO`: change tracked project configuration once at its source, then update clones normally.
- `MANUAL_REVIEW`: evidence is incomplete, mixed with credentials/state, dirty/unmerged, or policy-controlled.

Group action IDs into named batches only when every member has the same intent and risk, such as `STOP-WRITERS`, `GLOBAL-QUARANTINE`, or `CLEAN-MERGED-WORKTREES`. Show every member beneath the batch; batch names never hide rows.

End Phase 1 with an exact approval prompt:

```text
Approve scan <scan_id> actions <IDs> and/or batches <names> on <machines>.
Everything else remains unapproved.
```

## Phase 2 manifest

Create one private manifest per machine before mutation. Include:

- scan ID, approval text, approved IDs, start time, effective user, and tool/script version;
- preflight fingerprints and service/process state;
- source, operation, destination, collision check, rollback, result, and timestamp per action;
- preserved credential/state paths recorded by metadata only;
- verification command/postcondition and result per action;
- temporary files created and whether each was removed.

Use a mode-`0700` quarantine where supported and mode-`0600` manifests/rollback notes. Preserve original permissions when restoring. Refuse destination collisions rather than overwriting them.

## Phase 2 final report

Report applied, skipped, stale, failed, and still-unapproved IDs separately. Include quarantine/manifest locations, writer status, preserved-state checks, fresh-session harness evidence, repository status, disk change, rollback instructions, unavailable verification, and the exact next approval boundary.
