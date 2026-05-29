switchboard ui:
no logo in dialog, only name 
polish dialog so it's full page length and every single block in it is corretctly fit , no weird gaps. qa ui, take screenshots and adjust in a loop until perfect

don't show all tabs from all sessions. need only tabs i created manually by clicking Create tabs. E.g. subagents also produce sessions, i don't need those as separate tabs

when i send msg to codex, for some reason status becomes plannign - incorrect, it's working. simplify statuses. mb only new, working, ask (when questions or confirmations of approvals of actions), done, seen

---

  About this:

  [switchboard.agent]
  enabled = false

  That is correct on this VM. This VM is the central Switchboard
  server, so switchboard.server.enabled = true runs the UI/API and
  collects local Codex sessions directly.

  switchboard.agent is for satellite/client VMs. A second VM would
  set switchboard.agent.enabled = true and backend_url =
  "https://dev-vm.../switchboard" so it reports its sessions into th
  is central Switchboard. This central VM does not need to report
  to itself.

  ---

  that's very confusing. i might have server only but no collecting seeesions form some machine! i'd do it true by default, and when client only it's true without server 


  ---

  tg notifications: review all possible notifications and polish them so they alll are very nice formatted with emojies, etc. 

  ⚡ Quick open on this Mac -> that's an old link for mac automation, we're not using it anymore. also remove related code (for Automator and some mac daemon for deeplinking)

  instead need a link that opens klimkit webapp on a cetain tab, like link in browser notifications (works correctly)

  ---

  add nice tags to main readme for github: licence etc. 
  add contribution instructions
  add table of contents 
  etc - improve readme so it's more complete and ready for collaborative active work!


  ---

  pack polish:

  deeply analayze agents md skills and subagents. criticsally review, find duplicating stuff, inconsistencies, etc. 

  also i wana add to agents smth like
  just before getting back to finally needs to get pass decisions from 3 parallel final
  reviewer subagents before bothering klim


  also add a skill to pack:
  like harness-tunining 
  it should instruct model how to tune genrral homelevel  pack files correctly (make sure ~/klimkit is there, edit only there not directly in home folder! then push and will be autosynced to all machines where klimkit installed with autosync option bla bla) - and add this to readme ofc
  so klim when working on different projects experiment with harnesss and tune it on the fly with kilmkit , push and that would sync everywhere! 

  need codex to be configured to use 5.5 xhigh fast by default in yolo mode

  add to readme section describing our harnesss setup with subagetns skills etc and note that current pack designed ot be run in a dedicated vm or in a sandbox where it's safe for yolo mode. -- that's recommended. add noticable disclamer that it's super important to make sure agent has minimal permissions from this vm etc. webreseaerch simon willson trifacts thing and based on that add recommendations to readme with warnings. 

  also say in readme , chrome is recommended for switchboard