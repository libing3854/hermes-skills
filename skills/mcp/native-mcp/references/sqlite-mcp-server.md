# SQLite MCP Server

## Installation

```bash
# Verify uvx is available
which uvx

# Test the server directly
uvx mcp-server-sqlite --help
```

## Configuration

### Via CLI

```bash
hermes mcp add sqlite --command uvx --args "mcp-server-sqlite --db-path /path/to/database.db"
echo "y" | hermes mcp add sqlite --command uvx --args "mcp-server-sqlite --db-path /path/to/database.db"
```

### Via config.yaml

```yaml
mcp_servers:
  sqlite:
    command: uvx
    args:
      - mcp-server-sqlite
      - --db-path
      - /Users/libing/Desktop/中岛美雪语音克隆/voice_clone.db
    connect_timeout: 60
    timeout: 120
```

**Important:** When editing config.yaml manually, args must be a YAML list (each item separate), NOT a single quoted string. The single-string format causes "Connection closed" errors.

## Available Tools

| Tool | Description |
|------|-------------|
| `read_query` | Execute SELECT queries |
| `write_query` | Execute INSERT/UPDATE/DELETE |
| `create_table` | Create new tables |
| `list_tables` | List all tables |
| `describe_table` | Get table schema |
| `append_insight` | Add business insights |

## Troubleshooting

### "Connection closed" error

**Cause:** Args formatted as a single string instead of a list.

```yaml
# ❌ WRONG
args:
  - "mcp-server-sqlite --db-path /path/to/db"

# ✅ CORRECT
args:
  - mcp-server-sqlite
  - --db-path
  - /path/to/db
```

### "No such file or directory" error

**Cause:** Command includes the full path with args (e.g., `"uvx mcp-server-sqlite"`).

**Fix:** Use `--command uvx` and `--args "mcp-server-sqlite ..."` separately.
