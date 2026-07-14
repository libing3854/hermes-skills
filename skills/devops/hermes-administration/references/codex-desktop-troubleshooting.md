# Codex Desktop App 故障排除

## 常见问题

### 1. 消息发送失败 / 界面卡死
**症状：** 弹出"无法发送消息"错误，界面卡在加载状态
**原因：** 网络请求超时或API连接问题
**解决：**
```bash
# 杀掉所有Codex进程
pkill -9 -f "Codex.app"
sleep 2
# 重新打开
open -a Codex
```

### 2. GPU渲染崩溃（CrBrowserMain EXC_BREAKPOINT）
**症状：** Codex反复崩溃，日志显示`CrBrowserMain EXC_BREAKPOINT`或`Renderer SIGABRT`
**原因：** Chromium GPU渲染引擎bug，macOS版本已知问题（GitHub issue #27880）
**特征报错：** 冰哥描述的"c什么.h什么的"即 CrBrowserMain
**解决：创建禁用GPU的安全启动器**
```bash
# 创建 Codex Safe 应用
mkdir -p ~/Applications/Codex\ Safe.app/Contents/MacOS
cat > ~/Applications/Codex\ Safe.app/Contents/MacOS/run << 'EOF'
#!/bin/bash
exec /Applications/Codex.app/Contents/MacOS/Codex \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-gpu-compositing \
  --disable-gpu-sandbox \
  "$@"
EOF
chmod +x ~/Applications/Codex\ Safe.app/Contents/MacOS/run

# 创建Info.plist
cat > ~/Applications/Codex\ Safe.app/Contents/Info.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>run</string>
    <key>CFBundleName</key>
    <string>Codex Safe</string>
    <key>CFBundleIdentifier</key>
    <string>com.openai.codex.safe</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
PLIST
```
**使用：** 用 `~/Applications/Codex Safe.app` 启动代替原版

### 3. 完全无法启动
**症状：** `open -a Codex` 后进程不出现或立即退出
**解决：完全卸载重装**
```bash
# 1. 杀掉所有进程
pkill -9 -f "Codex.app"

# 2. 删除旧版
rm -rf /Applications/Codex.app

# 3. 下载最新版（Apple Silicon）
cd /tmp && curl -L --connect-timeout 30 --max-time 300 -o Codex.dmg \
  "https://persistent.oaistatic.com/codex-app-prod/Codex.dmg"

# 4. 挂载安装
hdiutil attach /tmp/Codex.dmg -nobrowse
cp -R "/Volumes/Codex Installer/Codex.app" /Applications/
hdiutil detach "/Volumes/Codex Installer"
rm -f /tmp/Codex.dmg

# 5. 重新打开
open -a Codex
```
**注意：** Intel Mac 用 `https://persistent.oaistatic.com/codex-app-prod/Codex-latest-x64.dmg`

### 4. Cloud Config Bundle 加载超时（国内网络特有）
**症状：** 红色横幅报错 `无法加载 config.toml：timed out waiting for cloud config bundle after 15s`，所有对话串无法继续。
**原因：** Codex Desktop 启动时从 OpenAI 后端加载企业配置 bundle（Business/Enterprise/Edu 计划），国内无法访问 `api.openai.com`，15 秒超时后报错。CLI 不受影响（不走 cloud config）。
**关键源码：** `codex-rs/cloud-config/src/service.rs:33` — `CLOUD_CONFIG_BUNDLE_TIMEOUT = 15s` 硬编码，无法配置。
**GitHub issue：** [#26504](https://github.com/openai/codex/issues/26504) — Desktop 特有 bug，OpenAI 尚未修复。

**诊断步骤：**
```bash
# 1. 测试直连 OpenAI（国内应超时）
curl -s -o /dev/null -w "HTTP: %{http_code}, Time: %{time_total}s\n" https://api.openai.com/v1/models --max-time 5

# 2. 测试通过代理
curl -s -o /dev/null -w "HTTP: %{http_code}, Time: %{time_total}s\n" --proxy http://127.0.0.1:7890 https://api.openai.com/v1/models --max-time 5

# 3. 如果代理也超时，检查 Clash 配置文件
ls -lt ~/.config/clash/*.yaml
# 常见问题：ClashX 使用了空的 config.yaml 而非完整的 Clash_*.yaml
```

**解决方案（按优先级）：**
1. **切换 Clash 配置** — 确保 ClashX 使用有 OpenAI 代理规则的配置文件（如 `Clash_1774761854.yaml`），不是空的 `config.yaml`
2. **给 Codex 单独配代理** — 在 `~/.codex/config.toml` 添加：
   ```toml
   [shell_environment_policy.set]
   HTTP_PROXY = "http://127.0.0.1:7890"
   HTTPS_PROXY = "http://127.0.0.1:7890"
   ```
3. **等待 OpenAI 修复** — issue #26504 已报告，Desktop 端应增加超时或优雅降级

**配置文件位置：** `~/.codex/config.toml`（用户级配置），备份为 `config.toml.bak`

**Pitfall：** 不要直接修改 `shell_environment_policy.set` 里的 ANTHROPIC_* 配置，那会导致 FreeModel API 也超时。如果要移除 FreeModel 配置，先备份。

### 5. 403 Forbidden — 代理节点被 Cloudflare 拦截
**症状：** Codex 红色横幅报错 `unexpected status 403 Forbidden`，错误中包含 HTML/CSS 和 Cloudflare Ray ID（如 `cf-ray: xxx-HKG`）。
**原因：** 代理节点（通常是香港）被 Cloudflare 识别并拦截。OpenAI 对数据中心/代理 IP 段会返回 403。
**诊断：**
```bash
# 测试 chatgpt.com 是否被拦截
curl -s -o /dev/null -w "HTTP: %{http_code}\n" https://chatgpt.com --max-time 10
# 403 = 被拦截，200 = 正常
```
**解决：** 在 ClashX 中切换代理节点（美国/新加坡优先，避免香港），然后重启 Codex。
**关键：** 这个问题和 cloud config bundle timeout 是不同的错误。timeout 是连不上，403 是连上了但被拦。

### 6. 孤立进程占用资源
**症状：** 系统变慢，发现多个遗留的 `codex app-server` 进程
**解决：**
```bash
# 查看所有Codex相关进程
ps aux | grep -i codex | grep -v grep

# 清理所有残留
pkill -9 -f "Codex"
```

## 诊断命令

```bash
# 查看Codex版本
defaults read /Applications/Codex.app/Contents/Info.plist CFBundleShortVersionString

# 查看系统日志中的Codex错误
log show --predicate 'process == "Codex"' --last 10m --style compact 2>/dev/null | grep -iE "error|crash|fatal|fail"

# 检查crash报告
ls -lt ~/Library/Logs/DiagnosticReports/ | grep -i codex

# 检查内存压力
vm_stat | head -10
sysctl vm.swapusage

# 检查Codex配置文件
cat ~/.codex/config.toml

# 检查Clash代理配置
ls -lt ~/.config/clash/*.yaml
grep "MATCH" ~/.config/clash/config.yaml
```

## 参考链接
- [Codex官方troubleshooting](https://developers.openai.com/codex/app/troubleshooting)
- [GitHub issue #27880 - GPU崩溃](https://github.com/openai/codex/issues/27880)
- [GitHub issue #26504 - Cloud config bundle timeout](https://github.com/openai/codex/issues/26504)
- [下载页面](https://developers.openai.com/codex/app)
- [源码 - cloud-config service.rs](https://fossies.org/linux/codex-rust/codex-rs/cloud-config/src/service.rs)
