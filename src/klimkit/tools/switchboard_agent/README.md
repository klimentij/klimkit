# Switchboard Agent

Legacy helper that summarizes Codex rollout files and can forward snapshots to a Switchboard backend.

Local config:

- `~/.config/klimkit/switchboard-agent.toml`
- state: `~/.local/state/klimkit/switchboard-agent/state.sqlite3`
- backend URL: set from `switchboard.backend_url` in `~/.config/klimkit/klimkit.toml`

Run manually:

```bash
src/klimkit/tools/switchboard_agent/run.sh --print-snapshot
```
