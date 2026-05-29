# Third-Party Notices

Klimkit includes adapted candidate skills from these upstream projects. The skill folders keep Klimkit-facing workflow text; this file keeps source and license attribution out of the skill invocation path.

| Klimkit skill | Upstream source | Reviewed commit | License note |
| --- | --- | --- | --- |
| `klimkit-agent-browser` | `vercel-labs/agent-browser`, `skills/agent-browser` | `b4f2f37d7b4f954022bc77f8d6dce70e07072b00` | Apache-2.0 |
| `klimkit-web-design-guidelines` | `vercel-labs/agent-skills`, `skills/web-design-guidelines` | `180115660cfb8a86b808f117475a01f54caf3bc5` | Upstream README says MIT; no standalone license file was found in the reviewed checkout. |
| `klimkit-ui-ux-pro-max` | `nextlevelbuilder/ui-ux-pro-max-skill`, `.claude/skills/ui-ux-pro-max` | `b7e3af80f6e331f6fb456667b82b12cade7c9d35` | MIT |
| `klimkit-improve-codebase-architecture` | `mattpocock/skills`, `skills/engineering/improve-codebase-architecture` | `e3b90b5238f38cdea5996e16861dcae28ef52eda` | MIT |
| `klimkit-impeccable` | `pbakaus/impeccable`, `plugin/skills/impeccable` | `63074dd362ad4a9182849dbeefb8245d46e0a791` | Apache-2.0 with upstream NOTICE |
| `klimkit-antigravity-security-auditor` | `sickn33/antigravity-awesome-skills`, `skills/security-auditor` | `bbfe09c18ead0e7ff2899d5aec29f35d8ca03bca` | MIT for code; CC BY 4.0 for content |

`roin-orca/skills --skill simple` was reviewed but not imported because no license file or license notice was found, and the skill text contained hostile prompt instructions plus an XSS-looking Markdown payload.
