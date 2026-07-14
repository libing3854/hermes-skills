---
name: hermes-administration
description: Hermes infrastructure management — web services, updates, profiles, configuration, and troubleshooting. Trigger when user asks to start/stop web services, update Hermes, manage profiles, or troubleshoot infrastructure issues.
---

# Hermes Administration

## Overview

Covers the class of tasks related to managing Hermes Agent infrastructure: web services, updates, profiles, configuration, and common pitfalls.

## Web Services

### Ports (CRITICAL — memorize these)
| Service | Port | Purpose |
|---------|------|---------|
| **Hermes Dashboard** | 9119 | Management interface, profile switching, cron jobs |
| **Hermes Workspace** | 3000 | Development environment (vite dev) |

**Pitfall**: Do NOT start Dashboard on port 8080. User's "web" = Dashboard (9119) + Workspace (3000).

### Starting Services

**Dashboard:**
```bash
hermes dashboard --port 9119 --no-open
```

**Workspace:**
```bash
cd /Users/libing/hermes-workspace && NODE_OPTIONS="--max-old-space-size=2048" node_modules/.bin/vite dev --host 127.0.0.1 --port 3000
```
**Pitfall**: 
- `vite` 和 `npx vite` 都可能找不到，必须用 `node_modules/.bin/vite` 的完整路径
- 需要设置 `NODE_OPTIONS="--max-old-space-size=2048"` 防止内存不足
- 冰哥可能会用"工作空间插件"、"web插件"、"web工具"来指代 hermes-workspace，都是同一个东西

### Checking Status
```bash
lsof -i :9119  # Dashboard
lsof -i :3000  # Workspace
```

### Stopping Services
```bash
# Find PID
lsof -i :9119 -t
# Kill
kill <PID>
```

## Updates

### Standard Update Process
```bash
hermes update
hermes gateway restart
hermes doctor  # Verify
hermes --version  # Confirm version
```

### Post-Update Verification
- Check `hermes doctor` for issues
- Verify config version updated
- Test gateway connectivity

## Profiles

### Profile Locations
- **Default**: `~/.hermes/SOUL.md`
- **Other profiles**: `~/.hermes/profiles/<name>/SOUL.md`

### Checking for Redundancy
When asked to check profiles:
1. Read each profile's SOUL.md
2. Compare with existing skills (avoid duplication)
3. Check for default persona consistency
4. Report findings with specific overlap locations

### Active Profiles (current setup)
| Profile | Model | Purpose |
|---------|-------|---------|
| lili | DeepSeek V4 Flash | Review/audit |
| shanli | LongCat 2.0 | Writing |
| shanliG | Gemini 3.5 Flash | Writing backup |
| dalim | mimo-v2.5-pro | Deep review |
| dalid | deepseek-v4-pro | Deep review |
| **delegation (default)** | **agnes-2.0-flash** | **子代理默认模型** |

### Gateway Restart Cascade（重要！）
**问题**：`hermes gateway restart` 会杀死所有子进程，包括 Dashboard 和 Workspace。
**症状**：重启后 Dashboard (9119) 和 Workspace (3000) 都不可用。
**解决**：重启后手动恢复：
```bash
# Dashboard
hermes dashboard --port 9119 --no-open &
# Workspace
cd /Users/libing/hermes-workspace && npx vite dev --host 127.0.0.1 --port 3000 &
```
**最佳实践**：如果只是修改 delegation 配置，用 `hermes config set` 后重启即可。但如果修改了非 delegation 配置，需要评估是否需要重启。

### Delegation Cost Control（重要！）

### delegation 配置直接影响子代理模型选择
`delegation` 配置中的 `provider`、`model`、`key_env` 三个字段决定了所有 `delegate_task` 调用使用的模型。

**配置示例（免费模型）：**
```yaml
delegation:
  provider: xiaomi
  model: mimo-v2.5-pro
  key_env: XIAOMI_API_KEY
```

**配置示例（付费模型 — 谨慎使用）：**
```yaml
delegation:
  provider: deepseek
  model: deepseek-v4-pro
  key_env: DEEPSEEK_API_KEY
```

