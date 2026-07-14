# launchd Plist Profile Hardcode Issue

## 问题描述

当 gateway 通过 profile-specific launchd plist（如 `ai.hermes.gateway-shanli.plist`）运行时，即使 `~/.hermes/active_profile` 已改回 `default`，gateway 仍然读取 shanli profile 的 `.env` 文件，因为 plist 中硬编码了 `--profile shanli` 和 `HERMES_HOME`。

## 触发场景

1. 在 shanli profile 下运行 `hermes gateway install` 或 `hermes gateway start`
2. launchd plist 被创建，硬编码了 `--profile shanli`
3. 后续即使 `active_profile` 改回 `default`，launchd 仍按 plist 运行

## 诊断方法

```bash
# 1. 检查 plist 内容
cat ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist

# 关键字段：
# <key>--profile</key> <string>shanli</string>
# <key>HERMES_HOME</key> <string>/Users/libing/.hermes/profiles/shanli</string>

# 2. 确认进程实际使用的 profile
ps aux | grep "hermes.*gateway" | grep -v grep
# 如果看到 --profile shanli → 硬编码问题
```

## 修复方案

**方案 A（推荐）：复制消息平台 key 到 shanli 的 `.env`**

```bash
# 从主 .env 复制消息平台相关 key
grep -E "^(TELEGRAM_BOT_TOKEN|DISCORD_BOT_TOKEN|QQ_APP_ID|QQ_CLIENT_SECRET|WEIXIN_TOKEN|WEIXIN_ACCOUNT_ID|GATEWAY_ALLOW_ALL_USERS)=" ~/.hermes/.env >> ~/.hermes/profiles/shanli/.env

# 重启 gateway
launchctl stop ai.hermes.gateway-shanli && sleep 2 && launchctl start ai.hermes.gateway-shanli
```

**方案 B：删除 shanli-specific plist，重新安装 default plist**

```bash
# 1. 停止当前 gateway
launchctl bootout gui/501/ai.hermes.gateway-shanli 2>/dev/null
kill $(pgrep -f "hermes.*gateway") 2>/dev/null

# 2. 删除 shanli-specific plist
rm ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist

# 3. 确保 active_profile 是 default
echo 'default' > ~/.hermes/active_profile

# 4. 重新安装
hermes gateway install
hermes gateway start
```

## 注意事项

- 方案 A 更简单，但 shanli profile 的 `.env` 会包含所有消息平台 key
- 方案 B 更干净，但需要确认 default profile 的 gateway 能正常启动
- 无论哪种方案，重启后都要验证所有平台连接状态
