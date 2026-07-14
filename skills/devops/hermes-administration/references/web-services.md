# Hermes Web Services Reference

## Architecture

Hermes has two web interfaces:

1. **Dashboard** (port 9119) — Management UI
   - Profile switching
   - Cron job management
   - Session history
   - Configuration

2. **Workspace** (port 3000) — Development Environment
   - Vite dev server
   - Live reload
   - Code editing

## Startup Commands

### Dashboard
```bash
# Standard startup
hermes dashboard --port 9119 --no-open

# With specific port (if 9119 occupied)
hermes dashboard --port 9120 --no-open
```

### Workspace
```bash
# From workspace directory
cd /Users/libing/hermes-workspace && vite dev --host 127.0.0.1 --port 3000
```

## Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :9119

# Kill the process
kill <PID>
```

### Dashboard Not Loading
1. Check if process is running: `lsof -i :9119`
2. Check logs: `~/.hermes/logs/`
3. Restart: `hermes gateway restart`

### Workspace Not Loading
1. Check node process: `lsof -i :3000`
2. Check vite logs
3. Reinstall deps: `cd /Users/libing/hermes-workspace && npm install`

## User Preferences

- User refers to web services as "web" or "web工具"
- Dashboard = management interface (port 9119)
- Workspace = development environment (port 3000)
- Do NOT confuse with port 8080 (wrong port)
