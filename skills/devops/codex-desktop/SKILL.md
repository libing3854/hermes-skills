---
name: codex-desktop
description: "Codex Desktop (macOS/Windows) 故障排除与配置指南。覆盖：config.toml 配置、cloud config bundle 超时、GPU 崩溃、代理配置、重装流程。触发条件：Codex 桌面版报错、打不开、卡住、403错误。"
version: 1.0.0
author: Lily
license: MIT
platforms: [macos, windows]
metadata:
  hermes:
    tags: [Codex, OpenAI, Desktop, Troubleshooting, Proxy, Config]
    related_skills: [codex]
---

# Codex Desktop 故障排除

OpenAI Codex 的桌面版应用（非 CLI）。独立产品，与 `codex` CLI 技能覆盖的场景不同。

## 配置文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| config.toml | `~/.codex/config.toml` | 主配置（模型、插件、MCP、代理组） |
| auth.json | `~/.codex/auth.json` | 登录凭据 |
| 缓存目录 | `~/Library/Application Support/Codex/` | Chromium 数据、GPU 缓存、crash 报告 |

⚠️ **不要与 Hermes 的 `~/.hermes/profiles/*/config.yaml` 混淆** — 完全不同的产品。

## 常见故障

### 1. Cloud Config Bundle 超时（`timed out waiting for cloud config bundle after 15s`）

**症状：** 打开对话串报红色横幅错误，无法发消息。

**根因：** Codex Desktop 启动时从 `chatgpt.com/backend-api` 加载企业配置（cloud config bundle），15 秒超时。在中国大陆因网络问题常见。

**源码分析（codex-rs/cloud-config/src/service.rs）：**
- 超时硬编码 `CLOUD_CONFIG_BUNDLE_TIMEOUT = 15s`
- 只对 Business/Enterprise/Edu 计划用户生效（`cloud_config_eligible_auth` 函数）
- 5 次重试，指数退避

**解决方案：**
1. 确保代理能访问 `chatgpt.com` 和 `api.openai.com`
2. 测试连通性：`curl -s -o /dev/null -w "%{http_code}" https://chatgpt.com --connect-timeout 10`
3. 返回 200/401 = 正常；返回 000 = 连不上；返回 403 = 被拦截

### 2. 403 Forbidden（Cloudflare 拦截）

**症状：** 发消息返回 `unexpected status 403 Forbidden`，HTML 错误页含 Cloudflare Ray ID。

**根因：** 代理节点 IP 被 Cloudflare 封禁。常见于香港/新加坡共享节点。

**解决方案：**
- 在 ClashX/代理软件中切换节点（推荐美国节点）
- 检查 Ray ID 尾缀（HKG=香港，NRT=日本，SFO=美国）
- 测试：`curl -s -o /dev/null -w "%{http_code}" https://chatgpt.com/backend-api`

### 3. GPU 崩溃（CrBrowserMain EXC_BREAKPOINT）

**症状：** 应用闪退或卡死，Console 日志含 `CrBrowserMain` 或 `EXC_BREAKPOINT`。

**根因：** Chromium GPU 渲染引擎 bug（GitHub issue #27880），macOS 版本 26.608-26.623 均受影响。

**解决方案：** 创建禁用 GPU 的启动包装器：
```bash
mkdir -p ~/Applications/Codex\ Safe.app/Contents/MacOS
cat > ~/Applications/Codex\ Safe.app/Contents/MacOS/run << 'SCRIPT'
#!/bin/bash
exec /Applications/Codex.app/Contents/MacOS/Codex \
  --disable-gpu --disable-software-rasterizer \
  --disable-gpu-compositing --disable-gpu-sandbox "$@"
SCRIPT
chmod +x ~/Applications/Codex\ Safe.app/Contents/MacOS/run
```

### 4. 重装 Codex Desktop

```bash
# 1. 杀进程
pkill -9 -f "Codex.app"

# 2. 删除旧版
rm -rf /Applications/Codex.app

# 3. 下载最新版（Apple Silicon）
curl -L --connect-timeout 30 --max-time 300 -o /tmp/Codex.dmg \
  "https://persistent.oaistatic.com/codex-app-prod/Codex.dmg"

# 4. 挂载安装
hdiutil attach /tmp/Codex.dmg -nobrowse
cp -R "/Volumes/Codex Installer/Codex.app" /Applications/
hdiutil detach "/Volumes/Codex Installer"
rm -f /tmp/Codex.dmg

# 5. 重新打开
open -a Codex
```

Intel Mac 用 `Codex-latest-x64.dmg`。

### 5. config.toml 中的 API Key 导致加载失败

**症状：** `timed out waiting for cloud config bundle`，但实际是 config.toml 中的第三方 API 端点不可达。

**排查：** 检查 `[shell_environment_policy.set]` 中的 `ANTHROPIC_BASE_URL` 等配置是否可达。

**临时修复：** 注释掉 `[shell_environment_policy.set]` 块，重启 Codex。

## Clash 代理配置要点

Codex Desktop 使用系统代理（HTTP/HTTPS/SOCKS），但需确保：

1. **正确的配置文件被加载** — `~/.config/clash/` 下可能有多个 yaml，ClashX 默认用 `config.yaml`
2. **规则不是全 DIRECT** — 检查 `MATCH` 规则是否走代理：
   ```bash
   grep "MATCH" ~/.config/clash/config.yaml
   # ❌ MATCH,DIRECT = 所有流量直连
   # ✅ MATCH,🔰节点选择 = 所有流量走代理
   ```
3. **OpenAI 域名可达** — 测试：
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://api.openai.com --connect-timeout 10
   curl -s -o /dev/null -w "%{http_code}" https://chatgpt.com --connect-timeout 10
   ```

## 日志位置

| 类型 | 路径 |
|------|------|
| Crash 报告 | `~/Library/Logs/DiagnosticReports/Codex*` |
| Crashpad | `~/Library/Application Support/Codex/Crashpad/` |
| 系统日志 | `log show --predicate 'process == "Codex"' --last 10m` |
