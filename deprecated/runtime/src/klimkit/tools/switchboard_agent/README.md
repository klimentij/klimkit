# Switchboard Agent

Helper that summarizes Codex rollout files and can forward snapshots to a Switchboard backend.

Local config:

- config: `~/klimkit/.klimkit/local/klimkit.toml`
- state: `~/klimkit/.klimkit/state/switchboard-agent/state.sqlite3`
- backend URL: set from `switchboard.agent.backend_url` in the single Klimkit config

Run manually:

```bash
kk serve --print-projections
```
