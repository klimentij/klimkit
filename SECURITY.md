# Security

Klimkit is intended for trusted personal machines and private tailnets.

The default Codex harness is tuned for a dedicated VM or external sandbox where yolo-mode automation is acceptable. Do not use that profile on a machine with broad cloud credentials, production write access, or unrelated private files.

- Switchboard can run without an auth token only on loopback. Non-loopback hosts require `switchboard.server.auth_token`.
- Tokenless loopback access also rejects non-loopback `Host` headers to reduce DNS-rebinding exposure. If Switchboard is exposed through a proxy, configure a token and HTTPS cookie behavior explicitly.
- Tailscale Serve is the intended remote exposure layer for Switchboard and code-server.
- code-server is configured with loopback binding and `auth: none`; `kk apply` configures Tailscale Serve so each client VM exposes its own code-server only inside the private tailnet.
- With `[code_server] managed_profile = true`, Klimkit syncs the repo's code-server `User` profile and extension list to every VM. The managed profile disables workspace trust and enables automatic tasks for a trusted operator box; do not use it for untrusted workspaces.
- Switchboard agent helper binds to `127.0.0.1` by default. Only set another `switchboard.agent.helper_host` for a trusted proxy path.
- Switchboard-launched Codex terminals are trusted-local automation and may use sandbox/approval bypass flags when configured.
- Legacy Switchboard proof reports are served only from configured repo roots under `.klimkit/reports/` or valid `.klimkit/<operator>/reports/` directories. Reserved artifact/runtime names are not treated as report owners, and symlinked `.klimkit` roots, operator directories, or report directories that escape the repo evidence tree are rejected. The current skills-first report location is self-contained HTML inside `docs/work/`, served by the `klimkit-report-server` skill's reference script.
- The projected Codex config may use `sandbox_mode = "danger-full-access"` and `approval_policy = "never"` by default. Keep the VM least-privileged and purpose-built.
- The legacy single local TOML can contain Switchboard and Telegram tokens. Legacy `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` are ignored by default. In the current docs-first layout, machine-local material stays in gitignored `.local/` folders under `docs/work/`; keep only sanitized work/proof/memory/log artifacts tracked.
- `kk preview` shows external installer actions such as the code-server upstream network installer. Review the plan before `kk apply`, or disable the installer with `code_server.install_if_missing = false`.
- Tailscale may require a one-time `sudo tailscale set --operator=$USER` before a non-root `kk apply` can update Serve routes.

Report vulnerabilities privately through the repository owner until a public advisory channel is configured.