### ⚠️ 血泪教训：key_env 配错导致 ¥112 账单（2026-07-01）
**事故**：`delegation.key_env` 设置为 `DEEPSEEK_API_KEY`，导致所有子代理默认使用 deepseek-v4-pro。在一次批量下载任务中，派出了 10+ 个子代理，每个子代理 50 次 API 调用，总计 **671 次 deepseek-v4-pro 调用，消耗 5575 万 tokens，费用约 ¥112**。

**根因**：子代理继承 delegation 配置中的 provider/model。简单任务（浏览器操作、文件下载）不需要昂贵模型。

**修复**：
```bash
hermes config set delegation.provider agnes-2.0-flash
hermes config set delegation.model agnes-2.0-flash
hermes config set delegation.key_env AGNES_API_KEY
hermes gateway restart
```

**最佳实践**：
- delegation 默认配置应使用免费/低价模型（agnes-2.0-flash 或 xiaomi/mimo-v2.5）
- 需要深度推理时，用 `delegate_dalim`（MiMo）或 `delegate_dalid`（DeepSeek）临时切换
- 简单任务（下载、文件操作、浏览器自动化）用免费模型即可
- 复杂任务（代码审查、深度分析）才用付费模型

**当前推荐配置（2026-07-01 更新）**：
```yaml
delegation:
  provider: agnes-2.0-flash
  model: agnes-2.0-flash
  key_env: AGNES_API_KEY
```

### 检查当前 delegation 配置
```bash
cat ~/.hermes/config.yaml | grep -A 20 "^delegation:"
# 或用 python 读取
python3 -c "import yaml; c=yaml.safe_load(open('/Users/libing/.hermes/config.yaml')); print(yaml.dump(c.get('delegation', {})))"
```

## Common Pitfalls

### Profile Naming Rules（重要！2026-07-03 发现）
**规则**：Profile名必须匹配 `[a-z0-9][a-z0-9_-]{0,63}`
- ✅ 有效：`mimo-v2-5`, `shanli`, `dalid`, `mimo_v2_5`
- ❌ 无效：`mimov2.5`（含点号）, `MiMo`（大写）, `-mimo`（以连字符开头）

**创建profile的正确方式**：
```bash
# ✅ 正确：用 hermes profile create
hermes profile create mimo-v2-5 --clone --description "MiMo v2.5"

# ❌ 错误：手动 mkdir ~/.hermes/profiles/mimov2.5
# 手动创建目录不会注册profile，hermes无法识别
```

### active_profile 文件损坏导致所有CLI命令失败（严重！2026-07-03 发现）
**症状**：所有 `hermes` 命令都报 `Error: Invalid profile name 'xxx'. Must match [a-z0-9][a-z0-9_-]{0,63}`。
**根因**：`~/.hermes/active_profile` 文件中存储了无效的profile名（如含点号的`mimov2.5`）。
**诊断**：
```bash
cat ~/.hermes/active_profile  # 检查是否是有效profile名
hermes profile list           # 如果报错就是active_profile有问题
```
**修复**：
```bash
echo "default" > ~/.hermes/active_profile
# 或指定有效profile
echo "mimo-v2-5" > ~/.hermes/active_profile
```
**关键**：这个文件存储的是当前活动profile名，一旦损坏，整个hermes CLI就瘫痪。修复只需一行echo。

### delegate_task 使用独立API配置（重要！）
**常见误解**：以为 `delegate_task` 会使用当前session的模型。
**事实**：`delegate_task` 使用 `~/.hermes/config.yaml` 中 `delegation` 配置的 `provider`/`model`/`key_env`，与当前session无关。
```yaml
# delegation配置决定了所有子代理的模型
delegation:
  provider: agnes-2.0-flash  # ← 子代理用这个provider
  model: agnes-2.0-flash     # ← 子代理用这个model
  key_env: AGNES_API_KEY     # ← 子代理用这个key
```
**要让子代理用特定模型**：
1. 用 `delegate_dalim`/`delegate_dalid` 临时切换（切换后立即调用delegate_task）
2. 或创建专用profile，用 `hermes -p <profile> chat -q "任务"` 直接执行（推荐，更可控）

