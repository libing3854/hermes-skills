# Kanban Profiles Configuration

## Problem (2026-06-26)

Default `kanban.profiles` in `~/.hermes/config.yaml` only includes `["lili", "shanli"]`. If you try to dispatch a task to nvlinshi or shanli-agnes20flash, the task will be created but never dispatched.

## Symptom

- Task stays in `ready` status indefinitely
- `hermes kanban dispatch` reports `Spawned: 0`
- No error message — silent failure

## Solution

```bash
# Check current profiles
grep "profiles:" ~/.hermes/config.yaml

# Add all required assignee profiles
sed -i '' "s/profiles: '\[\"lili\", \"shanli\"\]'/profiles: '[\"lili\", \"shanli\", \"nvlinshi\", \"shanli-agnes20flash\"]'/" ~/.hermes/config.yaml
```

Requires config approval (Hermes asks for user confirmation).

## Update (2026-07-03)

Added `mimo-v25` to profiles list for MiMo v2.5 writing tasks.

Always restart gateway after changing profiles:
```bash
hermes gateway start --profile default
```

## Reference

Each profile also has its own `kanban.profiles` in `~/.hermes/profiles/<name>/config.yaml`. The default config's list is what the dispatcher uses.
