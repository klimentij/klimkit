---
name: klimkit-claude-subagent
description: Spawn Claude Opus 5 or Fable 5 as an external subagent through the Claude Code CLI, supervised by exactly one GPT-5.6 Sol low-effort babysitter. Use automatically when the user says "spawn Opus 5", "spawn Fable 5", asks for an Opus 5 or Fable 5 sub-agent, or asks Codex to delegate a task to either Claude model.
---

# Spawn a Claude subagent

Use a **babysitter** architecture. The root Codex agent coordinates one native Sol
subagent; Sol runs one external Claude CLI worker. Claude does the requested task. Sol
only starts, monitors, and reports it.

An external Claude process is not a native Codex subagent. Never claim that it appears in
Codex's subagent UI or shares Codex mailbox semantics.

## Root contract

1. Resolve the requested Claude model and task:
   - Opus 5 -> `claude-opus-5`, session name `opus-worker`.
   - Fable 5 -> `claude-fable-5`, session name `fable-worker`.
   - Default Claude effort to `low`. Preserve another effort only when the user states it.
   - If the model or task is missing, ask for the missing value before spawning anything.
2. Spawn exactly one native subagent with:
   - model: `gpt-5.6-sol`
   - reasoning effort: `low`
   - context fork: `none`
3. Give Sol a standalone packet containing the babysitter prompt below, the exact task,
   working directory, permissions, scope, output requirements, and stop conditions.
4. Wait for Sol. Do not perform Claude's task in the root session while it runs.
5. Return Claude's result and evidence. Do not replace it with Sol's or the root agent's
   answer. Confirm that the Sol babysitter has finished or stop it after collecting the
   report.

The root step is complete only when exactly one Sol-low babysitter has returned one
verified Claude result or one exact blocker.

## Babysitter prompt

Pass this contract to Sol, substituting the model, session name, task, and working
directory. Do not weaken it.

```text
You are the babysitter for one external Claude Code worker. Do not solve, summarize,
review, or implement the delegated task yourself.

Requested model: <claude-opus-5|claude-fable-5>
Claude effort: <low unless the user explicitly requested another value>
Session name: <opus-worker|fable-worker>
Working directory: <absolute path>
Task: <exact standalone task and all user constraints>

1. Preflight the installed CLI in the working directory:
   - Run `claude --version` and `claude --help` first.
   - Run `claude auth status`; verify logged-in first-party Claude authentication, but do
     not relay email, organization identifiers, tokens, or other identity fields.
   - Treat the installed help as the source of truth for flags and model names.
   - If `claude` is missing, stop and report that exact blocker.

2. Keep Claude Code current:
   - Run `claude update` with approved host-network access on every invocation.
   - Re-run `claude --version` and `claude --help` after an update.
   - If updating fails, report the failure. Continue only when the installed help still
     supports the exact requested model and required flags.

3. Start exactly one Claude worker with approved host-network access. Use the exact
requested model; never substitute an alias, fallback model, or another provider. Pass the
task as one safely quoted argument, never as executable shell text.

claude -p \
  --model <MODEL> \
  --effort <EFFORT> \
  --permission-mode auto \
  --tools default \
  --output-format json \
  --name <SESSION_NAME> \
  '<TASK>'

Do not use `--bare`, `--safe-mode`, `--no-session-persistence`,
`--dangerously-skip-permissions`, or `--fallback-model`. Omitting
`--no-session-persistence` is intentional: preserve the session for follow-up work.

4. Babysit the process until it reaches a terminal state:
   - JSON output can remain silent until completion. Silence alone is not a hang.
   - Poll a yielded process at intervals no longer than 60 seconds. Do not impose an
     arbitrary short timeout or interrupt a healthy worker.
   - Stop only for user cancellation, an explicit user deadline, a clear process failure,
     or a permission question that requires the user.
   - If the result is `ENOTIMP`, confirm the command used approved host-network access and
     retry once that way. If the retry fails, return the exact error.

5. Parse the final JSON and return:
   - `.result` verbatim
   - `.session_id`
   - `.total_cost_usd`
   - `.terminal_reason` and `.is_error`
   - `.permission_denials`
   - the matching `.modelUsage` entry and its `canonicalModel`
   - CLI version, update outcome, and any errors

`modelUsage` may contain auxiliary models. Verification passes when it contains the exact
requested canonical model. It does not need to be the only entry. Never invent a result
or replace a failed Claude call with your own work.
```

## Spawn example

When the user says, “Spawn Opus 5 to review this migration plan,” create the babysitter:

```json
{
  "task_name": "opus_5_babysitter",
  "fork_turns": "none",
  "model": "gpt-5.6-sol",
  "reasoning_effort": "low",
  "message": "<babysitter prompt with claude-opus-5 and the migration-review task>"
}
```

For “Spawn a Fable 5 subagent to find flaws in this design,” use the same Sol settings and
set the Claude model to `claude-fable-5`. Do not spawn one Sol per model attempt or add a
second reviewer unless the user separately requests it.

## Resume a Claude session

For a follow-up during the same delegated run, have the same babysitter use the returned
session ID:

```bash
claude -p \
  --resume <SESSION_ID> \
  --permission-mode auto \
  --tools default \
  --output-format json \
  '<FOLLOW_UP>'
```

Keep the follow-up inside the user's original authority. A new user request to spawn Opus
5 or Fable 5 starts a new Sol-low babysitter unless the user explicitly asks to resume the
saved Claude session.

## Final handoff

Return, in this order:

1. Claude's exact result.
2. Requested and canonical model.
3. Session ID for resumption.
4. Cost, terminal status, permission denials, update result, and errors.
5. Sol babysitter status.

Do not expose authentication identity fields or raw configuration. Do not describe Sol as
the author of Claude's result.
