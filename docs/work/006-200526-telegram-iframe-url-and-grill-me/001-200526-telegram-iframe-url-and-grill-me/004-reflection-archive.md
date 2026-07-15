# Reflection archive — telegram-iframe-url-and-grill-me

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-20T03:46:55Z

**Observations:** The Telegram direct-link change extends the earlier selected-machine code-server invariant from Switchboard tabs into every out-of-band notification path while preserving Switchboard as the primary control-plane link.
**Derived Pattern:** User-opening URLs should be derived from trusted Tailscale DNS plus workspace folder at each producer boundary, covered across all independent emitters, and omitted entirely when either side of that identity is unavailable.
**Insight:** Adding a secondary direct code-server URL is safe only because the implementation treats it as a backend-derived affordance rather than a replacement for Switchboard state, but live service evidence still depends on the recurring user-systemd DBus boundary.
**Next Probe:** Before final handoff, keep the unavailable `systemctl --user daemon-reload` as an explicit residual ops gap and consider a future `kk apply` improvement that distinguishes projection success from service-manager reachability without pruning managed service state.

### 2026-05-20T04:13:48Z

**Observations:** The post-review stop-hook failure shows the Telegram URL contract was only fully proven when the real shell hook executed end to end with fake `tailscale` and `curl`, because static shell parsing and helper-level assertions missed Python quoting fragility inside `bash -c`.
**Derived Pattern:** Harness hooks that fail open and embed another language need runtime tests that execute the shipped hook, capture external side effects, and cover both available and unavailable infrastructure paths.
**Insight:** The direct-link invariant is now stronger because Switchboard-first ordering, malformed direct URL omission, and Tailscale DNS behavior are covered at the emitter that previously produced noisy `{"continue":true}` Telegram spam; the remaining operational gap is still user-systemd reachability, not Codex projection.
**Next Probe:** Before commit, push, and release, make sure the post-fix runtime evidence and this appended reflection are staged, and have final reviewers distinguish verified hook projection from the known `systemctl --user daemon-reload` DBus limitation.
