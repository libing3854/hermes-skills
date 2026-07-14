---
name: mimo-code
description: |
  MiMo Code CLI 配置、故障排除和使用指南。MiMo Code 是小米的 AI 编程助手（类 Claude Code）。
  触发条件：用户问 MiMo Code 相关问题、mimo 启动失败、配置错误、模型选择、
  或需要使用 mimo CLI 执行编程任务时激活。
tags: [mimo, code, cli, xiaomi, debugging, config]
---

# MiMo Code 配置与故障排除

## 基本信息

- **二进制位置**: `~/.mimocode/bin/mimo`
- **symlink**: `/usr/local/bin/mimo`
- **版本**: 0.1.0
- **支持模型**: 仅小米模型（mimo/mimo-auto 等），不支持 Agnes

## 关键配置文件

### 1. 全局配置（最重要）
```
~/.config/mimocode/mimocode.json
```

**正确格式**（model 字段必须是字符串）:
```json
{
  "model": "mimo/mimo-auto"
}
```

**❌ 错误格式**（会导致 ConfigInvalidError）:
```json
{
  "model": {
    "default": "agnes-2.0-flash",
    "provider": "agnes"
  }
}
```

### 2. 认证配置
```
~/.local/share/mimocode/auth.json
```
包含 API keys，格式：
```json
{
  "xiaomi": {
    "type": "api",
    "key": "your-key",
    "metadata": {
      "uid": "your-uid",
      "base_url": "https://token-plan-cn.xiaomimimo.com/v1"
    }
  }
}
```

### 3. 日志文件
```
~/.local/share/mimocode/log/
```
最新日志查看：`ls -lt ~/.local/share/mimocode/log/*.log | head -1`

## 常见故障排除

### 启动失败：ConfigInvalidError

**症状**: `mimo` 命令无响应或立即退出，日志显示 `ConfigInvalidError`

**原因**: `~/.config/mimocode/mimocode.json` 中 `model` 字段格式错误

**修复**:
```bash
# 方法1：删除配置文件（恢复默认）
rm -f ~/.config/mimocode/mimocode.json

# 方法2：重写为正确格式
cat > ~/.config/mimocode/mimocode.json << 'EOF'
{
  "model": "mimo/mimo-auto"
}
EOF
```

### 中文输入乱码

**症状**: 通过 AppleScript keystroke 发送中文到 mimo 时显示乱码

**原因**: AppleScript keystroke 不支持 Unicode 中文

**修复**: 使用剪贴板粘贴方式：
```applescript
set the clipboard to "中文内容"
keystroke "v" using command down
```

### Agnes 模型不可用

**症状**: mimo 的 `/models` 列表中没有 agnes 模型

**原因**: MiMo Code 只支持小米模型，Agnes 模型需要在 Hermes 中单独配置

**解决方案**: 
- 在 Hermes 中使用 Agnes：通过 `delegate_task` 或 Hermes 配置
- 在 MiMo Code 中：仅使用 mimo/mimo-auto 等小米模型

### MiMo Code 模型配置错误导致崩溃

**症状**: 通过 Multica 分配任务给 MiMo Code 时立即失败，错误：`Model not found: agnes-2.0-flash/.`

**原因**: `~/.config/mimocode/mimocode.json` 中 model 字段被设为 `agnes-2.0-flash`，但 MiMo Code 只支持小米模型。

**修复**:
```bash
cat > ~/.config/mimocode/mimocode.json << 'EOF'
{
  "model": "mimo/mimo-auto"
}
EOF
```

**⚠️ 不要把 model 设为非小米模型（如 agnes-2.0-flash、deepseek 等），MiMo Code 不支持。**

## Multica 集成

MiMo Code 可以作为 Multica 的自定义 runtime 接入多agent管理平台。

**协议族**: `opencode`（MiMo Code 基于 OpenCode 开发）

**配置步骤**:
```bash
# 1. 创建自定义 runtime profile
multica runtime profile create \
  --command-name mimo \
  --display-name "MiMo Code" \
  --description "小米AI编程助手 MiMo Code (基于OpenCode)" \
  --protocol-family opencode

# 2. 设置可执行路径
multica runtime profile set-path <profile-id> \
  --path /Users/libing/.mimocode/bin/mimo

# 3. 创建 agent
multica agent create \
  --name "MiMo Code" \
  --runtime-id <runtime-id> \
  --description "小米AI编程助手 MiMo Code"

# 4. 重启 daemon
multica daemon restart
```

**⚠️ 模型配置必须先修复**（见上方"模型配置错误"），否则任务会立即失败。

## 常用命令

```bash
# 查看版本
mimo --version

# 查看可用模型
mimo models

# 启动交互模式
mimo

# 查看配置
mimo config list
```

## 与其他工具的集成

### Hermes 集成
- MiMo Code 有 Hermes 插件：`~/.hermes/plugins/mimo-code/`
- 提供 9 个工具（mimo_task, server management 等）
- 注意：MiMo Code 不能直接调用 Hermes 的 Agnes 模型

### 前台控制
- MiMo Code TUI 难以程序化控制（卡在文件列表）
- 批量修改用 `execute_code` 脚本最快
- 前台终端控制参考 `macos-computer-use` 技能
