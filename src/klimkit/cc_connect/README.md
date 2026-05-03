# cc-connect wrapper

Klimkit keeps cc-connect as an optional runtime wrapper.

Managed config template:

- `templates/cc-connect/home/config.toml`
- installed to `~/.cc-connect/config.toml` when `components.cc_connect = true`

Run manually:

```bash
src/klimkit/cc_connect/run.sh
```

Secrets and real chat ids must live in local config, not tracked templates.
