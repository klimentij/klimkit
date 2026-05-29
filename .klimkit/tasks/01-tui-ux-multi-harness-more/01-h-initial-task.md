 What those knobs mean: - the fact i asked mean you have to add
  comments to toml config, clarify much better in readme. also
  make a single toml config for everything, not multiple! also i
  want all the state and config live in ~/klimkit repo in non-
  gittracked folder, bc it's annoying to switch to home dir every
  time to see it! --- Klimkit is a Python operator kit for setting
  up Codex-oriented machines without a TUI or prompt-driven
  wizard. The install script installs the kk command. kk creates a
  local TOML config, previews the exact file and service changes,
  and applies them when you choose. -> that's a bad top level
  description. reanalyze the repo and make much more helpful
  highlevel explainer. don't mention stack here. add our stack
  tech as a separate readme section so devs understand how it
  works under the hood. just simple list of tech stack + 1
  paragraph how everything is put together. then, i want you to
  prepare and refactor for it to be agent harness agnostic. still
  support only codex, but soon we'll add claude code etc. so mb
  need some cetral pack template and then we would generate per-
  harness spesific templates. also add deep , near 100% test
  coversage. even i want some test to be integration tests like a
  test could start codex cli and check if codex shows any yellow
  warnings (websearch its docs, maybe it can do it in non-
  interactive mode). i saw it shows warning when skills /subagents
  were not correctly formatted etc. also pull <knowledge-base-repo> - see
  in projects section there's log and memory files and agent md
  explaining how to use them. add the section to agents md in our
  pack. i want agent to create log and memory.md in repo root, mb
  in .klimkit/ of repo  root and i want it to know right
  formatting and how to insert and use them. the project folders
  would go under ./klimkit in every repo, better say feature
  folders with planning design and discussion. mb under tasks/
  subfolder? i precreated mannually in this repo so you unsertand better.  first plan the implementation in 02-a-...md. last section of plan must be exec summary (if i have tno time to read the plan). and one more secion with up to 3 clarification questions with spaces for me to fill out. avoid tables in md. btw -h- means human -a- means agent!

  actually also do an ultra deep critical reviewe of the repo, surface all ambiguty/inconsistency. we're aiming for prod level top os repo polish. actually make 02.. md with this ultra deep critical review and 03 - with the implementatino plan with clarifications