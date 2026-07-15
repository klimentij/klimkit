# Reflection archive — checklist-and-implementation

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-24T05:52:04Z

**Observations:** The stop-hook deep link is a narrow extension of the Telegram opening contract: Switchboard stays primary, direct code-server remains infrastructure-dependent, and `codex://threads/<raw-session-id>` is rendered only when the hook payload has a non-empty `session_id`, with runtime hook tests plus projection/cmp evidence covering the shipped path.
**Derived Pattern:** Klimkit notification links are safest when each affordance owns one boundary: Switchboard for control-plane state, code-server for Tailscale workspace reachability, and Codex app links for raw agent thread identity without normalization.
**Insight:** The earlier post-review stop-hook quoting failure shaped the right proof level here; adding a link inside a fail-open hook is not proven by static diff alone, but by executing the hook with fake external commands and verifying both presence and omission cases.
**Next Probe:** Before final reviewers, close the checklist/proof gap around main push, autosync consumption, and latest-release evidence, and avoid claiming publication until concrete SHA/tag checks exist.
