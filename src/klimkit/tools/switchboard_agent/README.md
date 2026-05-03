# Switchboard Agent

Legacy helper that summarizes Codex rollout files and can forward snapshots to a Switchboard backend.

Default config:

- `src/klimkit/tools/switchboard_agent/switchboard-agent.toml`
- state: `~/.local/state/klimkit/switchboard-agent/state.sqlite3`
- backend URL: blank until configured

Run manually:

```bash
src/klimkit/tools/switchboard_agent/run.sh --print-snapshot
```
