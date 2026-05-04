# Results And Proof

Agent-authored result for `05-h-start.md`.

## Scope Completed

- Moved Klimkit defaults to repo-local `.klimkit/local/klimkit.toml`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/`.
- Kept task/proof/memory/log artifacts trackable while ignoring private/runtime `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` subtrees.
- Collapsed Klimkit, Switchboard server, Switchboard agent, Telegram, and trusted local launch settings into one commented TOML source.
- Stopped default generation of separate `switchboard.toml` and `switchboard-agent.toml` install actions.
- Added a minimal Codex harness registry while keeping Codex projected to default `~/.codex`.
- Removed `packs/codex/hooks.json` and moved the Stop hook into inline Codex TOML hook config.
- Kept `packs/codex/` clean and hand-authored; no `packs/shared/` directory is introduced.
- Added `.klimkit/memory.md`, `.klimkit/log.md`, task naming guidance, and the `-h-` / `-a-` convention to the projected Codex AGENTS guidance.
- Rewrote README around product purpose, Tech Stack, Single Config, Generated Projections, and Security Model.
- Added `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`, and a GitHub Actions CI workflow.
- Added tests for repo-local paths, harness registry, static Codex pack validation, docs, and skipped-by-default Codex startup smoke validation.
- Cleaned stale `switchboard2` references from current docs and repo hygiene files.
- Hardened Switchboard tokenless loopback auth against untrusted `Host` headers and wired the trusted Codex sandbox-bypass config into generated tasks and UI commands.

## Proof Commands

```bash
uv run python -m unittest discover -s tests -q
```

Result: `Ran 90 tests in 6.785s`, `OK (skipped=1)`.

```bash
uv run coverage run -m unittest discover -s tests -q
uv run coverage report -m
```

Result: tests passed under coverage, total package coverage reported at `75%`.

```bash
uv run python -m unittest tests.test_codex_pack_validation -q
```

Result: `Ran 4 tests`, `OK`.

```bash
uv run python -m unittest tests.test_docs_static -q
```

Result: `Ran 2 tests`, `OK`.

```bash
uv run python -m unittest tests.test_codex_smoke -q
```

Result: `Ran 1 test`, `OK (skipped=1)`. This is expected unless `KLIMKIT_RUN_CODEX_SMOKE=1` is set. When enabled, the smoke starts Codex in a pseudo-terminal and terminates it after startup warnings have had a chance to print; it does not send a prompt/message to the agent.

```bash
KLIMKIT_RUN_CODEX_SMOKE=1 uv run python -m unittest tests.test_codex_smoke -q
```

Result: `Ran 1 test in 6.044s`, `OK`. Codex is signed in on this VM, so the startup-only smoke was run once against the current working-tree Codex pack in a temporary `CODEX_HOME`, without sending an agent message.

```bash
bash -n install.sh
bash -n packs/codex/hooks/stop-notify.sh
```

Result: both shell syntax checks passed.

```bash
./kk --config /tmp/klimkit-proof.toml setup --skip-services
./kk --config /tmp/klimkit-proof.toml preview
./kk --config /tmp/klimkit-proof.toml doctor
./kk --config /tmp/klimkit-proof.toml serve --print-projections
```

Result: setup created a single commented TOML at `/tmp/klimkit-proof.toml`; preview showed a single core Klimkit config action plus generated Codex/code-server/service projections; doctor reported config, uv, and git as ok; Switchboard projection printing exited successfully. The projection JSON includes live session and tailnet details, so the artifact records success without pasting that private output.

## Review Results

- Security audit second pass: PASS.
- Code review second pass: PASS.
- Final reviewer pass 1: PASS.
- Final reviewer pass 2: PASS.
- Final reviewer pass 3: PASS.

## Known Limits

- Live Codex startup smoke validation is skipped by default because it needs an installed, signed-in Codex CLI and a terminal startup path. It was also run successfully once on this VM with `KLIMKIT_RUN_CODEX_SMOKE=1`.
- Total coverage is now measurable but not yet gated by a threshold.
- `~/.codex` remains the Codex home by explicit clarification; repo-local `CODEX_HOME` migration is intentionally deferred.
- Shared pack extraction is intentionally deferred; `packs/codex/` remains the only current pack.
