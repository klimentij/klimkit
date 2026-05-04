# Klimkit Supervisor

Single long-lived machine daemon for the operator repo.

Responsibilities:

- run an explicit `kk sync-live` pass when requested for live-managed Codex assets
- optionally run the Switchboard snapshot worker
- when `components.server = true`, keep Switchboard alive

The machine-local config lives at `~/klimkit/.klimkit/local/klimkit.toml`.

Install and start it through:

```bash
kk apply
```

The managed Linux user unit is generated from `templates/systemd/user/klimkit.service`. On macOS, `kk apply` writes `~/Library/LaunchAgents/com.klim.klimkit.plist`.
