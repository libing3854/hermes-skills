---
name: agnes-ai-configuration
description: Agnes AI配置和使用指南 - API Key配置、图像生成、模型对照测试
version: 1.0
tags: [agnes, api, 图像生成, 配置]
---

# Agnes AI配置和使用指南

## API配置

### 基本信息
- **API地址**: apihub.agnes-ai.com/v1
- **环境变量**: AGNES_API_KEY
- **配置位置**: `~/.hermes/.env`

### 配置示例
```
AGNES_API_KEY=sk-xxxxx
```

## Custom Provider配置

### config.yaml配置
```yaml
providers:
  custom:ChatAnywhere Flash:
    api_key_env: CHATANYWHERE_API_KEY
    base_url: https://api.chatanywhere.tech/v1
    default_model: deepseek-v4-flash
```

### Profiles配置
已配置的Profiles：
- shanli-agnes15flash
- shanli-agnes20flash
- agnesimg20flash
- agnesimg21flash
- agnesvideo20

⚠️ **注意**: profile名禁点号

## 图像生成插件

### 插件位置
`~/.hermes/plugins/image_gen/agnes/`

### 使用方式
通过Hermes内部custom_providers调用，不在沙箱硬编码测试。

## 模型对照测试

### 测试方法
1. 输出到不同目录
2. 确认质量后覆盖原文

### 测试结果（2026-06-11）
- 默认模型闪莉：完成度低，文笔一般
- Agnes 2.0 Flash：完成度高，修改精准，文笔更自然

## MiMo Code 配置 Agnes（2026-06-13 实测）

### 配置文件格式
MiMo Code 使用 `mimocode.json` 配置自定义 provider：

```json
{
  "$schema": "https://mimo.xiaomi.com//config.json",
  "model": "agnes/agnes-2.0-flash",
  "provider": {
    "agnes": {
      "name": "Agnes AI",
      "api": "https://apihub.agnes-ai.com/v1",
      "options": {
        "apiKey": "sk-xxxxx"
      },
      "models": {
        "agnes-2.0-flash": {
          "name": "Agnes 2.0 Flash"
        },
        "agnes-1.5-flash": {
          "name": "Agnes 1.5 Flash"
        }
      }
    }
  }
}
```

### 关键点
- `model` 格式：`provider_id/model_id`（如 `agnes/agnes-2.0-flash`）
- `provider` 对象中定义自定义 provider
- `api` 字段使用 Agnes API 地址
- `options.apiKey` 填入 Agnes API Key

### 启动方式
```bash
cd /path/to/project  # 项目目录必须包含 mimocode.json
mimo
# 然后按 ctrl+x m 切换模型
```

### ⚠️ MiMo Code 可能修改 Hermes 配置
**问题**: MiMo Code 在运行过程中可能自动修改 `~/.hermes/config.yaml`，导致默认模型被更改。

**症状**: Hermes 默认模型突然从 mimo-v2.5 变成 agnes-2.0-flash

**解决**:
1. 检查 `~/.hermes/config.yaml` 的 `model:` 部分
2. 改回原来的配置：
```yaml
model:
  default: mimo-v2.5
  provider: xiaomi
```
3. 删除 MiMo Code 的配置文件防止再次修改：
```bash
rm /path/to/project/mimocode.json
```

**预防**: 不要在 MiMo Code 配置中设置 `model:` 字段，只在需要时用 `--model` 参数临时指定。

## 常见问题

### API Key在沙箱中被截断
**问题**: terminal/execute_code/delegate_task沙箱会自动截断所有以sk-开头的API Key
**解决**: 先在config.yaml的custom_providers中配置key_env，通过Hermes内部调用

### config.yaml中mimo-clone被误用为LLM provider
**问题**: mimo-clone是TTS插件，不是LLM provider。如果在config.yaml中错误地将LLM任务（model.provider, delegation.provider, auxiliary.provider等）设置为mimo-clone，会导致"Provider authentication failed: Unknown provider 'mimo-clone'"错误。
**症状**: 其他窗口报错"Provider authentication failed: Unknown provider 'mimo-clone'"
**解决**: 
1. 检查config.yaml中所有`provider: mimo-clone`的位置
2. LLM任务（title_generation, auxiliary, delegation, main model）改为`provider: xiaomi`
3. TTS任务保持`provider: mimo-clone`不变
```bash
# 检查哪些地方用了mimo-clone
grep -n "provider: mimo-clone" ~/.hermes/config.yaml

# 修复（保留TTS的mimo-clone，其他改为xiaomi）
sed -i '' '133s/provider: mimo-clone/provider: xiaomi/' ~/.hermes/config.yaml
# ... 对其他LLM配置行做同样修改
```
**验证**: `hermes doctor` 应不再报 provider 错误

### 验证方式
```bash
hermes chat -m agnes-2.0-flash --provider "custom:Agnes 2.0 Flash"
# 或
hermes --profile shanli-agnes20flash
```

## 注意事项

1. 新API → 先配custom_providers → 再通过Hermes调用
2. 不要在沙箱硬编码Key测试
3. Profile名禁点号
4. Workspace需先启动Dashboard才可用
