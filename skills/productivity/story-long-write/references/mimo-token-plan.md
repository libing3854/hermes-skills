# Xiaomi MiMo Token Plan 配置

## 两种使用方式

| 方式 | 说明 | Base URL | API Key 格式 |
|------|------|----------|-------------|
| 按量付费 API | 按实际使用量计费 | `https://api.xiaomimimo.com/v1` | `sk-xxxxx` |
| **Token Plan** | 固定订阅费，按套餐限量 | **`https://token-plan-cn.xiaomimimo.com/v1`** | **`tp-xxxxx`** |

⚠️ **Key 的 Base URL 必须匹配！** 用 Token Plan 的 key（`tp-` 开头）调按量付费的 endpoint（`api.xiaomimimo.com`）会报 401。

## 可用模型

| 模型 | 类型 | 说明 |
|:-----|:----|:------|
| `mimo-v2.5-pro` | 💬 对话 | **V2.5 专业版（推荐）** |
| `mimo-v2.5` | 💬 对话 | V2.5 标准版 |
| `mimo-v2-pro` | 💬 对话 | V2 专业版 |
| `mimo-v2-omni` | 🖼️ 全能 | V2 多模态（图/文/音） |
| `mimo-v2-tts` | 🎤 语音 | V2 语音合成 |
| `mimo-v2.5-tts` | 🎤 语音 | V2.5 语音合成 |
| `mimo-v2.5-tts-voiceclone` | 🎤 语音克隆 | V2.5 克隆 |
| `mimo-v2.5-tts-voicedesign` | 🎤 语音设计 | V2.5 设计 |

## Hermes Agent 配置

### 方式一：快速设置（hermes setup 向导）
初次配置选 Quick setup → 选择供应商 Xiaomi MiMo → 填写 API Key / Base URL / 默认模型

### 方式二：手动编辑 config.yaml

```yaml
model:
  provider: custom  # 注意：必须为 custom，不能是 xiaomi-coding 等自定义名
  base_url: https://token-plan-cn.xiaomimimo.com/v1
  api_key: tp-your-key-here
  default: mimo-v2.5-pro
```

### 方式三：自定义 provider（推荐，多模型可选）

```yaml
providers:
  xiaomi:
    name: Xiaomi MiMo
    base_url: https://token-plan-cn.xiaomimimo.com/v1
    key_env: XIAOMI_API_KEY
    api_mode: chat_completions
    default_model: mimo-v2.5-pro
    models:
      - mimo-v2.5-pro
      - mimo-v2.5
      - mimo-v2-pro
      - mimo-v2-omni
```

**.env 文件：**
```
XIAOMI_API_KEY=tp-your-key-here
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

## 验证

```bash
curl -s https://token-plan-cn.xiaomimimo.com/v1/models \
  -H "Authorization: Bearer tp-your-key-here" \
  | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"

curl -s -w "\nHTTP:%{http_code}" https://token-plan-cn.xiaomimimo.com/v1/chat/completions \
  -H "Authorization: Bearer tp-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-v2.5-pro","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```

## 切换 Token Plan（从按量付费切换过来）

编辑 `~/.hermes/.env`，将 `XIAOMI_API_KEY` 和 `XIAOMI_BASE_URL` 替换为 Token Plan 专属的值即可。

## 额度查询

MiMo 不提供公开的额度查询 API。额度信息需要在 MiMo 控制台（https://platform.xiaomimimo.com → 控制台）查看。

## 已知问题

- MiMo 模型输出包含 `reasoning_content` 字段（思维链），如果 Hermes Agent 解析有问题，需要检查 provider 的 `api_mode` 配置
- Token Plan 的 key 以 `tp-` 开头，与按量付费的 `sk-` 格式不同，注意区分
