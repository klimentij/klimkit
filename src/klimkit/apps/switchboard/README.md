# Klimkit Switchboard

Agentic engineering across machines, under control.

Klimkit Switchboard is the current Codex work dashboard and event backend.

Run locally:

```bash
kk serve
```

Default URL:

```text
http://127.0.0.1:4721/switchboard/
```

Security boundary:

- local mode binds to `127.0.0.1` and does not require a token
- non-loopback deployments must set `backend.auth_token`
- client collectors set `backend.base_url` to the configured server URL

Important config keys:

- `paths.state_dir`
- `server.host`
- `server.port`
- `server.base_path`
- `backend.base_url`
- `backend.auth_token`
- `collector.interval_seconds`
