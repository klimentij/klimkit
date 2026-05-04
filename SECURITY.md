# Security

Klimkit is intended for trusted personal machines and private tailnets.

- Switchboard can run without an auth token only on loopback. Non-loopback hosts require `switchboard.server.auth_token`.
- Tokenless loopback access also rejects non-loopback `Host` headers to reduce DNS-rebinding exposure. If Switchboard is exposed through a proxy, configure a token and HTTPS cookie behavior explicitly.
- Tailscale Serve is the intended remote exposure layer for Switchboard and code-server.
- code-server is configured with loopback binding and `auth: none`; delegate access to Tailscale or another trusted local proxy.
- The code-server template disables workspace trust and enables automatic tasks so agent workflows behave consistently. Do not use that profile for untrusted workspaces.
- Switchboard agent helper binds to `127.0.0.1` by default. Only set another `switchboard.agent.helper_host` for a trusted proxy path.
- Switchboard-launched Codex terminals are trusted-local automation and may use sandbox/approval bypass flags when configured.
- The single local TOML can contain Switchboard and Telegram tokens. `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` are ignored by default; keep only sanitized task/proof/memory/log artifacts tracked.
- `kk preview` shows external installer actions such as the code-server upstream network installer. Review the plan before `kk apply`, or disable the installer with `code_server.install_if_missing = false`.

Report vulnerabilities privately through the repository owner until a public advisory channel is configured.
