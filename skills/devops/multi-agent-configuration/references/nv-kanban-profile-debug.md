# NV Kanban Profile 创建调试记录 (2026-06-26)

## 背景

冰哥想用NV API的免费模型跑kanban看板任务。创建了`nvlinshi` profile，但反复调试才成功。

## 时间线

1. **创建profile** → `hermes profile create nvlinshi --clone`
2. **配置NV provider** → 添加nvidia provider到config.yaml，默认模型为llama-4-maverick-128k
3. **测试kanban** → 任务一直running不执行 ❌
4. **调试发现**：worker日志显示Duration 5-10s，Messages只有2条（1 user, 0 tool calls）→ 模型不理解任务
5. **手动恢复验证**：`hermes --resume <session> -p nvlinshi -z "完成任务"` → 模型回复"什么任务？"
6. **关键发现**：nv nv模型不识别kanban的`work kanban task t_xxx`格式
7. **第二轮测试**：换mistral-nemotron → 同样卡住 ❌
8. **第三轮测试**：测试所有NV模型对kanban格式的理解
   - 简单对话中：大部分能理解
   - kanban worker中：全部迷失（复杂上下文干扰）
9. **突破口**：Qwen3.5 122B成功执行kanban任务！✅

## 创建NV Profile的正确步骤

### 1. 创建profile
```bash
hermes profile create nvlinshi --clone --description "NV测速最优模型"
```

### 2. 配置model和provider
```yaml
model:
  default: qwen/qwen3.5-122b-a10b
  provider: nvidia
  base_url: https://integrate.api.nvidia.com/v1

providers:
  nvidia:
    api_mode: chat_completions
    base_url: https://integrate.api.nvidia.com/v1
    default_model: qwen/qwen3.5-122b-a10b
    key_env: NVIDIA_API_KEY
    name: NVIDIA NIM
```

### 3. 必须添加到kanban profiles
```yaml
kanban:
  profiles: '["lili", "shanli", "nvlinshi"]'  # 必须包含nvlinshi！
```
**不添加的后果**：kanban dispatcher不创建nvlinshi的worker，任务永远不执行。

### 4. SOUL.md必须简短
**❌ 错误**：用莉莉丝的长篇人格（200行+），模型在复杂上下文中迷失
**✅ 正确**：用闪莉风格（20行，简洁执行者）：
```markdown
# 闪莉
你是闪莉，冰哥的执行助手。
## 风格
- 严格执行任务要求
- 直接输出结果，不解释过程
- 不废话，不用emoji
```

### 5. Agent配置精简
移除不必要的字段：`task_completion_guidance`、`parallel_tool_call_guidance`、`environment_probe`等

### 6. 重启Gateway
```bash
hermes gateway restart
```

### 7. 测试
```bash
hermes kanban create "测试" --assignee nvlinshi --body "回复：成功"
hermes kanban dispatch --max 1
# 等待30秒检查状态
```

## 模型兼容性测试结果

| 模型 | 速度 | kanban简单对话 | kanban worker |
|------|------|:---:|:---:|
| qwen/qwen3.5-122b | 916ms | ✅ | ✅ 唯一成功 |
| llama-4-maverick-128k | 627ms | ✅ | ❌ 调用browser_back |
| mistral-nemotron | 769ms | ✅ | ❌ 输出乱码 |
| deepseek-v4-flash | 995ms | ❓未测 | ❓ |
| deepseek-v4-pro | 1101ms | ❓未测 | ❓ |
| GLM-5.1 | 19831ms | ❌ 太慢 | ❌ |
| Kimi K2.5 | 404 | - | - |
| MiniMax M2.7 | 超时 | - | - |

## NV大模型可用列表（已加入nv_ping AB测速）

| 模型ID | 上下文 | 速度 |
|------|:---:|------|
| `deepseek-ai/deepseek-v4-flash` | 1M | 995ms |
| `deepseek-ai/deepseek-v4-pro` | 1M | 1101ms |
| `qwen/qwen3.5-122b-a10b` | 128K | 916ms |
| `z-ai/glm-5.1` | 203K | 19831ms |

## 核心教训

1. **NV模型大多不识别kanban格式** — Qwen3.5是唯一例外
2. **kanban profiles必须包含新profile名** — 否则worker不启动
3. **SOUL.md影响大** — 长人格会导致模型在复杂上下文中迷失
4. **手动chat vs kanban不同** — 简单对话能理解的格式，在完整worker上下文中未必能执行
