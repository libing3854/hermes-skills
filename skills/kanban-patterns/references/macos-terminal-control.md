# macOS Terminal Control via AppleScript

## Overview

Hermes can control foreground Terminal.app windows using AppleScript, enabling interaction with interactive CLI tools (like MiMo Code, SSH sessions, etc.) that are running in separate terminal windows.

## Key Technique

### Find Terminal Windows

```bash
osascript -e '
tell application "Terminal"
    set winNames to {}
    repeat with w in every window
        set end of winNames to name of w
    end repeat
    return winNames
end tell
'
```

### Get Window ID by Name

```bash
osascript -e '
tell application "Terminal"
    repeat with w in every window
        if name of w contains "mimo" then
            return id of w
        end if
    end repeat
end tell
'
```

### Send Input to Terminal Window

```bash
# Method 1: Keystroke simulation (requires Accessibility permissions)
osascript -e '
tell application "Terminal"
    activate
    set w to window id <WINDOW_ID>
    set index of w to 1
end tell
delay 0.5
tell application "System Events"
    keystroke "your input here"
    key code 36  # Enter key
end tell
'
```

```bash
# Method 2: do script (creates new command in existing tab)
osascript -e '
tell application "Terminal"
    set w to window id <WINDOW_ID>
    set t to tab 1 of w
    do script "your command" in t
end tell
'
```

## Prerequisites

### Accessibility Permissions

For `keystroke` simulation to work:
- System Settings → Privacy & Security → Accessibility
- Add Terminal.app and Hermes to the allowed list

### Window Identification

Terminal window names follow the format:
```
<username> — <current_process> — <columns>×<rows>
```
Example: `libing — mimo — 120×30`

Use `contains` matching since the process name is embedded in the window title.

## Limitations

1. **`do script` creates new commands** — it doesn't send input to an existing interactive prompt. For tools like MiMo Code that expect keyboard input, use `keystroke` instead.

2. **`keystroke` requires focus** — the Terminal window must be activated first, and the keystroke goes to the frontmost window.

3. **⚠️ `keystroke` DOES NOT support Chinese characters** — sending Chinese text via `keystroke "你好"` produces garbled output like "啦，aaaaa". For Chinese text, use the **clipboard paste method** instead (see below).

4. **No output capture** — AppleScript can send input but cannot read the terminal's current content. To verify what happened, use `screencapture` or check the process output separately.

5. **Race conditions** — when sending multiple keystrokes, add `delay` between them to ensure the target application processes each input.

## Sending Chinese Text (Clipboard Paste Method)

`keystroke` cannot handle Chinese characters. Use clipboard paste instead:

```bash
osascript -e '
tell application "Terminal"
    set w to window id <WINDOW_ID>
    set index of w to 1
    activate
end tell

delay 0.5

set the clipboard to "你要发送的中文内容"

delay 0.3

tell application "System Events"
    keystroke "v" using command down
    delay 0.3
    key code 36  # Enter
end tell
'
```

**Why this works:** `set the clipboard to` handles Unicode correctly, and `Cmd+V` paste preserves the encoding. The `keystroke` command uses a different input path that garbles non-ASCII characters.

**Pattern for multi-line Chinese input:**
```bash
# Send multiple lines by pasting each line separately
for line in "第一行内容" "第二行内容" "第三行内容"; do
    osascript -e "
        set the clipboard to \"$line\"
        tell application \"System Events\" to keystroke \"v\" using command down
    "
    sleep 0.3
done
```

## Use Cases

- **Interactive CLI tools**: Send commands to MiMo Code, SSH sessions, database CLIs
- **Automated testing**: Script keyboard input for terminal-based applications
- **Remote control**: Control foreground terminal sessions from Hermes

## Diagnostic Commands

```bash
# List all Terminal windows
osascript -e 'tell application "Terminal" to get name of every window'

# Get frontmost window
osascript -e 'tell application "Terminal" to get name of front window'

# Check if Accessibility is enabled
osascript -e 'tell application "System Events" to get name of every process whose background only is false'
'
```
