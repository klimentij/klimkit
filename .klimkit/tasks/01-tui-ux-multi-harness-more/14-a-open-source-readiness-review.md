# Open Source Readiness Review

Date: 2026-05-04

## Preparedness Level

Verdict: **not ready for broad open-source launch yet; close to a credible private/public beta after a focused cleanup pass.**

Preparedness score: **7/10 for a trusted-operator repo, 5/10 for a polished open-source project.**

Klimkit has a coherent product direction, strong operational docs for the intended trusted-VM model, a real CLI, service management, tests, CI, and an MIT license. The main gap is not core functionality. The gap is public-project discipline: release channels, package metadata, CI breadth, remaining personal/private-looking analysis code, and explicit hardening around an intentionally powerful automation profile.

## Recent Implementation Readiness

The latest work improved production behavior in areas that mattered for the current task:

- Switchboard now preserves `new`, `working`, `ask`, `done`, and `seen` state across server/client machine identity differences such as `MacBook-Air-8.local` vs `MacBook-Air-8`.
- Client attention events now trigger server-side Telegram fanout for completed and input-needed sessions, with deduplication.
- Browser notifications were manually QA-tested through an injected notification capture harness.
- `packs/codex/` no longer hardcodes the human operator's name. Harness files can use `__HUMAN_NAME__`, projected from `[operator].human_name`, defaulting to `Human`.
- The current VM has local ignored config set to `human_name = "Klim"`, proving the generated projection still addresses the operator correctly while the pack remains generic.

## Strengths

- Clear operator model: one repo, one local config, preview/apply/pull, managed projections, manifest-backed ownership, and explicit service restarts.
- Good safety posture for managed files: `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` are ignored, while task notes and memory/log files remain trackable.
- Strong README coverage for install, config, generated projections, harness pack workflow, security model, common commands, and live apply behavior.
- `SECURITY.md` states the trusted-machine/tailnet assumption and calls out the dangerous Codex profile, tokenless loopback constraints, code-server posture, and Tailscale Serve boundary.
- `CONTRIBUTING.md` is concise and matches the repo's workflow.
- CI exists and runs unittest plus coverage on pull requests and pushes.
- Test suite is meaningful for a young repo: current validation passed 117 tests with 1 skipped test and 78% total coverage.
- The CLI has become operator-friendly: `kk apply` and `kk pull` now report restarts, live URLs, Tailscale URLs, projection paths, and Telegram notification status.
- Switchboard has real manual browser QA evidence for multi-machine status transitions and notification behavior.

## Blocking Findings Before Public Launch

### 1. Mutable-main install and autosync are too sharp for general open source

Evidence:

- `README.md` installs from `https://raw.githubusercontent.com/klimentij/klimkit/main/install.sh`.
- `install.sh` clones `https://github.com/klimentij/klimkit.git`.
- The supervisor autosync model intentionally fast-forwards from `origin/main` and applies every 5 seconds by default.

Risk:

For a personal fleet this is useful. For external users it means their agent VM can automatically consume every pushed `main` commit and restart services. That is a high-trust release model and needs either release channels or much louder onboarding language.

Recommendation:

- Add a stable release channel before broad launch: tag-based install, `KLIMKIT_REF`, or a config option such as `[autosync] ref = "origin/main"` with documented safe defaults.
- Consider defaulting third-party installs to a release branch/tag, while developer installs can opt into `main`.
- Add `install.sh` environment overrides for repo URL, checkout path, and ref, and document them.

### 2. Personal/private-looking analysis modules should not ship in the core package

Evidence:

- `src/klimkit/analysis/chatgpt_archive_eda.py` and `src/klimkit/analysis/chatgpt_export_eda.py` include personal categorization terms such as `wife_score`, `likely-wife`, and `likely-klim`.
- `src/README.md` describes `src/klimkit/analysis/` as maintained analysis helpers.

Risk:

Even if no secret data is committed, these modules make the public package look partly personal and unrelated to the core Klimkit product. They also create unnecessary privacy questions for contributors and users.

Recommendation:

