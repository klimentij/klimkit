# Reflection archive — generic-best-practice-up

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-14T12:07:00Z

**Observations:** The generic best-practice update shows the pack has matured enough that external advice should be decomposed into enforceable workflow, subagent, skill, and test changes rather than pasted as a parallel rule block.
**Derived Pattern:** Durable harness quality comes from distributing guidance to the layer that can enforce it: AGENTS for defaults, subagents for role-specific checks, skills for workflow mechanics, and tests for regression protection.
**Insight:** The strongest addition from the Karpathy-style and Matt Pocock material is not another checklist; it is making ambiguity, prototypes, fake support, projection failures, and weak feedback loops visible at the exact point where they usually become hidden agent errors.
**Next Probe:** After this release, watch whether future checklists and final reviews actually flag prototype leakage, unsupported production claims, and implementation-coupled tests without needing a human reminder.
