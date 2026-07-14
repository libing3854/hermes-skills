# Template-Driven Behavior Pattern

> **Core Principle:** Agents follow templates (output examples, code snippets, structured outputs) more strictly than text descriptions (rules, instructions, requirements).

## Discovery

When fixing the daily-morning-report skill (v3.5→v3.6), we discovered that:
- The skill's "输出红线" explicitly said "不要输出任何音频路径"
- But the skill also said "音频通过 MEDIA 标签发送"
- These two rules contradicted each other
- The agent followed the template (which had no MEDIA: line) and never output the audio tag
- Result: audio files were generated but never sent to Telegram

## The Pattern

```
Agent behavior priority:
1. Template/example (highest weight) ← agent copies this exactly
2. Explicit rules in instructions
3. General guidelines
4. Implicit conventions (lowest weight)
```

When the template and rules conflict, the agent follows the template.

## Implications for Skill Design

1. **Templates are the source of truth** — If you want the agent to output X, put X in the template
2. **Rules alone are not enough** — Writing "必须输出 MEDIA:标签" in the rules won't work if the template doesn't include it
3. **Contradictions are fatal** — If rule A says "don't output X" and rule B says "must output X", the agent will follow whichever matches the template (or neither)
4. **Fix all layers** — When adding a required output element, update ALL of:
   - The template/example
   - The explicit rules
   - The self-check list
   - Any other section that mentions the element

## Example

```markdown
# ❌ BROKEN: Template missing required element
## 输出模板
💬 [简短积极的鼓励寄语]

## 规则（文字描述）
- 必须在输出末尾附加 MEDIA:~/voice-memos/xxx.mp3
→ Agent follows template, never outputs MEDIA: tag

# ✅ FIXED: Template includes required element
## 输出模板
💬 [简短积极的鼓励寄语]

MEDIA:~/voice-memos/morning_report_YYYYMMDD_HHMM.mp3

## 规则（文字描述）
- 必须在输出末尾附加 MEDIA:~/voice-memos/xxx.mp3
→ Agent follows template, includes MEDIA: tag
```

## Related

This principle explains why:
- Prompt injection attacks work (agent follows injected instructions)
- Few-shot examples are powerful (agent mimics the pattern)
- Code templates in skills produce consistent output
- Self-check lists help catch missed elements (but don't replace templates)