- Move these scripts outside the distributed `src/klimkit` package, for example to `experiments/`, `private-tools/`, or another private repo.
- If kept, rename and sanitize all personal labels, add clear fixture-free docs, and exclude private workflows from packaged wheels.

### 3. Packaging metadata is underdeveloped

Evidence:

- `pyproject.toml` has name, version, description, Python requirement, scripts, and build backend.
- It lacks common public metadata: `readme`, `license`, `authors`, `maintainers`, `keywords`, `classifiers`, and project URLs.

Risk:

The package can build, but it does not yet look like a mature open-source package on PyPI or in downstream metadata consumers.

Recommendation:

- Add `readme = "README.md"`, SPDX license metadata, authors/maintainers, repository/homepage/issues URLs, and classifiers.
- Decide whether Klimkit will publish wheels to PyPI or stay Git-installed for now.
- Add a release checklist and changelog.

### 4. CI only covers one Linux/Python lane

Evidence:

- `.github/workflows/ci.yml` runs on `ubuntu-latest` with Python 3.11 only.
- The project requires Python 3.11+, so 3.12 and 3.13 should be in scope.
- macOS launchd support is important behavior but not exercised by CI.

Risk:

Cross-platform assumptions can regress silently, especially around shell behavior, launchd plist rendering, filesystem paths, and service commands.

Recommendation:

- Add a Python matrix for 3.11, 3.12, and 3.13.
- Add at least one macOS CI job for unit tests and launchd rendering.
- Add a lightweight shellcheck or install-script smoke test if the project wants to keep `curl | bash` as the primary install path.

### 5. Powerful defaults require a stronger public onboarding boundary

Evidence:

- `SECURITY.md` and `README.md` correctly warn that the default Codex profile may use `danger-full-access`, `approval_policy = "never"`, tokenless loopback code-server, and Tailscale Serve.
- The same defaults are central to the product's value.

Risk:

The current docs are honest, but public users may still copy/paste onto laptops or servers with broad secrets. This is the largest trust and support risk.

Recommendation:

- Add a first-run safety checklist to `kk setup` or README before service enablement.
- Add an explicit "dedicated VM only" confirmation in docs and maybe an opt-in config flag for yolo Codex projection.
- Document a minimal-permission VM setup and a "do not install here" section.

## Important Non-Blocking Findings

### Public docs still mix brand, personal story, and install ownership

Evidence:

- `README.md` still says the repo makes a VM behave like "Klim's working environment."
- The install URL points at `klimentij/klimkit`.
- The macOS launchd label uses `com.klim.klimkit`.

Assessment:

This is not a bug if "Klimkit" intentionally remains a personal-origin brand. It is inconsistent with the new generic harness operator templating, though.

Recommendation:

- Decide whether public copy should say "the operator's working environment" instead of "Klim's working environment."
- Keep product names as Klimkit, but reserve `__HUMAN_NAME__` for harness/operator-addressing text.

### Test fixtures contain private-looking names and tailnet domains

Evidence:

- Tests include fixture values such as `tail11c448`, `odev`, `MacBook-Air-8`, and `/Users/klim`.

Assessment:

These do not appear to be secrets; they are fixtures. They still read as copied-from-real-environment examples.

Recommendation:

- Before public launch, replace with synthetic fixture names such as `alpha.tail.example.ts.net`, `server-vm`, and `/Users/operator`.

### Coverage is useful but uneven

Evidence:

- Full coverage run passed at 78% total.
- Lower-coverage areas include long-running supervisor and Switchboard daemon behavior.

Recommendation:

- Add targeted tests for autosync backoff/failure reporting, Telegram error paths, Switchboard notification dedupe edge cases, and service restart decisions.
- Keep browser QA evidence for UI behavior, but add a minimal Playwright/agent-browser smoke script if UI regressions become common.

### Release process is implicit

Evidence:

- There is no changelog, release workflow, release checklist, or version bump policy.

Recommendation:

- Add `CHANGELOG.md`, a release checklist under `.klimkit/tasks/` or docs, and a GitHub release workflow once tags are used for installs.

### Public support surfaces are minimal

Evidence:

