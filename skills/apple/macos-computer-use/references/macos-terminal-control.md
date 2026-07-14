# macOS Terminal Control via AppleScript

## Overview

AppleScript can control foreground Terminal.app windows — sending keyboard input, switching tabs, and interacting with TUI applications (MiMo Code, SSH, htop, etc.). This is useful when the `computer_use` tool is not available or when you need to interact with a specific terminal window.

## Prerequisites

- **Accessibility permissions**: System Settings → Privacy & Security → Accessibility → Terminal.app must be checked
- The target Terminal window must be open and visible

## Finding Terminal Windows

```applescript
tell application "Terminal"
    set winNames to {}
    repeat with w in every window
        set end of winNames to (id of w as text) & ": " & name of w
    end repeat
    return winNames
end tell
```

Returns format: `"12345: libing — mimo — 120×30"`

## Sending Text Input

### ⚠️ Critical: Chinese text requires clipboard paste

`keystroke` does NOT work for Chinese characters — it produces garbled output. Use clipboard paste instead:

```applescript
-- Step 1: Activate and focus the target window
tell application "Terminal"
    set w to window id 12345
    set index of w to 1
    activate
end tell

delay 0.5

-- Step 2: Set clipboard content (Chinese safe)
set the clipboard to "你好，世界"

delay 0.3

-- Step 3: Paste and submit
tell application "System Events"
    keystroke "v" using command down
    delay 0.3
    key code 36  -- Enter key
end tell
```

### ASCII-only text (English, commands)

For ASCII-only input, `keystroke` works fine:

```applescript
tell application "System Events"
    keystroke "ls -la"
    key code 36  -- Enter
end tell
```

## Key Code Reference

| Key | Code |
|-----|------|
| Return/Enter | `key code 36` |
| Escape | `key code 53` |
| Tab | `key code 48` |
| Delete/Backspace | `key code 51` |
| Arrow Up | `key code 126` |
| Arrow Down | `key code 125` |
| Arrow Left | `key code 123` |
| Arrow Right | `key code 124` |

## Modifier Keys

```applescript
keystroke "x" using command down      -- Cmd+X
keystroke "x" using {command, shift}  -- Cmd+Shift+X
keystroke "x" using control down      -- Ctrl+X
keystroke "x" using {control, alt}    -- Ctrl+Alt+X
```

## Complete Workflow Example

```applescript
-- 1. Find the MiMo Code window
tell application "Terminal"
    set targetWindow to missing value
    repeat with w in every window
        if name of w contains "mimo" then
            set targetWindow to w
            exit repeat
        end if
    end repeat
    
    if targetWindow is missing value then
        return "MiMo Code window not found"
    end if
    
    -- 2. Bring window to front
    set index of targetWindow to 1
    activate
end tell

delay 1

-- 3. Send Chinese input via clipboard
set the clipboard to "帮我修改第277章的AI高频词"
delay 0.3

tell application "System Events"
    keystroke "v" using command down
    delay 0.3
    key code 36  -- Submit
end tell
```

## Limitations

1. **No output reading**: AppleScript can send input but cannot read terminal output. You must ask the user to verify or use `computer_use` tool for visual verification.
2. **Window must be visible**: The target window must be on screen (not minimized or hidden behind other windows).
3. **No background control**: Unlike `computer_use`, AppleScript steals focus — the user's cursor and keyboard focus will shift to Terminal.app.
4. **Race conditions**: Add `delay` between commands to avoid input arriving before the target app is ready.

## When to Use This vs computer_use

| Scenario | Use |
|----------|-----|
| Need to send Chinese text to TUI app | AppleScript clipboard paste |
| Need to read terminal output | `computer_use` (visual) |
| Background automation (no focus steal) | `computer_use` |
| Simple ASCII commands | Either works |
| User is actively using the terminal | Ask first, or use `computer_use` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chinese text appears garbled | Use clipboard paste instead of `keystroke` |
| "Not authorized" error | Grant Accessibility permission to Terminal.app |
| Window not found | Check window title with `osascript -e 'tell application "Terminal" to get name of every window'` |
| Input arrives too fast | Add more `delay` between commands (0.5-1 second) |
| Window ID changed | Re-fetch window list — IDs change when windows are closed/opened |
