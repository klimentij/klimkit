# Research — Claude Code Artifacts and Codex Sites (2026-07)

Web research backing the hosted-publishing default. Both surfaces are
authentication-protected by default, which is what the convention requires.

## Claude Code Artifacts

- Built-in `Artifact` tool publishes an HTML/Markdown file from the session to a private
  URL on claude.ai; requires a claude.ai-authenticated session (Pro/Max/Team/Enterprise,
  Anthropic API provider; not available with API keys, Bedrock/Vertex/Foundry, or ZDR
  orgs). CLI ≥ 2.1.183.
- **Private to the author by default.** Team/Enterprise can share to specific members or
  the whole org (viewers sign in to claude.ai); public link sharing is off by default
  org-wide and must be enabled by an Owner. On Pro/Max a public link is the only sharing
  option — so for our purposes, don't share at all on those plans.
- Republishing updates the same URL in place (viewers see live updates); each publish is
  a version with a version picker.
- Constraints: one self-contained page, strict CSP (no external requests, no backend, no
  relative links), `.html`/`.htm`/`.md` source, ≤16 MiB rendered.
- Source: https://code.claude.com/docs/en/artifacts

## Codex Sites

- Codex/ChatGPT builds, hosts, and serves a site on OpenAI infrastructure; two-stage
  flow: save a version (reviewable, linked to a commit), then deploy to the live URL.
  Local projects link via `.openai/hosting.json`.
- **Private and invitation-only by default; access is workspace-authenticated.** Sharing
  options are admins-only / whole workspace / named people; workspace admins can restrict
  public sharing. Launched in preview 2026-06-02 for ChatGPT Business/Enterprise; managed
  from ChatGPT web/desktop (Codex CLI can edit the local project before publishing).
- Supports backends (D1 database, R2 storage) — heavier than artifacts; for docs/work
  reports the static page is all that's needed.
- Source: https://developers.openai.com/codex/sites (redirects to
  https://learn.chatgpt.com/docs/sites)

## Ruling applied

Everything HTML in `docs/work/` meant for the human driver is deployed through the
harness's native hosted surface by default (Artifact tool on Claude Code, Sites on
Codex), always keeping the default authenticated visibility — private or workspace-only,
never public unless Klim explicitly asks. Deployed URL goes in the phase `LOG.md` next to
the file link; git-tracked HTML stays the source of truth. `klimkit-report-server`
(local/Tailscale) is demoted to fallback.