- `SECURITY.md` says to report vulnerabilities privately through the repository owner until a public advisory channel is configured.
- There are no issue templates, discussion policy, support policy, or code of conduct.

Recommendation:

- Add GitHub issue templates for bug report, feature request, and security-sensitive report redirect.
- Add `CODE_OF_CONDUCT.md` if the repo expects external contributors.
- Add a public security contact or GitHub private vulnerability reporting setup before broad announcement.

## Security Review

No obvious committed secrets were found by filename scan for `.env`, secret, token, or key files outside ignored/runtime paths.

The repo's core risk is intentional agency: Codex can be configured for broad filesystem and command access, code-server can be tokenless on loopback, and Switchboard launches/observes agent work. The docs currently state the trusted-tailnet boundary and should keep doing so. For open source, the safest framing is:

- Klimkit is for dedicated operator VMs.
- Tailscale/private network is the remote access boundary.
- Do not install on general personal machines with broad secrets.
- Do not expose Switchboard or code-server directly to the public internet.
- Treat autosync from mutable refs as remote code execution by trusted maintainers.

## Manual QA Evidence

Manual browser QA was completed against the live Switchboard at `http://127.0.0.1:4721/switchboard/` with two machines:

- `odev`
- `MacBook-Air-8.local`, merged with server events from `MacBook-Air-8`

The later status QA used synthetic sessions under `/tmp/klimkit-qa/20260504124758/` and captured browser notification calls in-page because headless Chrome cannot show OS notification toasts in a screenshot. The `NEW` proof screenshot was recaptured with fresh manual tabs under `/tmp/klimkit-qa/new-proof/` after final-review feedback found that the original first screenshot was taken before tabs rendered.

Screenshots:

- `tmp/qa/status/01-new-both-machines.png`: both machine tabs visible as `NEW`.
- `tmp/qa/status/02-working-both-machines.png`: both machine tabs visible as `WORKING`.
- `tmp/qa/status/03-ask-browser-notifications-both-machines.png`: both tabs visible as `ASK`; captured browser notifications for both machines.
- `tmp/qa/status/04-done-browser-notifications-both-machines.png`: both tabs visible as `DONE`; captured completion notifications for both machines.
- `tmp/qa/status/05-seen-after-ack-both-machines.png`: both tabs visible as `SEEN` after acknowledgement.

## Validation Evidence

Commands already passed during this review cycle:

- `node --check src/klimkit/apps/switchboard/static/app.js`
- `python3 -m py_compile src/klimkit/install.py src/klimkit/apps/switchboard/daemon.py src/klimkit/tools/switchboard_agent/switchboard_agent.py`
- `uv run python -m unittest tests.test_klimkit_install tests.test_switchboard_agent tests.test_switchboard tests.test_docs_static -q`
- `uv run python -m unittest discover -s tests -q`
- `uv run coverage run -m unittest discover -s tests -q && uv run coverage report --skip-empty`
- `kk apply`

Current validation result: **117 tests passed, 1 skipped, 78% total coverage.**

## Open Source Launch Checklist

1. Decide release channel policy for install/autosync: mutable `main`, stable tags, release branch, or explicit operator opt-in.
2. Move or sanitize personal analysis modules before packaging.
3. Add public package metadata to `pyproject.toml`.
4. Expand CI to Python 3.11/3.12/3.13 and at least one macOS lane.
5. Add changelog, release checklist, and versioning rules.
6. Replace private-looking test fixture names with synthetic names.
7. Add issue templates and a clear vulnerability reporting channel.
8. Add first-run safety checklist for dedicated-VM/yolo-mode assumptions.
9. Add browser smoke automation for Switchboard status and notification paths.
10. Review all public copy for the intended balance between Klimkit brand identity and generic operator language.

## Bottom Line

Klimkit is technically coherent and already usable as an operator-controlled machine kit. It is not yet polished enough for a broad open-source launch because public trust boundaries, release discipline, and package hygiene need another pass. The highest-leverage next step is to split "personal fleet fast path" from "public safe path": stable releases for external users, explicit mutable-main autosync for the trusted fleet, and removal or sanitization of private-looking analysis code.
