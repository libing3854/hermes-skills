# Z-Library Daily Limit Check

Always navigate to `https://zh.z-library.sk/login` before starting any download session. The login page is the **authoritative source** for daily limit status.

## Key Snapshot Fields (Chinese UI)

```
heading "欢迎光临,  <username> !"
StaticText "<email>"
StaticText "高级帐户"              ← account tier
StaticText "直到 <date>"           ← premium expiry
StaticText "每日限额"
StaticText "X/Y"                   ← ← THIS IS THE KEY FIELD
```

## Interpretation

| Display | Meaning | Action |
|---------|---------|--------|
| `每日限额 5/10` | 5 of 10 used, 5 remaining | Proceed with up to 5 downloads |
| `每日限额 10/10` | ALL USED | **STOP — hard block** |
| `每日限额 0/10` | None used | Proceed with up to 10 downloads |

## Real Example (exhausted)

```
uid=N StaticText "欢迎光临,  奇谭书 !"
uid=N StaticText "[REDACTED]"
uid=N StaticText "高级帐户"
uid=N StaticText "直到 14 Jul, 2026"
uid=N StaticText "每日限额"
uid=N StaticText "10/10"            ← EXHAUSTED
uid=N StaticText "下载"
uid=N StaticText "14"
```

Note: "高级帐户" (Premium) does NOT guarantee unlimited downloads. The actual limit is shown in `每日限额 X/Y`. Premium tiers can still have a 10/day cap.

## Recovery Options When Exhausted

1. **Wait** — limit resets at midnight UTC (next day)
2. **Donate more** — higher donation tiers increase daily cap (up to 999/day)
3. **Desktop app** — Z-Library desktop app may offer bonus downloads or separate limits
4. **Schedule retry** — ask user if they want to retry tomorrow
