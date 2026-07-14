# Cron Job Framework Error Diagnosis

> First encountered: 2026-06-22
> Symptom: Cron job loads skill successfully but fails with framework ImportError

## Case Study: `inject_memory_provider_tools` ImportError

### Symptom
- Cron output file is 22KB+ (skill loaded fine)
- Error at end of output: `ImportError: cannot import name 'inject_memory_provider_tools' from 'agent.memory_manager'`
- All agent-mode cron jobs affected (morning report, AI weekly, GitHub trending, financial dashboard)
- Script-mode cron jobs (no_agent=true) unaffected

### Root Cause
Hermes Agent update added `inject_memory_provider_tools` to `agent/memory_manager.py`. The running Gateway process cached the old module version at startup. New cron jobs importing from the updated module fail because the running process still has the old bytecode cache.

### Verification
```bash
# Confirm function exists in source
grep -n "def inject_memory_provider_tools" ~/.hermes/hermes-agent/agent/memory_manager.py
# Should show line number (e.g., line 65)

# Confirm import fails in current process context
cd ~/.hermes/hermes-agent && python3 -c "from agent.memory_manager import inject_memory_provider_tools; print('OK')"
# If this fails with TypeError (not ImportError), it's a Python version issue

# Confirm venv Python works
~/.hermes/hermes-agent/venv/bin/python3 -c "from agent.memory_manager import inject_memory_provider_tools; print('OK')"
# Should print "OK"
```

### Fix
```bash
hermes gateway restart
```

### Why restart works
Gateway restart spawns a new Python process that loads fresh `.pyc` bytecode files. The stale cache is bypassed.

### Prevention
After any Hermes Agent update (`git pull` or `hermes update`), restart the Gateway to pick up module changes:
```bash
hermes gateway restart
```

## General Pattern: Module Import Errors in Cron Jobs

When cron jobs fail with ImportError/TypeError from `agent.*` or `tools.*` modules:

1. **Check if the function/class exists in source**: `grep -rn "name" ~/.hermes/hermes-agent/agent/`
2. **Check Python version**: `~/.hermes/hermes-agent/venv/bin/python3 --version` (need 3.10+ for `X | Y` union syntax)
3. **Check if Gateway was restarted after last code change**: `ps -p <gateway_pid> -o lstart`
4. **Fix**: `hermes gateway restart`

### Python Version Compatibility
| Syntax | Min Python | Example Error |
|--------|-----------|---------------|
| `Callable \| None` | 3.10 | `TypeError: unsupported operand type(s) for \|` |
| `X \| Y` union types | 3.10 | `TypeError: unsupported operand type(s) for \|` |
| `match/case` | 3.10 | `SyntaxError: invalid syntax` |
| `tomllib` | 3.11 | `ModuleNotFoundError: No module named 'tomllib'` |

If the venv Python is 3.10+ but system Python is 3.9, cron jobs should use venv Python (they do, via Gateway process).
