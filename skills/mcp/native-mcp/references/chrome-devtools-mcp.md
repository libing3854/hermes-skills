# Chrome DevTools MCP — Configuration Reference

Repository: https://github.com/ChromeDevTools/chrome-devtools-mcp
Stars: 42k+ | Latest: v1.1.1 (as of 2026-05-31)

## Installation

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  chrome-devtools:
    command: npx
    args:
      - -y
      - chrome-devtools-mcp@latest
      - --headless
      - --no-usage-statistics
    timeout: 120
    connect_timeout: 60
```

## Common Configuration Flags

| Flag | Description |
|------|-------------|
| `--headless` | Run Chrome without UI (recommended for automation) |
| `--no-usage-statistics` | Opt out of Google telemetry |
| `--slim` | Expose only 3 core tools (navigation, script, screenshot) |
| `--isolated` | Temporary user-data-dir, auto-cleaned on close |
| `--viewport=1280x720` | Set initial viewport size |
| `--browser-url=http://127.0.0.1:9222` | Connect to existing Chrome instance |
| `--autoConnect` | Auto-connect to Chrome 144+ with remote debugging enabled |
| `--experimentalVision` | Enable coordinate-based tools (click_at x,y) |
| `--experimentalMemory` | Enable heap snapshot tools |
| `--experimentalScreencast` | Enable screencast recording (requires ffmpeg) |

## Registered Tools (45+)

Tools are prefixed `mcp_chrome_devtools_` in Hermes.

### Input Automation (10)
- click, drag, fill, fill_form, handle_dialog, hover
- press_key, type_text, upload_file, click_at

### Navigation (6)
- close_page, list_pages, navigate_page
- new_page, select_page, wait_for

### Emulation (2)
- emulate, resize_page

### Performance (3)
- performance_analyze_insight
- performance_start_trace, performance_stop_trace

### Network (2)
- get_network_request, list_network_requests

### Debugging (8)
- evaluate_script, get_console_message
- lighthouse_audit, list_console_messages
- take_screenshot, take_snapshot
- screencast_start, screencast_stop

### Memory (5)
- take_heapsnapshot, get_heapsnapshot_class_nodes
- get_heapsnapshot_details, get_heapsnapshot_retainers
- get_heapsnapshot_summary

### Extensions (5)
- install_extension, list_extensions
- reload_extension, trigger_extension_action
- uninstall_extension

## Connecting to Running Chrome

### Method 1: Auto-connect (Chrome 144+)
1. In Chrome, go to `chrome://inspect/#remote-debugging` and enable
2. Add `--autoConnect` to MCP server args

### Method 2: Manual port forwarding
1. Start Chrome with: `--remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile`
2. Add `--browser-url=http://127.0.0.1:9222` to MCP server args

## Pitfalls

- **System pip vs Hermes venv**: `pip3 install mcp` installs to system Python (3.9 on macOS), which is too old. Use `/Users/libing/.hermes/hermes-agent/venv/bin/python -m pip install mcp`
- **No pip in venv**: The Hermes venv may not have `pip` as standalone command. Always use `python -m pip`
- **User data directory**: Default is `$HOME/.cache/chrome-devtools-mcp/chrome-profile-stable`. Use `--isolated` for temporary profiles
- **Telemetry**: Enabled by default. Use `--no-usage-statistics` to disable