### Wrong Port
**Symptom**: User says "web启动" but Dashboard doesn't appear.
**Cause**: Started on port 8080 instead of 9119.
**Fix**: Always use `--port 9119` for Dashboard.

### Python 3.9兼容性问题（2026-06-26）
**症状：** `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`
**原因：** macOS默认Python 3.9不支持`X | None`类型语法（需3.10+）
**影响包：** Crawl4AI、Mem0、sentence-transformers等新包
**解决：** 用`python3.12`代替`python3`，或`pip3.12 install`代替`pip3 install`
```bash
python3.12 -m pip install --break-system-packages <package>
```

### Gateway Restart Required
**Symptom**: SOUL.md changes not taking effect.
**Fix**: Run `hermes gateway restart` after any SOUL.md or config changes.

### redact_secrets 拦截 API Key 写入（v0.17.0 新增）
**Symptom**: 写入API Key（如Firecrawl的`fc-`前缀key）到.env时被系统截断，echo/heredoc/Python全部只能写13字符。
**Cause**: `security.redact_secrets: true`（v0.17.0默认开启）自动识别并屏蔽所有疑似API key的输出。
**Fix**:
```bash
# 1. 临时关闭
hermes config set security.redact_secrets false
# 2. 写入key
echo "KEY_NAME=***">> ~/.hermes/.env
# 3. 恢复
hermes config set security.redact_secrets true
# 4. 重启gateway（配置变更需重启）
hermes gateway restart
```
**关键**: 即使`redact_secrets: false`也要重启gateway才能生效。直接用shell echo可行，不要用Python heredoc。

### Profile Gateway Conflict
**Symptom**: Gateway crashes with lock errors.
**Cause**: active_profile contains "shanli" causing default gateway override.
**Fix**: Ensure plist uses `--profile default`.

### Codex Desktop Issues
For Codex Desktop app troubleshooting (config.toml, GPU crashes, proxy, 403 errors), see `codex-desktop` skill.
Key paths: `~/.codex/config.toml`, `~/Library/Application Support/Codex/`.

### Codex App 卡死（无法发送消息）
**Symptom**: Codex 桌面端弹出「无法发送消息」错误，弹窗卡在「正在加载...」，界面无响应。
**Cause**: API 请求超时或网络连接异常导致 UI 线程阻塞。
**Fix**:
```bash
# 1. 强杀所有 Codex 进程
pkill -9 -f "Codex.app"
# 2. 确认已杀干净（应返回 0）
ps aux | grep -i codex | grep -v grep | wc -l
# 3. 重新打开
open -a Codex
```

### Codex App GPU 渲染崩溃
**Symptom**: Codex反复崩溃，日志显示`CrBrowserMain EXC_BREAKPOINT`或`Renderer SIGABRT`。用户可能描述为"c什么.h什么的"报错。
**Cause**: Chromium GPU渲染引擎bug，macOS已知问题（GitHub issue #27880）。
**Fix**: 创建禁用GPU的安全启动器 `~/Applications/Codex Safe.app`，详见 `references/codex-desktop-troubleshooting.md`。

### kanban.profiles 配置（重要！2026-07-03 发现）

**问题**：创建新profile后，kanban任务不会dispatch给它，因为 `kanban.profiles` 配置没有包含新assignee。

**症状**：`hermes kanban create --assignee mimo-v25` 创建成功，但任务永远是 `ready` 状态不被dispatch。

**诊断**：
```bash
grep "profiles:" ~/.hermes/config.yaml
# 检查输出中是否包含你的新assignee
```

**修复**：
```bash
# 用python修改（避免sed引号转义问题）
python3 -c "
import yaml
with open('/Users/libing/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
profiles = cfg.get('kanban', {}).get('profiles', '[]')
if isinstance(profiles, str):
    profiles = yaml.safe_load(profiles)
if 'mimo-v25' not in profiles:
    profiles.append('mimo-v25')
    cfg['kanban']['profiles'] = profiles
    with open('/Users/libing/.hermes/config.yaml', 'w') as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print('Added mimo-v25 to kanban.profiles')
"

# 重启gateway使配置生效
hermes gateway restart
```

**验证**：`hermes kanban list` 中任务状态从 `ready` 变为 `running` 表示配置正确。

