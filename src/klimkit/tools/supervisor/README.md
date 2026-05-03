# Klimkit Supervisor

Single long-lived machine daemon for the operator repo.

Responsibilities:

- run an explicit `kk sync-live` pass when requested for live-managed Codex assets
- optionally run the Switchboard snapshot worker
- when `components.server = true`, keep Switchboard alive
- when `components.cc_connect = true`, keep cc-connect alive

The machine-local config lives at `~/.config/klimkit/klimkit.toml`.

Install and start it through:

```bash
kk apply --yes
```

The managed Linux user unit is generated from `templates/systemd/user/klimkit.service`. On macOS, `kk apply --yes` writes `~/Library/LaunchAgents/com.klim.klimkit.plist`.
