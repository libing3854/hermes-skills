# Codex Desktop macOS 故障排查

## 问题1：`timed out waiting for cloud config bundle after 15s`

**症状：** Codex 打开后报"无法加载 config.toml"，错误信息包含 `timed out waiting for cloud config bundle after 15s`。

**根因：** Codex 启动时会从 OpenAI 后端加载 cloud config bundle（企业配置），超时 15 秒。在中国大陆，`api.openai.com` 被墙，连接超时。

**源码分析（codex-rs/cloud-config/src/service.rs）：**
- 超时时间硬编码：`CLOUD_CONFIG_BUNDLE_TIMEOUT = 15s`
- 仅对 Business/Enterprise/Edu 计划用户生效（`cloud_config_eligible_auth` 函数）
- 个人 Plus 用户不应触发此逻辑，但 Codex Desktop 可能仍有此流程

**解决方案：**
1. 确保代理可用：`curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models` 应返回 401（连通）或非 000
2. 如果代理正常但仍超时，检查 Codex 是否使用系统代理
3. 临时方案：删除 `~/.codex/config.toml` 中的 `[shell_environment_policy.set]` 段（如果有自定义 API 配置）

**相关 issue：** https://github.com/openai/codex/issues/26504

## 问题2：`403 Forbidden` on chatgpt.com

**症状：** Codex 发消息时报 `unexpected status 403 Forbidden`，错误中包含 `chatgpt.com/backend-api/codex/responses` 和 Cloudflare Ray ID。

**根因：** 代理节点（通常是香港/新加坡）的 IP 被 Cloudflare 封禁。OpenAI 对某些代理 IP 返回 403。

**诊断：**
```bash
curl -s -o /dev/null -w "%{http_code}" https://chatgpt.com
# 403 = 被拦截，需要换节点
# 200 = 正常
```

**解决方案：**
1. 在 ClashX/代理软件中切换节点（推荐美国节点，避免香港）
2. 重启 Codex

## 问题3：NSXPCDecoder 警告

**症状：** 系统日志中大量 `NSXPCDecoder validateAllowedClass` 警告。

**影响：** 无。这是 macOS 系统级警告，不影响 Codex 功能。可以忽略。

## 问题4：CrBrowserMain EXC_BREAKPOINT 崩溃

**症状：** Codex 反复崩溃，crash 日志显示 `CrBrowserMain EXC_BREAKPOINT`。

**根因：** Codex Desktop 的 Chromium 渲染引擎 bug，与 GPU/Shader 相关。

**解决方案：**
```bash
# 创建禁用 GPU 的启动脚本
/Applications/Codex.app/Contents/MacOS/Codex \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-gpu-compositing \
  --disable-gpu-sandbox
```

**相关 issue：** https://github.com/openai/codex/issues/27880

## 通用排查步骤

```bash
# 1. 检查 Codex 进程
ps aux | grep -i codex | grep -v grep

# 2. 杀掉卡死的进程
pkill -9 -f "Codex.app"

# 3. 检查网络连通性
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models --connect-timeout 10
curl -s -o /dev/null -w "%{http_code}" https://chatgpt.com --connect-timeout 10

# 4. 重启 Codex
open -a Codex
```
