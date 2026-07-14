---
name: ai-system-prompt-analysis
description: "Analyze and compare AI system prompts from leaked collections. Structured extraction, key insight summarization, cross-model comparison."
version: 1.0.0
author: Lilith
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [AI, System-Prompts, Analysis, Research, Anthropic, OpenAI, Google]
    related_skills: [github-discovery, free-llm-discovery]
---

# AI System Prompt Analysis

Analyze and compare AI system prompts from public repositories. Use this skill when the user wants to understand how different AI models are configured, compare their behaviors, or research prompt engineering patterns.

## Primary Source

**asgeirtj/system_prompts_leaks** (57k+ stars, actively maintained)
- URL: https://github.com/asgeirtj/system_prompts_leaks
- Structure: Organized by vendor (Anthropic, OpenAI, Google, Microsoft, etc.)
- Updates: Very active (often daily)

## Content Extraction Method

GitHub markdown files can be very large. Use this chunked extraction approach:

```javascript
// Get first 5000 chars
document.querySelector('article.markdown-body')?.innerText?.substring(0, 5000)

// Get next chunk (adjust range as needed)
document.querySelector('article.markdown-body')?.innerText?.substring(5000, 10000)
```

**Why this works better than browser_snapshot(full=true)**:
- More control over chunk size
- Avoids truncation/summarization by the snapshot tool
- Can focus on specific sections

## Structured Analysis Framework

When analyzing a system prompt, extract these key dimensions:

### 1. Core Behavior Directives
- Search/web access rules
- Tool usage preferences
- Proactivity level (does it wait or act?)

### 2. Safety Boundaries
- Refusal triggers and handling
- Child safety rules
- Weapon/malware restrictions
- Content moderation approach

### 3. Tone and Formatting
- Default tone (warm, professional, casual)
- Formatting preferences (prose vs lists, bold usage)
- Emoji/cursor word restrictions
- Response length tendencies

### 4. Product Knowledge
- Model version and capabilities
- Available tools and products
- Beta/preview features

### 5. Unique Characteristics
- What makes this model's prompt different?
- Any surprising or notable instructions?

## Comparison Template

When comparing multiple models, use this structure:

```
| Dimension | Model A | Model B |
|-----------|---------|---------|
| Search behavior | ... | ... |
| Proactivity | ... | ... |
| Tone | ... | ... |
| Safety strictness | ... | ... |
| Unique features | ... | ... |
```

## Vendor-Specific Notes

### Anthropic (Claude)
- Models: Opus, Sonnet, Haiku, Mythos, Fable
- Tiers: Mythos > Opus > Sonnet > Haiku
- Products: Claude Code, Cowork, Chrome/Excel/PowerPoint agents
- Key traits: Search-first, warm tone, child safety emphasis

### OpenAI (ChatGPT)
- Models: GPT-5.x series, Codex
- Products: ChatGPT, Codex CLI, DALL-E
- Check for: Memory system, browsing, code execution

### Google (Gemini)
- Models: Gemini 3.x, Flash, Pro
- Products: Gemini CLI, Antigravity, Jules
- Check for: Multimodal capabilities, workspace integration

## Pitfalls

- **Prompt versioning**: Same model name may have different prompts over time
- **Completeness**: Leaked prompts may be partial or modified
- **Context**: Some instructions only apply in specific product contexts
- **Rate limits**: GitHub API has limits; use browser for bulk reading
