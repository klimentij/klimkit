# Reflection archive — research-reflection

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`). The four 2026-05-22 marketing
> sessions below (README/Show HN hygiene) had no dedicated work folder of their own; they
> are archived here as the closest fitting, temporally-adjacent folder from the same
> reflection-ledger era.

### 2026-05-21T10:12:05Z

**Observations:** Symphony reframes exactly the pressure Klimkit has been building around: Switchboard makes parallel Codex work visible, but the human still dispatches sessions; Symphony moves the control plane to durable work items and lets a daemon own dispatch, retry, and handoff.
**Derived Pattern:** Klimkit's next orchestration layer should preserve its local evidence model while adding a tracker adapter and run scheduler above existing worktrees, reports, Tailscale surfaces, and harness packs.
**Insight:** Linear is not the essence of Symphony; the essence is a normalized work-item contract with strong status, dependency, proof, and handoff semantics. GitHub Issues can be Klimkit's default if Projects/labels/issue fields are treated as an adapter detail rather than assumed to be equivalent to Linear.
**Next Probe:** Draft a small Klimkit orchestration spec that stops at Human Review first, uses `.klimkit/tasks` as the durable evidence spine, and compares a local queue with a GitHub Issues/Projects adapter before any daemon implementation.

### 2026-05-22T02:59:45Z

**Observations:** The operator knowledge base raw/index pass shows that Klim's search and orchestration problems are linked: the raw corpus is large enough to need a maintained evidence index, while Symphony-style work dispatch needs small context packs that can pull prior thinking into each runnable issue.
**Derived Pattern:** Klimkit's autonomy layer should combine two adapters, not one: a work-item adapter for GitHub/Linear/local tasks and a knowledge adapter for operator knowledge base/wiki/raw retrieval, with `.klimkit/tasks` bridging execution evidence back into durable memory.
**Insight:** The years-long trajectory is a steady move from chat surfaces toward explicit system boundaries. The next boundary is not a prettier board; it is an issue-backed scheduler plus proof packet pipeline that can use GitHub dependencies for DAG execution and operator knowledge base search for operator-specific context.
**Next Probe:** Write the first orchestrator spec around local queue plus GitHub Issues/Projects, and separately promote SQLite FTS from experiment to maintained operator knowledge base search before relying on raw-corpus context packs in autonomous runs.

### 2026-05-22T03:04:00Z

#### Observations

The marketing hygiene patch turns a private-pride moment into a public repo signal by using the cropped terminal proof instead of the surrounding Slack thread. That preserves the point of the story without importing private conversational context.

#### Derived Pattern

Klimkit's public README works best when it shows evidence discipline in the first screenful: not just the product logo or dashboard screenshots, but a concrete long-running agent result and the checks that made the result inspectable.

#### Insight

The 7.5 hour screenshot is valuable because it makes the abstract proof-contract thesis visceral. The launch story should keep emphasizing that the scarce asset is not runtime or autonomy by itself; it is reviewable state after the run ends.

#### Next Probe

After this hygiene lands, watch whether visitors click into `.klimkit/tasks`, reports, or harness files from the README. If they do, add a small public example artifact gallery; if they only react to the dashboard, sharpen the README toward proof reports and final-review gates.

### 2026-05-22T03:08:51Z

**Observations:** The marketing patch publishes lightweight repo-facing evidence in README while the richer browser proof packet remains a local/Tailscale artifact with screenshot and video assets intentionally ignored by Git.
**Derived Pattern:** Klimkit launch material needs two evidence tiers: small public assets that make the proof-contract story fast to load, and heavier proof reports that stay inspectable through the configured report server unless they are deliberately promoted into a public gallery.
**Insight:** The 7.5 hour crop is the right public hook precisely because it is bounded and cheap; the final handoff should not imply the full proof-report media bundle is public GitHub content just because the report HTML exists in `.klimkit/reports`.
**Next Probe:** If Klim wants HN readers to inspect proof artifacts directly, create a consciously public example artifact page with tracked media or stable hosted assets instead of relying on ignored report media or private Tailscale URLs.

### 2026-05-22T03:30:23Z

#### Observations

The post-review corrections tightened the proof boundary rather than changing the marketing thesis: the Telegram screenshot now removes actual tailnet URLs, the proof report includes both Switchboard screenshots, and the proof note no longer calls uncommitted files tracked or already public.

#### Derived Pattern

Marketing hygiene for Klimkit has to distinguish three states that are easy to blur: ready in the working tree, committed/tracked in Git, and live on GitHub. The same applies to evidence media: public-facing assets can live in non-ignored repo paths, while report media remains local/Tailscale unless deliberately promoted.

#### Insight

The corrected package is stronger because it does not trade proof for exposure. It shows enough evidence to make the 7.5 hour story credible, removes unnecessary live-network details from the public README asset, and leaves heavier QA evidence behind the report server where the harness expects it.

#### Next Probe

Before publishing the HN link, either commit and push the README/assets as the public surface, or create a dedicated public proof-gallery page with intentionally committed/hosted media so readers do not depend on ignored report assets or private Tailscale URLs.

### 2026-05-22T04:08:45Z

#### Observations

Klim's correction exposed the difference between numeric optimization and visual acceptability: the first image pass satisfied the byte-size instinct but damaged the public first impression. The publish gap was equally concrete: until `f1eb323` was pushed and checked in the browser, the work existed only in local proof.

#### Derived Pattern

README marketing assets should be judged by the rendered GitHub page, not only by local file size or a local report. For dark UI screenshots, a slightly larger high-quality JPEG can be the better public artifact than a smaller noisy PNG.

#### Insight

The launch workflow needs a hard distinction between "ready", "committed", "pushed", and "visible on GitHub main". The final proof should include the live README image URLs and release state because the user's trust issue was not just asset quality; it was whether the public repo actually changed.

#### Next Probe

Before the HN post goes out, inspect the GitHub README once more from a logged-out or clean browser and decide whether the Telegram screenshot belongs in the public narrative or should be replaced by a smaller purpose-built notification example.
