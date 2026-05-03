use scripting additions

property appName : "Codex Focus"
property supportFolderName : "CodexFocus"
property targetsFileName : "targets.json"

on run
  return
end run

on open location deepLink
  try
    my appendLog("Received deep link: " & deepLink)
    set targetUrl to my resolveTargetUrl(deepLink)
    my appendLog("Resolved target URL: " & targetUrl)
    if targetUrl is missing value or targetUrl is "" then error "No target URL resolved from link: " & deepLink
    my ensureSupportedUrl(targetUrl)
    if my focusExistingChromeTab(targetUrl) then
      my closeSafariTrampolineTabs()
      my appendLog("Focused existing Chrome tab")
      return
    end if
    my appendLog("No existing Chrome tab found; opening URL")
    my openChromeUrl(targetUrl)
    my closeSafariTrampolineTabs()
  on error errMsg number errNum
    my appendLog("Error " & errNum & ": " & errMsg)
    if errNum is -1743 or errMsg contains "Not authorized to send Apple events" then
      display alert appName message "Grant Automation permission to Codex Focus for Google Chrome and System Events, then run the deep link again." as warning
    else
      display alert appName message errMsg as warning
    end if
  end try
end open location

on ensureSupportedUrl(targetUrl)
  if targetUrl starts with "https://" then return
  if targetUrl starts with "http://" then return
  error "Unsupported target URL: " & targetUrl
end ensureSupportedUrl

on resolveTargetUrl(deepLink)
  set explicitUrl to my getQueryValue(deepLink, "url")
  if explicitUrl is not missing value and explicitUrl is not "" then return explicitUrl

  set targetName to my getQueryValue(deepLink, "target")
  if targetName is missing value or targetName is "" then return missing value

  return my lookupNamedTarget(targetName)
end resolveTargetUrl

on getQueryValue(deepLink, wantedKey)
  set queryStart to offset of "?" in deepLink
  if queryStart is 0 then return missing value

  set queryString to text (queryStart + 1) thru -1 of deepLink
  set fragmentStart to offset of "#" in queryString
  if fragmentStart is not 0 then set queryString to text 1 thru (fragmentStart - 1) of queryString

  set previousDelimiters to AppleScript's text item delimiters
  try
    set AppleScript's text item delimiters to "&"
    set pairsList to text items of queryString

    repeat with onePair in pairsList
      set AppleScript's text item delimiters to "="
      set pairItems to text items of onePair
      if (count of pairItems) > 0 then
        set rawKey to item 1 of pairItems
        set rawValue to ""
        if (count of pairItems) > 1 then
          set rawValue to (items 2 thru -1 of pairItems) as text
        end if

        set decodedKey to my urlDecode(rawKey)
        if decodedKey is wantedKey then
          set AppleScript's text item delimiters to previousDelimiters
          return my urlDecode(rawValue)
        end if
      end if

      set AppleScript's text item delimiters to "&"
    end repeat
  on error
    set AppleScript's text item delimiters to previousDelimiters
    error
  end try

  set AppleScript's text item delimiters to previousDelimiters
  return missing value
end getQueryValue

on urlDecode(encodedText)
  if encodedText is "" then return ""
  set py to "import sys, urllib.parse; print(urllib.parse.unquote_plus(sys.argv[1]))"
  return do shell script "/usr/bin/python3 -c " & quoted form of py & " " & quoted form of encodedText
end urlDecode

on lookupNamedTarget(targetName)
  set configPath to POSIX path of ((path to library folder from user domain) as text) & "Application Support/" & supportFolderName & "/" & targetsFileName
  set py to "import json, pathlib, sys; path = pathlib.Path(sys.argv[1]); target = sys.argv[2]; data = json.loads(path.read_text()) if path.exists() else {'targets': {}}; print(data.get('targets', {}).get(target, ''))"
  set resolvedUrl to do shell script "/usr/bin/python3 -c " & quoted form of py & " " & quoted form of configPath & " " & quoted form of targetName

  if resolvedUrl is "" then
    error "No configured target named '" & targetName & "' in " & configPath
  end if

  return resolvedUrl
end lookupNamedTarget

on closeSafariTrampolineTabs()
  set trampolinePrefix to "http://127.0.0.1:43123/open"
  delay 0.4

  tell application "Safari"
    if not running then return

    repeat with w from (count of windows) to 1 by -1
      set tabsToClose to {}

      repeat with t from (count of tabs of window w) to 1 by -1
        try
          set currentURL to URL of tab t of window w
          if currentURL starts with trampolinePrefix then set end of tabsToClose to t
        end try
      end repeat

      repeat with tabIndex in tabsToClose
        close tab tabIndex of window w
      end repeat
    end repeat
  end tell
end closeSafariTrampolineTabs

on focusExistingChromeTab(targetUrl)
  tell application "Google Chrome"
    if not running then return false
    activate

    repeat with w from 1 to count of windows
      repeat with t from 1 to count of tabs of window w
        set theTab to tab t of window w
        if (URL of theTab) is targetUrl then
          set minimized of window w to false
          set active tab index of window w to t
          set index of window w to 1
          activate
          my bringChromeFront()
          return true
        end if
      end repeat
    end repeat
  end tell

  return false
end focusExistingChromeTab

on openChromeUrl(targetUrl)
  tell application "Google Chrome"
    activate
    open location targetUrl
  end tell

  my bringChromeFront()
end openChromeUrl

on bringChromeFront()
  tell application "System Events"
    if exists process "Google Chrome" then
      tell process "Google Chrome"
        set frontmost to true
      end tell
    end if
  end tell
end bringChromeFront

on appendLog(messageText)
  try
    set logPath to POSIX path of ((path to library folder from user domain) as text) & "Application Support/" & supportFolderName & "/codex-focus.log"
    do shell script "/bin/mkdir -p " & quoted form of (POSIX path of ((path to library folder from user domain) as text) & "Application Support/" & supportFolderName)
    do shell script "/bin/echo " & quoted form of ((do shell script "/bin/date '+%Y-%m-%d %H:%M:%S'") & " " & messageText) & " >> " & quoted form of logPath
  end try
end appendLog
