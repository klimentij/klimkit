on run argv
  set targetUrl to "https://your-host.tailnet.ts.net/?folder=/absolute/workspace/path"
  if (count of argv) > 0 then set targetUrl to item 1 of argv

  tell application "Google Chrome"
    activate

    repeat with w from 1 to count of windows
      repeat with t from 1 to count of tabs of window w
        set theTab to tab t of window w
        if (URL of theTab) is targetUrl then
          set minimized of window w to false
          set index of window w to 1
          set active tab index of window w to t
          activate

          tell application "System Events"
            tell process "Google Chrome"
              set frontmost to true
            end tell
          end tell

          return "focused"
        end if
      end repeat
    end repeat

    open location targetUrl
  end tell

  tell application "System Events"
    tell process "Google Chrome"
      set frontmost to true
    end tell
  end tell

  return "opened"
end run
