# Web Start — Three-Service Launch

When the user says "启动web" or "start web", launch three services:

| Service | Default Port | Command | Notes |
|---------|:----:|---------|-------|
| Gateway | `:8642` (API) / varies (main) | `hermes gateway run --replace` | Main port depends on config; API server port set via `platforms.api_server.port` |
| Dashboard | `:9119` | `hermes dashboard` | Web UI for kanban, skills, config, jobs |
| Workspace GUI | `:3000` | `cd ~/hermes-workspace && pnpm dev --port 3000` | Chat + file + terminal UI |

## Launch Script

A convenience script exists at `~/.hermes/scripts/web-start.sh` that:
1. Checks each service — skips if already running
2. Starts only missing services
3. Reports final status for all three

```bash
bash ~/.hermes/scripts/web-start.sh
```

## `.env` Configuration

The workspace `.env` at `~/hermes-workspace/.env` should have explicit backend URLs:

```env
HERMES_API_URL=http://127.0.0.1:8642
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
```

These tell the workspace frontend where to find the Gateway (sessions API, chat) and Dashboard (kanban, skills, config, jobs).

## Workspace Startup Pitfall

The workspace MUST be started via `pnpm dev` — **not** bare `vite` or `vite dev`:

```bash
# ✅ Correct — pnpm puts vite in PATH
cd ~/hermes-workspace && pnpm dev

# ❌ Wrong — "vite: command not found"
cd ~/hermes-workspace && vite dev --port 3000
```

The `web-start.sh` script may fail silently on the workspace step if the vite process exits. After running the script, always verify port 3000 is listening:

```bash
lsof -i :3000 -P -n | head -3
```

If not running, start manually: `cd ~/hermes-workspace && pnpm dev`.

## Post-Launch Verification

Always verify all three services after startup:

```bash
echo "Gateway: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8642 2>/dev/null || echo '未响应')"
echo "Workspace: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo '未响应')"
echo "Dashboard: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:9119 2>/dev/null || echo '未响应')"
```

All three should return `200`. If Gateway is already running from launchd, it may be on a different main port — check with `lsof -i -P | grep LISTEN | grep -E "(hermes|node)"`.

## Post-Update Checklist

After `hermes update`, restart the gateway to pick up new code:

```bash
hermes gateway restart
```

If you see `ImportError` after updating, stale `.pyc` bytecode may be cached:

```bash
find ~/.hermes/hermes-agent -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find ~/.hermes/hermes-agent -name "*.pyc" -delete 2>/dev/null
hermes gateway restart
```

To see what changed in the update:

```bash
cd ~/.hermes/hermes-agent && git log --oneline -20
```

## Troubleshooting

- **Dashboard not found:** Run `hermes dashboard` in background
- **Workspace shows "backend does not support sessions API":** Dashboard is not running — start it on :9119
- **Gateway 8642 not listening:** Check `API_SERVER_ENABLED=true` in `~/.hermes/.env`, then restart gateway
- **Workspace not starting (vite: command not found):** Use `pnpm dev` instead of bare `vite`
