# Agnes AI Provider 详细信息

## 基本信息

| 项目 | 内容 |
|------|------|
| 公司 | Sapiens AI（新加坡） |
| Base URL | `https://apihub.agnes-ai.com/v1` |
| 接口风格 | OpenAI 兼容 |
| 认证方式 | `Authorization: Bearer *** |
| 免费策略 | 长期免费，无到期限制 |

## 可用模型（实测）

### 文本模型（/v1/chat/completions）
| 模型ID | 状态 | 上下文 |
|--------|:----:|:------:|
| `agnes-2.0-flash` | ✅ 可用 | 256K |
| `agnes-1.5-flash` | ⚠️ 超时 | 待确认 |

### 图像模型（/v1/images/generations）
| 模型ID | 端点 | 状态 |
|--------|------|:----:|
| `agnes-image-2.0-flash` | `/v1/images/generations` | ✅ 可用 |
| `agnes-image-2.1-flash` | `/v1/images/generations` | 待测试 |

**⚠️ 图像模型不能通过 `/v1/chat/completions` 调用，必须用 `/v1/images/generations` 端点。**

curl 调用示例：
```bash
curl -s https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "一只可爱的猫咪坐在月亮上，星空背景，卡通风格",
    "n": 1,
    "size": "1024x1024"
  }'
```
返回 JSON 含 `data[0].url`（临时链接，需尽快下载）。

**Hermes 集成**：已创建 Agnes image_gen 插件（`~/.hermes/plugins/image_gen/agnes/`），`image_generate` 工具可直接调用 Agnes 生图。配置见下方"image_gen 插件"章节。也可通过 curl 直接调用 `/v1/images/generations`。

### 视频模型
| 模型ID | 状态 |
|--------|:----:|
| `agnes-video-v2.0` | 待测试 |

## API 限制

| 限制 | 数值 |
|------|------|
| RPM（免费用户） | ~20 次/分钟 |
| 触发点 | 第 22 个请求返回 429 |
| 错误信息 | "You've reached the API rate limit for free users" |

### 测试记录

#### 2026-06-11 首次测试
- agnes-2.0-flash: ✅ 200 OK（通过 curl 直接测试）
- agnes-image-2.0-flash（via chat/completions）: ❌ 404 Not Found
- /v1/models 端点: ❌ 401（不支持）

#### 2026-06-11 图像端点确认
- agnes-2.0-flash（via Hermes custom_providers）: ✅ 正常
- agnes-image-2.0-flash（via `/v1/images/generations`）: ✅ 1024x1024 PNG，~1.4MB，质量好
- 返回格式：`{"data":[{"url":"https://platform-outputs.agnes-ai.space/images/..."}]}`
- 图片链接有时效性，下载后保存到本地

### API Key 调试经验（2026-06-11，耗时 3 小时）
**症状**：API 始终返回 401 "无效的令牌"，即使 Key 是新的。
**错误尝试**：用 echo/sed/python/execute_code 等多种方式写入 .env，Key 始终被截断。
**根因**：Hermes 对 `sk-` 开头的字符串有自动掩码机制，任何通过 terminal/execute_code 传递的 Key 都会被截断。
**正确方式**：`hermes config set AGNES_API_KEY <key>` — 这是唯一能安全写入完整 Key 的方法。
**另一个坑**：`execute_code` 和 `delegate_task` 子进程无法读取 `.env` 中的环境变量，需要 Profile 配置 `key_env` 让 Hermes 内部处理。

### API Key 格式
- 前缀: `sk-`
- 长度: 51 字符
- 示例格式: `sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

## 配置到 Hermes

### 方法一：hermes config set（推荐）
```bash
hermes config set AGNES_API_KEY sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 方法二：custom_providers 配置
```yaml
custom_providers:
- base_url: https://apihub.agnes-ai.com/v1
  key_env: AGNES_API_KEY
  model: agnes-2.0-flash
  name: Agnes 2.0 Flash
- base_url: https://apihub.agnes-ai.com/v1
  key_env: AGNES_API_KEY
  model: agnes-1.5-flash
  name: Agnes 1.5 Flash
```

### Profile 配置（正确格式，2026-06-11 更新）

⚠️ Profile 名称不能含点号 `.`，否则 kanban/CLI 报 `Invalid profile name`。

```yaml
# ~/.hermes/profiles/shanli-agnes20flash/config.yaml
model:
  default: agnes-2.0-flash
  provider: "custom:Agnes 2.0 Flash"
custom_providers:
  - name: "Agnes 2.0 Flash"
    model: agnes-2.0-flash
    base_url: https://apihub.agnes-ai.com/v1
    key_env: AGNES_API_KEY
```

Profile 的 .env 文件需要复制主 .env 中的 AGNES_API_KEY。

### 已知可用 Profile 名称（2026-06-11 重建）

| Profile 名称 | 模型 | 用途 |
|-------------|------|------|
| `shanli-agnes15flash` | agnes-1.5-flash | 文本（⚠️ 2026-06-11 测试超时） |
| `shanli-agnes20flash` | agnes-2.0-flash | 文本 ✅ |
| `shanli-agnesimg20flash` | agnes-image-2.0-flash | 图像 |
| `shanli-agnesimg21flash` | agnes-image-2.1-flash | 图像 |
| `shanli-agnesvideo20` | agnes-video-v2.0 | 视频 |

## image_gen 插件（已创建 2026-06-11）

插件位置：`~/.hermes/plugins/image_gen/agnes/`

### 配置步骤

```bash
# 1. 设置 image_gen 使用 agnes provider
hermes config set image_gen.provider agnes
hermes config set image_gen.model agnes-image-2.0-flash

# 2. 启用插件（手动添加到 plugins.enabled）
# 编辑 ~/.hermes/config.yaml，在 plugins.enabled 列表中添加 'image_gen/agnes'
```

### 已知问题与修复

**AGNES_API_KEY 在工具进程中读不到**：`image_generate` 工具调用时报 "AGNES_API_KEY not set"。

**根因**：插件 `is_available()` 和 `generate()` 用 `os.environ.get("AGNES_API_KEY")` 读取，但工具进程的 `os.environ` 可能未被 `load_hermes_dotenv()` 填充。

**修复**：在插件中添加 `_get_api_key()` 辅助函数，先试 `os.environ`，失败则用 `hermes_cli.config.get_env_value()` 直接读 `.env` 文件：
```python
def _get_api_key() -> Optional[str]:
    key = os.environ.get("AGNES_API_KEY")
    if key:
        return key
    try:
        from hermes_cli.config import get_env_value
        return get_env_value("AGNES_API_KEY")
    except Exception:
        return None
```

**注意**：修改插件代码后需清缓存 + 新会话才生效：
```bash
find ~/.hermes/plugins/image_gen/agnes -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

## 与其他 Provider 对比

| 项目 | Agnes AI | Google Gemini | Groq | DeepSeek |
|------|:---:|:---:|:---:|:---:|
| 免费额度 | ✅ 长期免费 | ✅ 免费层 | ✅ 免费层 | ✅ 新用户免费 |
| RPM限制 | ~20 | 免费层限制 | 30 | 免费层限制 |
| 多模态 | ✅ | ✅ | ❌ | ❌ |
| OpenAI兼容 | ✅ | ✅ | ✅ | ✅ |
| 上下文 | 256K | 1M | 128K | 128K |
