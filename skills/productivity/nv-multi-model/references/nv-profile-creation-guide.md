# NV测速模型 → Profile创建指南

从NV测速数据中选择模型创建hermes profile的完整流程。

## 创建流程

```bash
# 1. 查看最新测速排名
cat ~/.hermes/data/NVping/tmp/ranking.json

# 2. 选择目标模型（优先速度快+instruct类）
python3 -c "
import json
with open('.hermes/data/NVping/tmp/ping_B.json') as f:
    p = json.load(f)
for name, v in sorted(p['models'].items(), key=lambda x: x[1].get('ms', 99999)):
    if v.get('ok'):
        print(f'{v[\"ms\"]:>5}ms  {name}')
"

# 3. 测试模型理解能力（关键步骤）
# 用简单kanban格式测试模型是否能理解指令
curl -s -m 15 -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -d '{"model":"MODEL_ID","messages":[{"role":"user","content":"work kanban task t_test\n回复两个字：成功"}],"max_tokens":20}'
# 判断标准：回复包含"成功" → 初步通过

# 4. 创建profile（从default克隆）
hermes profile create <name> --clone --description "NV模型专用"

# 5. 修改config.yaml
#   model.default: 所选模型ID（如 mistralai/mistral-nemotron）
#   model.provider: nvidia
#   model.base_url: https://integrate.api.nvidia.com/v1
#   providers 添加 nvidia 配置块

# 6. 修改SOUL.md为闪莉风格（简洁执行者）
# ❌ 不要用莉莉丝风格（太长，干扰kanban worker理解）
# ✅ 用 shanli 的SOUL.md风格（直接、简洁）

# 7. 简化agent配置
# 移除多余字段：task_completion_guidance, parallel_tool_call_guidance,
#   environment_probe, environment_hint, coding_context,
#   verify_on_stop, image_input_mode, reasoning_effort, verbose
# gateway_timeout 设为 1800（与shanli一致）

# 8. 添加 kanban.profiles 包含新profile名

# 9. 重启gateway测试
hermes gateway restart
```

## 已知不兼容的模型类别

| 类别 | 模型示例 | 问题 |
|------|---------|------|
| guard/safety类 | nemoguard-*, gliner-pii | 只能做安全检测 |
| calibration类 | ising-calibration-* | 专用校准模型 |
| 视觉专用 | *-vision-*, *-vl-* | 不擅长纯文本指令 |
| 翻译专用 | riva-translate-* | 只能翻译 |
| 超小模型 | nemotron-mini-4b, gemma-2-2b | 能力不足 |

## kanban worker兼容性

**结论（2026-06-26实测）：** 当前25个NV模型在完整kanban worker上下文中均不工作。

- 简单对话：✅ 能理解 `work kanban task` 格式
- kanban worker：❌ 在系统prompt+工具+技能+任务的复杂上下文中迷失

**应用建议：**
- NV模型 → 手动chat、长文本分析、深度审核
- kanban worker → 仍用闪莉(longcat)、lili(deepseek)