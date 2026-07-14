---
name: free-ai-providers
description: 配置和调试免费/自定义 AI Provider 到 Hermes。当用户要求添加新的 AI API（如 Agnes AI、Groq、硅基流动等）时使用。
version: 1.0
---

# 免费 AI Provider 配置指南

## 触发条件
- 用户想添加新的免费/自定义 AI API Provider
- 用户遇到 API Key 配置问题
- 用户要求测试新 Provider
- 用户想为某个 Provider 创建 Profile

## 配置流程（标准三步）

### 第一步：保存 API Key
```bash
hermes config set <KEY_NAME> <api-key-value>
```
> ⚠️ **关键：必须用 `hermes config set`，不要直接编辑 .env**

原因：Hermes 的 terminal/execute_code 环境会自动掩码以 `sk-` 开头的字符串。任何通过 echo/sed/cat 传递的 API Key 都会被截断。只有 `hermes config set` 能安全写入 .env。

验证 Key 完整性：
```bash
grep "<KEY_NAME>" ~/.hermes/.env | wc -c
# 期望值 = Key长度 + KEY_NAME= 的长度 + 1（换行符）
```

### 第二步：添加 custom_provider 到 config.yaml
```yaml
custom_providers:
- base_url: https://api.example.com/v1
  key_env: KEY_NAME
  model: model-id
  name: Display Name
```

### 第三步：创建 Profile（可选但推荐）
```bash
mkdir -p ~/.hermes/profiles/<profile-name>
echo 'KEY_NAME=<key-value>' > ~/.hermes/profiles/<profile-name>/.env
```

## Profile 命名规则

⚠️ **Profiles 名称必须匹配 `[a-z0-9][a-z0-9_-]{0,63}`**
- ❌ 不能包含中文
- ❌ 不能包含大写字母（会被转为小写，但可能导致匹配失败）
- ❌ **不能包含点号 `.`** — kanban dispatcher 和 CLI 都会拒绝，报 `Invalid profile name`
- ✅ 使用纯英文小写 + 数字 + 连字符/下划线
- ✅ 示例：`shanli-agnes20flash`（不是 `shanli-agnes2.0flash`）

## Provider 诊断流程

当 API 返回 401 "无效的令牌" 时，按以下顺序诊断：

1. **检查 Key 长度**（最重要！）
   ```bash
   grep "KEY_NAME" ~/.hermes/.env | cut -d= -f2 | wc -c
   ```
   如果只有 14 字符左右 → Key 被截断，用 `hermes config set` 重新设置

2. **用 curl 直接测试**
   ```bash
   curl -s -X POST "https://api.example.com/v1/chat/completions" \
     -H "Authorization: Bearer $KEY_NAME" \
     -H "Content-Type: application/json" \
     -d '{"model":"model-id","messages":[{"role":"user","content":"hi"}]}'
   ```

3. **检查 Profile .env 是否同步**
   ```bash
   for p in ~/.hermes/profiles/*/; do echo "$p: $(cat "$p.env" | wc -c)"; done
   ```

4. **查询实际可用模型**（如果 Provider 支持）
   ```bash
   curl -s "https://api.example.com/v1/models" \
     -H "Authorization: Bearer ***
   ```
   ⚠️ 不是所有 Provider 都支持 /v1/models 端点

## 已知 Provider 信息

见 `references/agnes-ai.md` — Agnes AI 详细信息
见 `references/freemodel.md` — FreeModel API 详细信息（Claude/GPT模型代理）
见 `references/longcat.md` — LongCat 大模型（美团），2026-06-30更新：LongCat-2.0正式发布，旧模型全部下线

## Anthropic 格式 Provider 配置

部分 Provider（如 FreeModel 的 Claude 模型）使用 Anthropic 原生 API 格式而非 OpenAI 格式。配置时需添加 `api_mode: anthropic_messages`：

```yaml
custom_providers:
- api_key: <your-key>
  base_url: https://cc.freemodel.dev
  model: claude-opus-4-8
  name: FreeModel Claude Opus 4.8
  api_mode: anthropic_messages  # 关键！告诉 Hermes 使用 Anthropic 消息格式
```

**支持的 api_mode 值：**
- `chat_completions` — OpenAI 格式（默认）
- `anthropic_messages` — Anthropic Messages API 格式
- `codex_responses` — Codex Responses 格式
- 空字符串 — 自动检测（根据 URL）

**验证方法：** 用 `delegate_task(model="custom:Name", ...)` 测试

详见 `references/freemodel.md` — FreeModel 双端点详细信息

## 清理 Custom Providers

当 custom_providers 列表膨胀（如从 37 个涨到不需要的数量），用 Python 脚本批量清理：

```python
import yaml
with open('/Users/libing/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)

providers = cfg.get('custom_providers', [])
keep = [p for p in providers if KEEP_CONDITION]  # 按名称/URL过滤
cfg['custom_providers'] = keep

with open('/Users/libing/.hermes/config.yaml', 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

**注意**：`yaml.dump` 会重写整个文件格式。清理前备份：
```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak
```

清理后必须重启 Gateway：
```bash
hermes gateway restart
```

## 常见陷阱

1. **🔴 不要用 echo/sed/cat/execute_code 写 Key** — Hermes 对 `sk-` 开头的字符串有自动掩码机制，任何通过 terminal/execute_code 传递的 Key 会被截断成 13-14 字符。只用 `hermes config set <KEY_NAME> <key>`。
2. **🔴 不要用 execute_code 硬编码 Key** — 同样会被截断。这个机制不影响 `hermes config set`，因为那是内部安全通道。
3. **🔴 Profile 命名用英文** — 必须匹配 `[a-z0-9][a-z0-9_-]{0,63}`，中文会导致 `spawn_failed: Invalid profile name`。
4. **图像模型端点可能不同** — 不是所有 Provider 的图像生成都在 `/v1/chat/completions`。例如 Agnes 图像模型必须用 `/v1/images/generations`（curl 直接调用有效），Hermes 的 `image_generate` 工具默认走 FAL.ai 不走 Agnes。详见 `references/agnes-ai.md`。
5. **子代理不继承环境变量** — delegate_task 的子代理读不到 export 的环境变量，需依赖 `key_env` 配置让 Hermes 内部加载 .env。
6. **先测试文本模型** — 确认 API Key 有效后再测试图像/视频模型。
7. **/v1/models 端点不一定支持** — 不是所有 OpenAI 兼容 Provider 都支持模型列表端点。
8. **🔴 免费 Provider 有每日额度限制** — FreeModel 等免费 Provider 通常有每日请求/Token 限额。并发多个 session 会迅速耗尽额度。错误码 402 + "Usage limit reached" 表示额度用完。**建议**：重要任务前先确认剩余额度，避免同时跑超过 2 个并发 session。

## Profile 委托模式（推荐）

当需要让特定模型执行复杂任务（如小说修改）时，**创建 Profile 比直接调 API 更可靠**：

```bash
# 创建 profile
hermes profile create <name> --clone --description "..."
# 配置模型（修改 profile 的 config.yaml）
# 然后委托任务
hermes -p <name> chat -q "任务描述" -Q --max-turns 30
```

**优势**：绕过 API key 屏蔽、proxy 限制，Agent 有完整工具集。
**详见**：`novel-writing-pipeline` 技能的"外部AI编辑"章节。
8. **检查 Key 长度快速诊断截断** — `grep "KEY_NAME" ~/.hermes/.env | cut -d= -f2 | wc -c`，如果远远小于预期长度就是被截断了。
