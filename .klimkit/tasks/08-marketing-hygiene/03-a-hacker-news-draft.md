# Hacker News Draft

Status: draft only. Not posted.

## Title Candidate

Show HN: Klimkit - a repo-managed harness for long-running Codex work

## URL

https://github.com/klimentij/klimkit

## Submission Text / First Comment Draft

I built Klimkit for my own Codex workflow across disposable VMs and multiple machines.

The problem it tries to solve is not "how do I get an agent to write code?" The harder problem for me has been: after a long-running agent session, what proof is left behind? What did it read, change, test, skip, and hand off? Can another fresh VM or fresh agent recover the state from the repo?

Klimkit keeps that operating setup in one repo: Codex harness instructions, subagents, hooks, code-server settings, Switchboard workspace tabs, Tailscale-friendly links, task notes, proof reports, reflection logs, and final-review gates.

One recent dogfood moment that pushed me to open-source it: a vanilla Klimkit/Codex run worked for about 7.5 hours, stayed on goal without an outer loop such as `/goal`, and closed with backend tests, frontend checks, Playwright, secret scanning, Git checks, and a clean pushed state. The interesting part was not the runtime. It was that the run left enough evidence to inspect afterwards.

This is early and opinionated. It assumes a trusted personal VM or private tailnet, and the default Codex pack is intentionally yolo-mode for a dedicated sandbox, not a general laptop profile. The install path is fork-first for people who want their own operator repo.

I would especially like feedback on whether the artifact model transfers: task notes, checklists, proof reports, reflection, and 3-pass final review as a way to make long agent sessions reviewable.

## Shorter Variant

I built Klimkit to keep long-running Codex work reviewable across disposable VMs: one repo owns the harness, machine setup, Switchboard tabs, task notes, proof reports, reflection log, and final-review gates.

The dogfood moment that made me proud was a roughly 7.5-hour vanilla Klimkit/Codex run that stayed on goal without an outer loop and closed with tests, Playwright, secret scanning, Git checks, and clean pushed state.

It is early, personal, and intended for trusted sandbox machines/private tailnets. Feedback welcome on whether this artifact-first model is useful outside my own workflow.
