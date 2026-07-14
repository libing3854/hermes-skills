# MCP Server配置模式

## 配置文件位置

| Agent | 配置路径 |
|-------|---------|
| Hermes | ~/.hermes/mcp-servers/<name>/config.json |
| Claude Code | ~/.claude/settings.json → mcpServers |
| MiMo Code | ~/.config/mimocode/mimocode.json → mcpServers |

## 配置格式（统一）

```json
{
  "command": "npx",
  "args": ["-y", "package-name"],
  "env": {
    "API_KEY": "your-key"
  },
  "timeout": 30
}
```

Python MCP Server:
```json
{
  "command": "python3.12",
  "args": ["/path/to/server.py"],
  "env": {},
  "timeout": 30
}
```

## 已配置的MCP Servers

| Server | 功能 | 安装方式 | 配置位置 |
|--------|------|---------|---------|
| Chrome DevTools | 网页控制 | npx | Hermes |
| SQLite | 数据库 | uvx | Hermes |
| Prompt Optimizer | 提示词优化 | node | Hermes |
| Mem0 | 统一记忆 | python3.12 | Hermes+Claude+MiMo |
| Tavily | 搜索增强 | npx | Hermes+Claude+MiMo |

## 注意事项
- Hermes的config.json中env变量用`${VAR_NAME}`格式引用.env中的值
- Claude Code和MiMo Code的config.json中env变量需要写入实际值
- MCP Server需要重启Agent才能生效
- Python MCP Server需要确保用python3.12（3.9不兼容新包）
