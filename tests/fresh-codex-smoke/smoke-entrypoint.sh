#!/usr/bin/env bash
set -euo pipefail

export HOME=/root
KLIMKIT_REPO="${KLIMKIT_REPO:-https://github.com/klimentij/klimkit.git}"
KLIMKIT_REF="${KLIMKIT_REF:-codex-plugin-skill-cleanup}"
OPERATOR_NAME="${OPERATOR_NAME:-SmokeOperator}"
PERSONALITY_NAME="${PERSONALITY_NAME:-Steady Operator}"
PERSONALITY_DESCRIPTION="${PERSONALITY_DESCRIPTION:-Direct, careful, evidence-first, and conservative with scope.}"

mkdir -p "$HOME/.codex"
if [[ -d /host-codex-auth ]]; then
  for file in auth.json installation_id; do
    if [[ -f "/host-codex-auth/$file" ]]; then
      cp "/host-codex-auth/$file" "$HOME/.codex/$file"
      chmod 0600 "$HOME/.codex/$file" || true
    fi
  done
fi

if [[ ! -f "$HOME/.codex/auth.json" && -z "${OPENAI_API_KEY:-}" ]]; then
  cat >&2 <<'EOF'
No Codex auth was provided.

Mount a directory containing auth.json at /host-codex-auth, or pass an auth
environment supported by your Codex CLI build.
EOF
  exit 2
fi

codex --version
skills --version

rm -rf /workspace/klimkit /workspace/fresh-repo
git clone --depth 1 --branch "$KLIMKIT_REF" "$KLIMKIT_REPO" /workspace/klimkit

skills add /workspace/klimkit --list
skills add /workspace/klimkit --skill '*' -g -a codex -y --copy
skills ls -g -a codex --json | tee /tmp/skills.json

python3 - <<'PY'
import json
from pathlib import Path

expected = {
    "klimkit-workflow",
    "klimkit-implement",
    "klimkit-setup",
    "klimkit-checklister",
    "klimkit-code-explorer",
    "klimkit-security-auditor",
    "klimkit-reflector",
    "klimkit-final-reviewer",
    "klimkit-grill-me",
    "klimkit-diagnose",
    "klimkit-tdd",
    "klimkit-report-server",
    "klimkit-walkthrough",
    "klimkit-worktree-stack",
}
data = json.loads(Path("/tmp/skills.json").read_text())
installed = {item["name"] for item in data}
missing = sorted(expected - installed)
extra_deferred = sorted(
    installed
    & {"klimkit-to-issues", "klimkit-triage", "klimkit-github-control-plane"}
)
if missing or extra_deferred:
    raise SystemExit(f"Unexpected installed skills. missing={missing} extra_deferred={extra_deferred}")
print(f"Verified installed Klimkit skills: {', '.join(sorted(expected))}")
PY

mkdir -p /workspace/fresh-repo
git -C /workspace/fresh-repo init >/dev/null

cat >/tmp/klimkit-setup-prompt.txt <<EOF
Use the installed klimkit-setup skill.

This is a noninteractive fresh-machine smoke test. Do not ask follow-up questions.
Use operator name "${OPERATOR_NAME}".
Use agent personality "${PERSONALITY_NAME}": ${PERSONALITY_DESCRIPTION}

Create the minimal operator-scoped Klimkit setup in the current repository:
- .klimkit/${OPERATOR_NAME}/config.toml
- .klimkit/${OPERATOR_NAME}/memory.md
- .klimkit/${OPERATOR_NAME}/log.md
- .klimkit/${OPERATOR_NAME}/reflection.md
- .klimkit/${OPERATOR_NAME}/tasks/
- .klimkit/${OPERATOR_NAME}/reports/

Keep the files minimal and public-safe. After creating them, summarize what was created.
EOF

codex exec \
  --cd /workspace/fresh-repo \
  --dangerously-bypass-approvals-and-sandbox \
  --ignore-rules \
  --output-last-message /tmp/codex-last-message.txt \
  "$(cat /tmp/klimkit-setup-prompt.txt)" \
  | tee /tmp/codex-exec.log

root="/workspace/fresh-repo/.klimkit/${OPERATOR_NAME}"
test -f "$root/config.toml"
test -f "$root/memory.md"
test -f "$root/log.md"
test -f "$root/reflection.md"
test -d "$root/tasks"
test -d "$root/reports"
rg -n "$OPERATOR_NAME|$PERSONALITY_NAME" "$root/config.toml"

printf '\nFresh Codex smoke passed. Created files:\n'
find /workspace/fresh-repo/.klimkit -maxdepth 3 -print | sort
