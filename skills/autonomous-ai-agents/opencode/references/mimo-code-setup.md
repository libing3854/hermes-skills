# MiMo Code Setup & Control

## Installation

```bash
curl -fsSL https://mimo.xiaomi.com/install | bash
```

Binary location: `~/.mimocode/bin/mimo`

## Server Mode

MiMo Code can run as a headless server for programmatic control:

```bash
# Start server
mimo serve --port 3000

# Check if server is running
curl http://localhost:3000/health
```

## OpenCode SDK Integration

MiMo Code is based on OpenCode and supports the OpenCode SDK:

```javascript
// npm install @opencode-ai/sdk
const { OpenCode } = require('@opencode-ai/sdk');

const client = new OpenCode({ port: 3000 });
const session = await client.session.create();
await client.session.prompt(session.id, 'Your task here');
```

## Hermes Plugin

A Hermes plugin for MiMo Code control is available at:
`~/.hermes/plugins/mimo-code/`

Tools provided:
- `mimo_task` — One-shot task execution
- `mimo_server_start/stop/status` — Server management
- `mimo_session_create/prompt/messages/abort/list` — Session management

## Interactive TUI Control

For controlling MiMo Code TUI with Chinese input, use AppleScript clipboard paste:
See `references/applescript-terminal-control.md`

## Keybindings (TUI)

| Key | Action |
|-----|--------|
| `Tab` | Switch mode |
| `Ctrl+P` | Settings |
| `@` | Add file |
| `$` | Sub-agent |
| `/` | Invoke command |

## Limitations

- MiMo-V2.5 free tier has rate limits (triggers "Too many requests")
- Large tasks may timeout or get stuck
- Server mode requires Python 3.10+
