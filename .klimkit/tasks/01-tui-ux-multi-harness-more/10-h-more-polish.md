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
  "https://odev.../switchboard" so it reports its sessions into th
  is central Switchboard. This central VM does not need to report
  to itself.

  ---

  that's very confusing. i might have server only but no collecting seeesions form some machine! i'd do it true by default, and when client only it's true without server 


  ---

  tg notifications: review all possible notifications and polish them so they alll are very nice formatted with emojies, etc. 

  ⚡ Quick open on this Mac -> that's an old link for mac automation, we're not using it anymore. also remove related code (for Automator and some mac daemon for deeplinking)

  instead need a link that opens klimkit webapp on a cetain tab, like link in browser notifications (works correctly)