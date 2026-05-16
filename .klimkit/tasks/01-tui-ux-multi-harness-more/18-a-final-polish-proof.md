# Final Polish Proof

Human task: `17-h-final-polish.md`.

## Implementation

- Softened install guidance so forks are recommended for real fleets but not enforced for trying Klimkit.
- Kept `install.sh` local-checkout based; it no longer describes a required fork checkout.
- Moved the Switchboard screenshots from `tmp/sb-screeenshots/` into `assets/screenshots/`.
- Added Switchboard PWA and workspace catalog screenshots near the top of `README.md`.
- Added the Telegram notification screenshot in the Telegram notifications section.
- Added a Switchboard catalog `Archived` column.
- Kept archived catalog rows hidden on fresh app load by resetting `showArchived` to false after loading saved filters.
- Changed catalog row open behavior so clicking an archived workspace unarchives it first, then activates it so the tab and code-server iframe become visible.
- Bumped package and README release metadata to `0.1.1`.

## Verification

```text
$ uv run python -m unittest tests.test_klimkit_install tests.test_switchboard tests.test_docs_static -q
----------------------------------------------------------------------
Ran 72 tests in 7.253s

OK
```

```text
$ bash -n install.sh && node --check src/klimkit/apps/switchboard/static/app.js
# no output
```

```text
$ uv run python -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 136 tests in 7.544s

OK (skipped=1)
```

```text
$ git diff --check
# no output
```
