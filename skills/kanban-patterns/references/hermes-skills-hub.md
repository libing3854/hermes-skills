# Hermes Skills Hub

## Overview

Hermes Agent has a built-in Skills Hub with **92,109 skills** across multiple registries, including **97 official optional skills** from Nous Research.

**Access:** `hermes skills browse` / `hermes skills search` / `hermes skills install`

## Quick Commands

```bash
# Browse all available skills (paginated)
hermes skills browse

# Search for specific skills
hermes skills search "comfyui"
hermes skills search "writing"
hermes skills search "image generation"

# Install a skill
hermes skills install <skill-name>

# List installed skills
hermes skills list

# Check for updates
hermes skills check
```

## Skill Sources

| Source | Description |
|--------|-------------|
| official | 97 official optional skills from Nous Research |
| skills.sh | Community skills indexed from GitHub |
| clawhub | ClawHub marketplace |
| github | Direct GitHub repos |

## Notable Official Skills

From the tweet by @Fluyeporlaweb (2026-06-13):

- `macos-computer-use` — Control Mac desktop in background without stealing focus
- `comfyui` — Generate images, video, audio with ComfyUI
- `humanizer` — Strip AI language, add real voice
- `popular-web-designs` — 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS

## Integration with Kanban Workflow

Skills can be used in kanban task bodies:

```bash
hermes kanban create "Task" \
  --assignee shanli \
  --workspace "dir:/path" \
  --body "## Task
Use the humanizer skill to strip AI-isms from the output.
..."
```

## Reference

- Official docs: https://hermes-agent.nousresearch.com/docs/skills/
- Skills Hub: https://agentskills.io
