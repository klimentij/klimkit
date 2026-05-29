---
name: klimkit-security-auditor
description: Review auth, authorization, secrets, data exposure, input validation, sandboxing, infrastructure, compliance-sensitive flows, and unsafe defaults before completion. Use when a change touches security boundaries, credentials, deployment, containers, permissions, user data, or network exposure.
---

# Klimkit Security Auditor

Use this as the single Klimkit security review skill. Prefer concrete attack paths and compliance gaps over theoretical concerns. Combine narrow completion-gate review with broader DevSecOps, application security, cloud, and compliance thinking when the change warrants it.

## Workflow

1. Confirm authorization, scope, environment, compliance requirements, and any no-go tests before scanning or probing.
2. Read repo instructions, security docs, threat models, changed files, nearby auth/data/config code, deployment paths, and verification evidence.
3. Identify assets, actors, privileges, data classes, and trust boundaries affected by the change.
4. Trace data flow from entry points through middleware, APIs, queues, privileged SDKs/service accounts, storage, logs, reports, and third-party services.
5. Check authentication, authorization, token handling, secret hygiene, input validation, output encoding, data exposure, sandbox boundaries, network exposure, dependency risk, supply-chain risk, CI/CD defaults, infrastructure controls, and unsafe defaults.
6. Run adversarial feature analysis: for every changed capability, ask how a user could deface, hijack, modify, exfiltrate, or abuse shared state.
7. Use non-intrusive checks first. Do not run destructive, noisy, production, credential-stuffing, or persistence tests without explicit approval in the thread.
8. Tie each finding to evidence and a plausible abuse path. Do not report vague hypotheticals.
9. Order findings by severity and business impact.
10. Note clean areas explicitly audited, skipped checks, and residual risk.
11. Name policy, tests, monitoring, or documentation updates needed to keep guidance aligned with code.

## High-Value Checks

- Ownership and IDOR: every read, update, delete, export, webhook action, and admin-like operation verifies ownership or authorization, even when using privileged service accounts.
- Privileged bypasses: Admin SDKs, service roles, background jobs, and server-only clients do not bypass the policy that normal callers rely on.
- Middleware and routing: auth middleware filenames, exports, matchers, route groups, edge/server placement, and deployment config actually protect the intended paths.
- Secrets and tokens: no credentials in source, logs, reports, browser storage, screenshots, CI output, generated artifacts, or exception messages.
- SSRF and network access: user-controlled URLs cannot reach internal hosts, metadata services, loopback, private IPs, DNS rebinding targets, or unsafe redirects without validation and IP pinning.
- Input and output handling: untrusted data is validated, encoded, parameterized, size-limited, and handled without leaking stack traces or sensitive state.
- Session and identity: cookies, JWTs, OAuth/OIDC/SAML/WebAuthn flows, MFA, refresh tokens, revocation, scopes, and SameSite/Secure/HttpOnly attributes match the risk.
- Web security headers: CSP, HSTS, X-Frame-Options or frame-ancestors, CORP/COEP where relevant, content-type sniffing, CORS, and cache controls are deliberate.
- Dependency and supply chain: vulnerable packages, unpinned actions/images, untrusted install scripts, missing lockfiles, weak SBOM/provenance, and risky transitive tooling are called out.
- Cloud, container, and infra: IAM least privilege, network segmentation, storage ACLs, secret managers, image scanning, Kubernetes/container defaults, serverless permissions, and public exposure are reviewed.
- Compliance and governance: GDPR, HIPAA, PCI-DSS, SOC 2, ISO 27001, NIST, retention, audit logging, privacy by design, and incident response are considered when user data or regulated workflows are in scope.
- Monitoring and recovery: audit trails, security logs, alerting, incident response, backup/restore, and breach-notification paths are adequate for the changed surface.

## Output

Lead with findings:

```text
Severity: critical, high, medium, low
Evidence: file/path, route, config, log, test, or observed behavior
Impact: concrete abuse path and business/user risk
Fix: smallest robust mitigation
Verification: how to prove the fix
```

After findings, include:

- `Clean Areas Checked`: important security surfaces explicitly reviewed with no findings.
- `Skipped Checks`: unavailable code, environment, auth state, production restriction, or missing evidence.
- `Residual Risk`: what remains uncertain after the review.

If there are no findings, say that clearly and still list clean areas, skipped checks, and residual risk.
