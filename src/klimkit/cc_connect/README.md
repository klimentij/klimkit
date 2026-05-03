# cc-connect wrapper

Klimkit keeps cc-connect as an optional runtime wrapper.

Managed config template:

- `templates/cc-connect/home/config.toml`
- installed to `~/.cc-connect/config.toml` when `components.cc_connect = true`

Klimkit creates the file if it is missing, but it does not overwrite an
existing `~/.cc-connect/config.toml`. Keep Telegram bot tokens, `admin_from`,
and `allow_from` values in that home-local file.

Run manually:

```bash
src/klimkit/cc_connect/run.sh
```

Secrets and real chat ids must live in local config, not tracked templates.
