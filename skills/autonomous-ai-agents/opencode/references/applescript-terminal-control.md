# AppleScript Terminal Control

## Problem

AppleScript `keystroke` command doesn't work for Chinese characters - it produces garbled text.

## Solution: Clipboard Paste

Use `pbcopy` + `cmd+v` via AppleScript to send Chinese text to terminal windows.

```appleshell
-- Set clipboard content
set the clipboard to "你的中文文本"

-- Activate target window
tell application "Terminal"
    set w to window id <WINDOW_ID>
    set index of w to 1
    activate
end tell

delay 0.5

-- Paste from clipboard
tell application "System Events"
    keystroke "v" using command down
    delay 0.3
    key code 36  -- Enter
end tell
```

## Finding Window ID

```appleshell
tell application "Terminal"
    set winNames to {}
    repeat with w in every window
        set end of winNames to (id of w as text) & ": " & name of w
    end repeat
    return winNames
end tell
```

## Requirements

- System Settings → Privacy & Security → Accessibility → Terminal.app must be checked
- Window must be in the foreground (use `set index of w to 1`)

## Use Cases

- Controlling MiMo Code TUI with Chinese input
- Controlling any terminal application that needs Chinese text input
- Automating interactive CLI tools

## Limitations

- Only works with Terminal.app (not iTerm2 or other terminals)
- Requires Accessibility permissions
- Window must be visible (can't control background windows reliably)