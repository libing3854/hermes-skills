---
name: mcp-server-management
description: 安装、配置、管理MCP Server的统一指南。覆盖：npm/pip安装、Hermes/Claude Code/MiMo Code多平台配置、自托管MCP编写、Mem0/Tavily/GhidraMCP等实际案例。触发条件：用户要求装MCP工具、配置MCP服务器、或问"MCP怎么用"。
tags: [mcp, server, setup, configuration, tools]
---

# MCP Server 管理指南

## 概述

MCP（Model Context Protocol）是AI Agent调用外部工具的标准协议。一个MCP Server可以同时被Hermes、Claude Code、Codex、MiMo Code等多个Agent共享。

## 安装方式

### npm包（最常见）
```bash
npm install -g @brave/brave-search-mcp-server
npm install -g tavily-mcp
```

### pip包
```bash
pip install mem0-mcp-server
```

### GitHub克隆
```bash
git clone --depth 1 https://github.com/org/repo.git ~/.hermes/mcp-servers/name/
```

## 多平台配置

**必须同时配置到所有需要使用的Agent：**

### 1. Hermes MCP配置
```bash
mkdir -p ~/.hermes/mcp-servers/<name>
cat > ~/.hermes/mcp-servers/<name>/config.json << 'EOF'
{
  "command": "npx",
  "args": ["-y", "package-name"],
  "env": {"API_KEY": "your-key"},
  "timeout": 30
}
EOF
```

### 2. Claude Code MCP配置
```python
import json, os
path = os.path.expanduser('~/.claude/settings.json')
with open(path) as f:
    cfg = json.load(f)
cfg['mcpServers']['name'] = {
    'command': 'npx',
    'args': ['-y', 'package-name'],
    'env': {'API_KEY': 'your-key'}
}
with open(path, 'w') as f:
    json.dump(cfg, f, indent=2)
```

### 3. MiMo Code MCP配置
```python
# ~/.config/mimocode/mimocode.json
cfg['mcpServers']['name'] = {
    'command': 'npx',
    'args': ['-y', 'package-name'],
    'env': {'API_KEY': 'your-key'}
}
```

### 4. Codex MCP配置
```bash
# ~/.codex/config.toml
[mcp_servers.name]
command = "npx"
args = ["-y", "package-name"]
```

## 自托管MCP Server编写

当官方MCP不支持本地模式时（如Mem0只支持云API），自己写：

```python
#!/usr/bin/env python3.12
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def my_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**依赖：** `pip install mcp` (Python 3.10+)

## Agent Skills 安装

除了MCP Server，还可以安装Agent Skills（SKILL.md格式的技能文件）：

```bash
# Vercel标准方式
npx skills add <owner>/<repo> --skill <name>

# 示例
npx skills add mattpocock/skills --skill teach
```

详见 [references/agent-skills-install.md](references/agent-skills-install.md)

## 已安装的MCP Servers

| 名称 | 用途 | 配置位置 |
|------|------|---------|
| Chrome DevTools | 浏览器控制 | ~/.hermes/mcp-servers/ |
| SQLite | 数据库操作 | ~/.hermes/mcp-servers/ |
| Prompt Optimizer | 提示优化 | ~/.hermes/mcp-servers/ |
| Mem0 | 统一记忆层 | ~/.hermes/mcp-servers/mem0-local/ |
| Tavily | 搜索增强 | ~/.hermes/mcp-servers/tavily/ |
| GhidraMCP | 逆向工程 | ~/.hermes/mcp-servers/ | ✅ 需先启动Ghidra |

## CLI工具管理（CLI-Anything Hub）

除MCP Server外，还安装了CLI-Anything Hub（`cli-hub`），管理40+个CLI工具：

```bash
# 安装
CLI_HUB_ANALYTICS=off python3.12 -m pip install --break-system-packages cli-anything-hub

# 使用
cli-hub list           # 浏览所有CLI
cli-hub install <name> # 安装CLI
cli-hub launch <name>  # 启动CLI
cli-hub can "3D建模"   # 按能力搜索
```

**⚠️ 安全注意：** CLI-Anything默认开启PostHog遥测，安装时必须关闭：
```bash
CLI_HUB_ANALYTICS=off pip install cli-anything-hub
```

**已安装的CLI（7个）：** generate-veo-video, jimeng, minimax-cli, elevenlabs, feishu, wecom, 1password-cli

**需要桌面软件的CLI（89个）：** blender/freecad/gimp/obsidian等需先安装对应软件。

## 常见坑

### 1. API Key被`redact_secrets`截断
写入API Key到.env时，`security.redact_secrets: true`会自动截断。解决：
```bash
hermes config set security.redact_secrets false
# 写入key
hermes config set security.redact_secrets true
hermes gateway restart
```

### 2. Python 3.9不支持`X | None`语法
MCP相关包（mem0ai 2.0、crawl4ai 0.5+）需要Python 3.10+。用Python 3.12：
```bash
python3.12 -m pip install --break-system-packages <package>
```

### 3. Qdrant向量维度不匹配
Mem0默认embedding维度1536（OpenAI），用HuggingFace模型需显式设置384：
```python
config = {
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'embedding_model_dims': 384,  # 必须显式设置
            'path': '/tmp/mem0_data'
        }
    }
}
```

### 7. Mem0 v2.0 search API变更
旧版用`user_id='xxx'`直接传参，新版必须用`filters`：
```python
# ❌ 旧版（v0.x）
m.search('query', user_id='xxx')
m.get_all(user_id='xxx')

# ✅ 新版（v2.0+）
m.search('query', filters={'user_id': 'xxx'})
m.get_all(filters={'user_id': 'xxx'})
```
不改会报：`ValueError: Top-level entity parameters frozenset({'user_id'}) are not supported in search()`

### 8. Mem0 openai_base_url参数名
LLM配置中base_url的参数名是`openai_base_url`，不是`base_url`：
```python
# ❌ 错误
'config': {'model': '...', 'api_key': '...', 'base_url': '...'}

# ✅ 正确
'config': {'model': '...', 'api_key': '...', 'openai_base_url': '...'}
```

### 9. 配置文件目录不存在
Hermes MCP config目录需要手动创建：
```bash
mkdir -p ~/.hermes/mcp-servers/<name>
```

### 10. 重启后MCP不生效
修改MCP配置后需要重启相关Agent。

### 11. Gateway重启级联kill
`hermes gateway restart`会连带kill Dashboard和Workspace。重启后必须：
```bash
hermes dashboard --port 9119 --no-open &
cd hermes-workspace && vite dev --host 127.0.0.1 --port 3000 &
```
详见 [hermes-maintenance skill](../hermes-maintenance/SKILL.md) 第八节。

## 参考文档

- [references/mem0-local-mcp-setup.md](references/mem0-local-mcp-setup.md) — Mem0本地MCP完整配置
- [references/mem0-v2-api-changes.md](references/mem0-v2-api-changes.md) — Mem0 v2.0 API变更速查
- [references/ghidramcp-setup.md](references/ghidramcp-setup.md) — GhidraMCP逆向工程MCP
- [references/agent-skills-install.md](references/agent-skills-install.md) — Agent Skills安装方法
- [references/python-package-security-audit.md](references/python-package-security-audit.md) — Python包安全审查清单
- [references/multica-setup.md](references/multica-setup.md) — Multica多Agent平台
