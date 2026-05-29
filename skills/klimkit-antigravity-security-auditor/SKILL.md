---
name: klimkit-antigravity-security-auditor
description: Broad security audit candidate for application, DevSecOps, cloud, data-flow, and compliance review. Use when Codex needs a second security lens beyond `klimkit-security-auditor`, especially for IDOR, privileged bypasses, middleware matching, SSRF, CI/CD controls, or compliance-oriented risk framing.
---

# Klimkit Antigravity Security Auditor

Use this as an expanded security lens. Prefer `klimkit-security-auditor` for normal completion gates; use this skill when the task needs broader threat modeling or the user explicitly asks for a deeper security audit.

## Workflow

1. Confirm authorization, scope, environment, and any no-go tests before scanning or probing.
2. Trace data flow across trust boundaries: UI, API, middleware, service accounts, queues, storage, third-party services, logs, and reports.
3. Check for high-value failure modes:
   - IDOR and ownership bypass on global or shared resources.
   - Privileged SDK or service-account paths that bypass normal authorization rules.
   - Middleware filename, export, matcher, route, or deployment misconfiguration.
   - SSRF, DNS rebinding, internal network access, unsafe redirects, and webhook trust issues.
   - Secret exposure in source, logs, generated reports, browser storage, or CI output.
   - CI/CD, dependency, container, and infrastructure defaults that create deploy-time risk.
4. Use non-intrusive checks first. Do not run destructive, noisy, production, or credential-stuffing tests without explicit written approval in the thread.
5. Report findings first, then clean areas checked, skipped checks, and residual risk.

## Output

```text
P1 - Finding title
Evidence: file:line, route, config, log, or observed behavior
Impact: concrete abuse path
Fix: smallest robust mitigation
Verification: how to prove the fix
```

Security reports must not include live secrets, tokens, private customer data, or exploit payloads beyond what is necessary to explain the risk.
