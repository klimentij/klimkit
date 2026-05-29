# Vercel Skill Reimport Proof

## Checklist

- [x] Revert the repository content to the state before the previous imported-skill sequence.
- [x] Reimport requested skills through Vercel Skills CLI.
- [x] Exclude `roin-orca/skills --skill simple` because prior review found no license and hostile prompt text.
- [x] Move installed skill folders from `.agents/skills` into root `skills/`.
- [x] Preserve installed files and directories from the Vercel Skills CLI output.
- [x] Apply only Klimkit naming prefixes to the imported skill folder names and `name:` frontmatter.
- [x] Initially avoided overwriting existing `klimkit-security-auditor` by importing the Antigravity skill with a source-qualified name.
- [x] Later folded the useful Antigravity checks into `klimkit-security-auditor` and removed the source-qualified copy.

## Vercel Skills CLI Commands Used

```bash
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser --copy -y
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines --copy -y
npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max --copy -y
npx skills add https://github.com/mattpocock/skills --skill improve-codebase-architecture --copy -y
npx skills add https://github.com/pbakaus/impeccable --copy -y
npx skills add https://github.com/sickn33/antigravity-awesome-skills --skill security-auditor --copy -y
```

The requested `https://www.skills.sh/vercel-labs/agent-browser/agent-browser` URL was tried first, but the CLI reported no well-known skills endpoint there. The GitHub package source was used for the same `agent-browser` skill.

## Follow-Up Merge

On 2026-05-29T10:04:51Z, the imported Antigravity security-auditor was merged into the original `klimkit-security-auditor` skill. The separate source-qualified copy was deleted so Klimkit has one security auditor with both the original focused completion-gate behavior and the broader Antigravity data-flow, DevSecOps, cloud, compliance, IDOR, middleware, privileged-bypass, and SSRF checks.
