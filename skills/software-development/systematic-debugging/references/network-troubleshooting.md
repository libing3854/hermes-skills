# Network Troubleshooting: ISP Outage vs Proxy Failure

## Problem

All remote services (Telegram, WeChat, QQ Bot, web apps) disconnect simultaneously. Need to distinguish:
- **ISP/宽带闪断** — the local internet connection dropped
- **Proxy/VPN failure** — the proxy node went down but local internet is fine
- **Target service outage** — only one specific service is down

## Diagnostic Technique: Multi-Target Timeout Analysis

### Step 1: Check ClashX Logs

ClashX logs all TCP connections with routing rules and errors. On macOS:

```bash
# Find the most recent ClashX log
ls -lt ~/Library/Logs/ClashX/ | head -5

# Look for timeout/failure patterns around the incident time
grep "i/o timeout\|connect error" ~/Library/Logs/ClashX/com.west2online.ClashX*.log | grep "04:18"
```

### Step 2: Classify the Failure

Examine which connection types failed:

| Pattern | Diagnosis | Root Cause |
|---------|-----------|------------|
| **Domestic direct sites** (fanqienovel.com, qq.com, weixin.qq.com) AND **proxy nodes** all i/o timeout simultaneously | **ISP/宽带闪断** | Modem, router, or ISP-level outage |
| Only **proxy nodes** timeout; domestic direct sites work | **Proxy/VPN failure** | Node expired, banned, or overloaded |
| Only one **specific service** fails | **Service outage** | Target server or API issue |

### Step 3: Extract Evidence from ClashX Logs

```bash
# Find ALL failures at the incident minute — look for pattern diversity
grep "i/o timeout\|connect error\|error:" ~/Library/Logs/ClashX/*.log | grep "04:18"

# Each line shows: time → routing rule → target → error
# Example: dial DIRECT (match GeoIP/CN) → fanqienovel.com:443 → i/o timeout
# Example: dial ✈️Telegram (match DomainSuffix/telegram.org) → api.telegram.org:443 → connect error
```

### Step 4: Corroborate with macOS Network Logs

```bash
# Check for WiFi/network state changes at the same time
log show --predicate 'subsystem == "com.apple.network"' \
  --start '2026-05-25 04:17:00' --end '2026-05-25 04:20:00' --style compact | \
  grep -E "satisfied|unsatisfied|interface|sleep|wake"
```

- `path:satisfied` = network available
- `path:unsatisfied` = network down
- `interface: en0` = Ethernet or WiFi interface present

### Example from Real Incident

```
04:18:13  fanqienovel.com (DIRECT/国内)     → i/o timeout     ← FIRST failure
04:18:25  api.telegram.org (代理)           → connect error    ← proxy node also down
04:18:32  ilinkai.weixin.qq.com (DIRECT)    → i/o timeout      ← domestic also down
04:18:41  api.sgroup.qq.com (DIRECT)        → i/o timeout      ← QQ Bot domestic API down
04:18:58  network path satisfied            → ✓ RECOVERED
```

**Conclusion:** All domestic AND proxy targets failed simultaneously → ISP flash outage (~45s).

## Recovery by Service

| Service | Auto-Recovery Behavior |
|---------|----------------------|
| Telegram | Auto-reconnects (up to 10 attempts @ exponential backoff) |
| WeChat (iLink Bot) | Auto-reconnects (3 retries) |
| QQ Bot | **Does NOT auto-recover** after a failed reconnect attempt. Requires `hermes gateway restart` (or `launchctl stop/start ai.hermes.gateway`) |
| Hermes cron jobs | `live adapter delivery` falls back to `standalone` delivery |
