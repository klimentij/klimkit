# Klimkit Supervisor

Single long-lived machine daemon for the operator repo.

Responsibilities:

- fetch `origin/main` cheaply and sync only live-managed Codex assets into `$HOME`
- optionally run the Switchboard snapshot worker
- on `machine.profile = "server"`, keep Switchboard2 and cc-connect runtimes alive

The machine-local config lives at `~/.config/klimkit/klimkit.toml`.

Install and start it through:

```bash
klimkit apply --yes
```

The managed Linux user unit is generated from `templates/systemd/user/klimkit.service`. On macOS, `klimkit apply --yes` writes `~/Library/LaunchAgents/com.klim.klimkit.plist`.
