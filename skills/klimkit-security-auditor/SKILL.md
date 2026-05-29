---
name: klimkit-security-auditor
description: Review auth, authorization, secrets, data exposure, input validation, sandboxing, infrastructure, compliance-sensitive flows, and unsafe defaults before completion. Use when a change touches security boundaries, credentials, deployment, containers, permissions, user data, or network exposure.
---

# Klimkit Security Auditor

Use this as a focused security review. Prefer concrete attack paths and compliance gaps over theoretical concerns.

## Workflow

1. Read repo instructions, security docs, changed files, nearby auth/data/config code, and the verification evidence.
2. Identify the assets and trust boundaries affected by the change.
3. Check authentication, authorization, token handling, secret hygiene, input validation, output encoding, data exposure, sandbox boundaries, network exposure, dependency risk, and unsafe defaults.
4. Tie each finding to evidence and a plausible abuse path. Do not report vague hypotheticals.
5. Order findings by severity.
6. Note clean areas that were explicitly audited.
7. Name policy or documentation updates needed to keep guidance aligned with code.

## Output

Lead with findings:

- `Severity`: critical, high, medium, low.
- `Evidence`: file/path or behavior.
- `Impact`: what can go wrong.
- `Fix`: specific next action.

If there are no findings, say that clearly and list residual risk or unverified areas.