## Codex Desktop 故障排查

See `references/codex-desktop-troubleshooting.md` for Codex Desktop issues including:
- config.toml cloud config bundle timeout (GitHub #26504)
- 403 Forbidden errors (proxy/Cloudflare blocking)
- GPU rendering crashes
- Reinstallation steps

## MCP Server配置

See `references/mcp-server-setup-patterns.md` for MCP server installation and configuration across Hermes/Claude Code/MiMo Code.

## 外部工具故障排除

### Codex App 配置加载超时（cloud config bundle timeout）
**Symptom**: Codex 红色横幅报错：`无法加载 config.toml：timed out waiting for cloud config bundle after 15s`。所有对话串无法继续。
**Cause**: Codex 启动时从 OpenAI 后端加载企业配置 bundle，国内网络无法访问 `api.openai.com` 导致 15 秒超时。源码中硬编码 `CLOUD_CONFIG_BUNDLE_TIMEOUT = 15s`（codex-rs/cloud-config/src/service.rs:33）。
**Diagnosis**:
```bash
# 1. 测试直连（应超时）
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models --max-time 5
# 2. 测试代理
curl -s -o /dev/null -w "%{http_code}" --proxy http://127.0.0.1:7890 https://api.openai.com/v1/models --max-time 5
```
**Fix**: 确保系统代理正确配置且 Clash 使用了有 OpenAI 规则的配置文件（不是空的 config.yaml）。详见 `references/codex-desktop-troubleshooting.md`。

See `references/codex-desktop-troubleshooting.md` for full Codex Desktop troubleshooting guide.

### 已配置的MCP Servers
- Chrome DevTools MCP — 网页控制
- SQLite MCP — 数据库操作
- Prompt Optimizer MCP — 提示词优化
- Mem0 MCP — 统一记忆层（本地自托管）
- Tavily MCP — 搜索增强

## Codex Desktop 故障排查

### config.toml 加载超时

**症状：** `timed out waiting for cloud config bundle after 15s`

**原因：** Codex Desktop 启动时从 OpenAI 后端加载 cloud config bundle，国内网络连不上 `api.openai.com`。

**诊断：**
```bash
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models --connect-timeout 5
# 000 = 连不上，需要代理
```

**解决：** 确保代理（ClashX 等）已启动且规则包含 OpenAI 域名。

### Cloudflare 403 Forbidden

**症状：** `unexpected status 403 Forbidden`，cf-ray 结尾为 HKG/JPN 等亚洲节点。

**原因：** 代理节点（香港/日本）被 Cloudflare 拦截。OpenAI 对某些代理 IP 返回 403。

**解决：** 在 ClashX 中切换到美国或新加坡节点，重启 Codex。

### config.toml 位置

- macOS: `~/.codex/config.toml`
- 备份: `~/.codex/config.toml.bak`（Codex 更新时自动备份）

### GitHub Issues 参考

- #26504: cloud config bundle timeout（Desktop 端特有，CLI 不受影响）
- #27880: macOS 26.609 反复崩溃（CrBrowserMain EXC_BREAKPOINT）

## Codex Desktop 故障排查

macOS 上 Codex Desktop 常见问题（config bundle 超时、403 Forbidden、GPU 崩溃等）的诊断和修复方案，详见 `references/codex-troubleshooting.md`。

## 插件管理（Plugin Management）

### 查看插件状态
```bash
# 查看所有插件（包括 bundled）
hermes plugins list

# 只看用户安装的插件
hermes plugins list --plain --no-bundled

# 查看特定插件详情
hermes plugins list --plain | grep -i <关键词>
```

### 启用/禁用插件
```bash
# 启用插件
hermes plugins enable <plugin-name>

# 禁用插件
hermes plugins disable <plugin-name>

# 生效：下次会话自动加载
```

### 插件分类
- **bundled**: Hermes 自带插件（whatsapp-platform, spotify, fal 等）
- **user**: 用户安装的插件（delegate-duo, evey-*, agnes, model-selector 等）

### 冰哥的术语映射（重要！）
冰哥经常用简称或口语化表达，需要映射到正确的Hermes概念：

| 冰哥说的 | 实际指的是 | 类型 | 操作 |
|---------|-----------|------|------|
| wab插件 | whatsapp-platform（bundled插件） | 插件 | `hermes plugins enable whatsapp-platform` |
| 工作空间插件、web插件、web工具、web后台 | hermes-workspace（端口3000）+ Dashboard（端口9119） | 服务 | 检查端口，掉了一键重启 |
| web | Dashboard (9119) + Workspace (3000) | 服务 | 同上 |

**重要**：当冰哥提到某个"插件"但在 `hermes plugins list` 中找不到时：
1. 先用 `grep -i` 在插件列表中搜索关键词（如 "wab" → "whatsapp"）
2. 如果还没有，搜索 session_search 看历史对话中是否提过
3. 仍然没有 → 可能不是插件，而是项目/服务/技能

### 当前已启用插件
```bash
hermes plugins list --plain | grep enabled
```

## 工作空间 / 项目管理（Project Management）

### ⚠️ 工作空间不是插件！
Hermes 的"工作空间"是 **项目 (Project)** 系统，通过 `hermes project` 命令管理。

### 常用命令
```bash
# 查看当前项目
hermes project list

# 创建新项目
hermes project create <名称>

# 添加文件夹到项目
hermes project add-folder <项目> <路径>

# 切换当前项目
hermes project use <项目>

# 查看项目详情
hermes project show <项目>

# 绑定看板
hermes project bind-board <项目> <看板名>
```

### 项目存储位置
- 数据库：`~/.hermes/projects.db`
- 每个 profile 有独立的项目状态

## 网站访问故障排除（Web Access Troubleshooting）

当用户要求访问某个网站但浏览器工具失败时，按以下步骤诊断：

### 诊断流程
```bash
# 1. 检查域名解析
nslookup <domain>

# 2. 检查网络连通性
ping -c 3 <domain>

# 3. 检查HTTP代理配置（重要！代理未运行会导致curl挂死）
echo $https_proxy $http_proxy
# 如果设置了代理但代理没运行，curl会一直hang住
# 解决：临时取消代理 unset https_proxy http_proxy，或确保代理在运行

# 4. 检查HTTP/HTTPS连接
curl -s -o /dev/null -w '%{http_code}' https://<domain> --connect-timeout 10
curl -s -o /dev/null -w '%{http_code}' http://<domain> --connect-timeout 10

# 5. 详细连接信息（查看错误原因）
curl -v --connect-timeout 10 https://<domain> 2>&1 | head -30

# 6. 检查常见页面
curl -s --connect-timeout 10 "https://<domain>/robots.txt"
curl -s --connect-timeout 10 "https://<domain>/sitemap.xml"
```

### 常见问题及解决
| 症状 | 原因 | 解决方案 |
|------|------|----------|
| ping通但HTTP超时 | 服务器未运行Web服务或防火墙限制 | 尝试不同端口或联系服务商 |
| Connection reset by peer | 服务器拒绝连接或需要特定访问方式 | 检查是否需要代理或VPN |
| ERR_CONNECTION_RESET | 浏览器连接被重置 | 用curl详细模式查看具体错误 |
| 403 Forbidden | 访问被拒绝 | 检查是否需要认证或User-Agent |
| 502 Bad Gateway | 服务器网关错误 | 等待一段时间后重试 |
| curl长时间hang无响应 | HTTP代理设置了但未运行 | `unset https_proxy http_proxy` 或确保代理在运行 |

### 浏览器工具失败时的备选方案
1. 用 `curl` 命令直接获取页面内容
2. 用 `web_search` 搜索网站相关信息（如果可用）
3. 尝试不同的URL协议（http/https）
4. 尝试访问子页面（/help, /docs, /support）

## Quick Reference

```bash
# Status
hermes doctor
hermes --version
hermes gateway status

# Web
hermes dashboard --port 9119 --no-open

# Update
hermes update && hermes gateway restart

# Profiles
ls ~/.hermes/profiles/

# Plugins
hermes plugins list --plain | grep enabled

# Projects
hermes project list

# 网站诊断
ping -c 3 <domain>
nslookup <domain>
curl -v --connect-timeout 10 https://<domain>
```
