# Klim's directive — adopt docs/work as the Klimkit default

Received 2026-07-15, verbatim:

> https://github.com/Ace-Cooperatives/conversation-be/pull/3680 I wanted you to check out this PR in the home/satify repository and inspect my edits, the PR edits to AgentsMD and the ClaudeMD Simlink, and everything related to docs/work structure. You can actually copy it and sanitize it to make sure there are no Sellify mentions, ensuring it's generic to any project. I want it to become the new default for Klimkit instead of the .klimkit folder.
>
> With task folders, I want to adopt this docs/work structure exactly as is there. Just slightly adjust it if needed, plus the agents.md edit, and create it as a new structure. Yes, also move the existing .klimkit structure into this new structure. So in this very repo, it should be part of this.
>
> And yeah, create a new PR to scope all that stuff. Migration to the docs/work structure should be part of this PR. Of course, it's okay to use your tokens, but since they're expensive, you can use sub-agents with Sonnet 5 for large token input analysis of certain nodes to migrate the old .klimkit folder into the new docs/work structure.

The referenced upstream convention was designed in conversation-be PR #3680
(`docs/work/README.md`, work/phase `LOG.md` convention, `CLAUDE.md → AGENTS.md`
symlink, `.local/` gitignore tiering).
