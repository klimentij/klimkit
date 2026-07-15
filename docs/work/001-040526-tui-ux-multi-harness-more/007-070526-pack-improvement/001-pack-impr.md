add a new checklister subagent

refactor  pack's agents.md so it has super clear separation of concerns in sections without overlaps and duplication

e..g i want a  workfow to be a separte section

checklister must add to the -a- .. md a checklist of acceptance creteria. such that all checks must be done to make the human happy given the request. if task touches or depended etc on UI, check list must describe in great detail what screen must be in what states etc., also check on db, loca state states, test passing creteria etc. everything a world top ultra experience human QA would consider to accept/reject the result

final step of the workflow, when the agent is ready to write the final response for human, agent must call 3 parallel final reviewers agents

3/3 passes required  before bothering human


mb workflow like
other subagents - when feasible
required checklister
3 parallel final reviewer (input=human msg as is or url to md task + checklist from checklister + final output draft that's about to be shown to human)


also review the whole agentsmd + subagents +skills in the pack for consistency etc.


---

also add to readme this workflow to some dedicated pack explainer section


also say that beofre every feature recommended to make a worktree

i use nortmally on projects main branch for staging, dev that accumulated from ft branches. i create a worktree with script like this tmp/create-worktree.sh (sanitize so it's generic and doesn't metion my project etc.) and put it to some folder like examples and link to it in readme . and then create switchboard tab with the folder of this worktree

i normally use switchboard to run 5-7 parallel agents working in parallel brnaches on every machine. also add it to one of the tops parts of readme as it's an important repo promise

---
