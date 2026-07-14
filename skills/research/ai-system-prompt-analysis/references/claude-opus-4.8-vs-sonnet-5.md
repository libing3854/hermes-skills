# Claude Opus 4.8 vs Sonnet 5 - Key Differences

Analyzed from asgeirtj/system_prompts_leaks on 2026-07-14.

## Source Files
- `Anthropic/claude-opus-4.8.md`
- `Anthropic/claude-sonnet-5.md`

## Model Hierarchy (as of 2026-07)

```
Mythos Tier (not publicly available)
├── Claude Mythos 5
└── Claude Fable 5 (extra safety for bio/cyber/LLM-R&D)
    
Opus Tier
├── Claude Opus 4.8 (latest, most advanced public)
├── Claude Opus 4.7
└── Claude Opus 4.6

Sonnet Tier
├── Claude Sonnet 5
└── Claude Sonnet 4.6

Haiku Tier
└── Claude Haiku 4.5
```

**Note**: Mythos 5 and Fable 5 access suspended due to export control directive.

## Key Differences

| Dimension | Opus 4.8 | Sonnet 5 |
|-----------|----------|----------|
| **Search behavior** | "search_first" - MUST search before EVERY factual question about present-day world | Mentioned but not as strongly enforced |
| **Proactivity** | Not explicitly emphasized as a separate section | Dedicated `<proactivity>` section - use tools proactively, don't push work back to user |
| **Ambiguity handling** | Not detailed | Explicit: "pick most reasonable interpretation, state assumption briefly, proceed" |
| **Format rules** | Detailed: avoid bullets, use prose, minimal bold | Fewer format restrictions |
| **Mythos info** | Not mentioned | Detailed explanation of Mythos tier |
| **Drug guidance** | Not explicitly addressed | Can provide life-saving info (overdose recognition) even for illicit substances |

## Opus 4.8 Unique Features

### Strict Search Mandate
> "Claude searches before EVERY factual question about the present-day world."
> "Don't end a response by offering to search for something the user's request already asked for."

### Detailed Format Rules
- Avoid over-formatting (bold, headers, lists, bullets)
- Default to prose, not lists
- Never use bullets when declining (softens the blow)
- Only use lists when (a) asked, or (b) content is multifaceted

### Specific Word Restrictions
- Avoid: "genuinely", "honestly", "actually"
- No pet names unless requested
- No emojis unless user uses them first

## Sonnet 5 Unique Features

### Proactivity Section
> "Claude uses tools to gather what it needs rather than asking the user to supply the information or answering from memory."
> "Claude prefers gathering context and delivering a complete result over deferring work back to the user."

### Ambiguity Resolution
> "When a request is ambiguous or underspecified, Claude picks the most reasonable interpretation, states the assumption briefly, and proceeds with a complete answer."
> "Ambiguity or missing detail is a reason to choose a sensible default and attempt the task, not a reason to decline it."

### Diagnostic Restraint
> "Claude does not name a diagnosis the person has not disclosed — including framing their experience as 'depression' or another mental-health diagnosis to explain what they are feeling."

## Shared Features (Both Models)

### Child Safety
- Never create romantic/sexual content involving minors
- Refuse cautiously after any child-safety refusal
- Don't decode CSAM-related slang

### Weapon Restrictions
- No CBRN or conventional weapons guidance
- Judge cumulative output, not individual turns
- Past assistance ≠ authorization

### Tone
- Warm, kind, not condescending
- Willing to push back constructively
- No cursing unless user does

### Legal/Financial
- Provide factual info for informed decisions
- Not confident recommendations
- Note not a lawyer/financial advisor

## Implications for Hermes Agent

These findings suggest:

1. **Opus models** are more rigid about process (search-first, format rules)
2. **Sonnet models** are more action-oriented (proactive tool use, proceed with assumptions)
3. Both share strong safety boundaries but differ in execution style
4. The proactivity pattern in Sonnet 5 is worth emulating in agent design
