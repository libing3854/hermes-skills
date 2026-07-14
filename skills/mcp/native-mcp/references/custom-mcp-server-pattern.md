# Custom MCP Server Creation Pattern

When a project's MCP server is too complex to install (Docker unavailable, monorepo with `workspace:*` deps, Node.js version mismatch), create a lightweight custom server instead.

## When to Use

- Project requires Docker but it's not installed
- Project uses pnpm workspaces / `workspace:*` protocol (npm can't resolve)
- Node.js version requirements don't match system version
- Project has heavy dependencies or complex build steps
- You only need a subset of the project's functionality

## Pattern

### 1. Create server directory

```bash
mkdir -p ~/.hermes/mcp-servers/<server-name>
```

### 2. Create `server.mjs` (ESM module)

```javascript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  { name: 'my-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'my_tool',
      description: 'What it does',
      inputSchema: {
        type: 'object',
        properties: {
          input: { type: 'string', description: 'Input parameter' }
        },
        required: ['input']
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  // Handle tool calls
  return {
    content: [{ type: 'text', text: JSON.stringify({ result: 'done' }) }]
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 3. Create `package.json`

```json
{
  "name": "hermes-<server-name>",
  "version": "1.0.0",
  "type": "module",
  "main": "server.mjs",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.28.0"
  }
}
```

### 4. Install and configure

```bash
cd ~/.hermes/mcp-servers/<server-name>
npm install
```

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  <server-name>:
    command: node
    args:
      - /Users/libing/.hermes/mcp-servers/<server-name>/server.mjs
    timeout: 60
    connect_timeout: 30
```

### 5. Restart Hermes

```bash
hermes gateway restart
```

## Pitfalls

- **ESM required**: Use `.mjs` extension or set `"type": "module"` in package.json
- **MCP SDK version**: Must be `^1.28.0` for the imports used above
- **Tool naming**: Tools auto-register as `mcp_{server-name}_{tool-name}`
- **No hot-reload**: Server changes require Hermes restart
