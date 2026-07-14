# 自定义 Provider 接入指南

> 如何将第三方 API 代理（如 ChatAnywhere、API 中转服务）作为 Hermes custom_provider 接入，
> 实现优先免费、耗尽降级的安全调用模式。

---

## 一、核心模式

```
自定义 Provider（免费/低价） → 额度耗尽 → 降级到官方 API
```

**关键限制**：子代理（delegate_task）**不继承 fallback_providers 配置**，所以降级必须由莉莉丝手动检测错误并重试。

---

## 二、配置步骤

### 1. 安全存储 API Key

**❌ 错误做法**：Key 明文写在 config.yaml 的 `api_key:` 字段中

```yaml
# ❌ 不要这样
- name: Some Provider
  base_url: https://api.example.com/v1
  model: some-model
  api_key: sk-abc...xyz    # 明文 Key，有泄露风险
```

**✅ 正确做法**：Key 存到 `~/.hermes/.env`，用 `key_env` 引用

`.env` 新增：
```bash
SOME_PROVIDER_API_KEY=sk-abc...xyz
```

`config.yaml` 引用：
```yaml
- name: Some Provider
  base_url: https://api.example.com/v1
  model: some-model
  key_env: SOME_PROVIDER_API_KEY    # ✅ 环境变量引用
```

> **理由**：`.env` 文件权限 600（仅 owner 可读写），不在 git 仓库内。
> 而 `config.yaml` 可能被屏幕共享、备份、截图时泄露。

### 2. 添加 custom_providers 条目

每条 custom_provider 对应一个模型，格式示例：

```yaml
custom_providers:
  # 一个 base_url 可以对应多条，用不同的 model 名称区分
  - name: Provider Name       # 唯一标识，用作 provider 引用名
    base_url: https://api.../v1
    model: model-id          # 模型 ID，对接管时作为 model 参数传入
    key_env: PROVIDER_KEY    # 引用 .env 变量名
```

### 3. 调用方式

```python
# 优先走自定义 Provider
delegate_task(tasks=[{
    "goal": "...",
    "model": {"model": "model-id", "provider": "custom:Provider Name"}
}])

# 额度耗尽后备（手动降级）
delegate_task(tasks=[{
    "goal": "...",
    "model": {"model": "model-id", "provider": "deepseek"}  # 切到官方
}])
```

---

## 三、完整示例：ChatAnywhere 免费 Key

ChatAnywhere（https://github.com/chatanywhere/GPT_API_free）是一个公益 API 中转服务，
提供 26 个免费模型，国内直连无需代理。

### 配置

**`.env`** 新增：
```bash
CHATANYWHERE_API_KEY=sk-...
```

**`config.yaml`** custom_providers 部分（摘录）：
```yaml
# ── GPT-5 旗舰（5次/天） ──
- name: ChatAnywhere GPT-5.5
  base_url: https://api.chatanywhere.tech/v1
  model: gpt-5.5-ca
  key_env: CHATANYWHERE_API_KEY

# ── DeepSeek 系列（30次/天） ──
- name: ChatAnywhere Flash
  base_url: https://api.chatanywhere.tech/v1
  model: deepseek-v4-flash
  key_env: CHATANYWHERE_API_KEY
- name: ChatAnywhere Pro
  base_url: https://api.chatanywhere.tech/v1
  model: deepseek-v4-pro
  key_env: CHATANYWHERE_API_KEY

# ── 轻量高频（200次/天） ──
- name: ChatAnywhere GPT-4o Mini
  base_url: https://api.chatanywhere.tech/v1
  model: gpt-4o-mini-ca
  key_env: CHATANYWHERE_API_KEY
```

### 日限额

| 模型等级 | 日限额 | 示例模型 |
|---------|:------:|---------|
| GPT-5/4 旗舰 | 5次/天 | gpt-5.5-ca, gpt-5.4-ca, gpt-4o-ca |
| DeepSeek 系列 | 30次/天 | deepseek-v4-flash, deepseek-r1, deepseek-v3.2 |
| 轻量版 | 200次/天 | gpt-5-mini-ca, gpt-4o-mini-ca, gpt-4.1-mini-ca |
| Embedding | 200次/天 | text-embedding-3-large |

### 降级流程

```
莉莉/大莉 → ChatAnywhere（免费，30次/天）
              ↓ 429/quota 错误
          莉莉丝检测到失败 → 自动重试 DeepSeek 官方 API
              ↓ 也失败
          回滚到闪莉竞速兜底链
```

### 注意事项

- ChatAnywhere 所有模型 ID 都带 `-ca` 后缀（如 `gpt-5.5-ca`），表示来自第三方提供商
- 标准版（不带 `-ca`）需要付费 Key
- 200次/天的模型适合高频轻量任务

---

## 四、安全最佳实践（完整检查清单）

| # | 检查项 | 正确做法 |
|:-:|--------|---------|
| 1 | Key 存储位置 | `.env` 文件，不用 `api_key:` 硬编码 |
| 2 | 文件权限 | `.env` 设为 600，`.config.yaml` 设为 600 |
| 3 | 环境变量命名 | `PROVIDER_NAME_API_KEY` 格式，大写+下划线 |
| 4 | 引用方式 | `key_env: PROVIDER_NAME_API_KEY` |
| 5 | 已有配置改造 | 现有 `api_key:` 行改为 `key_env:`，Key 迁移到 `.env` |
| 6 | 子代理 fallback | 不支持自动 fallback，莉莉丝手动检测+重试 |

---

## 参见

- `nv-multi-model` — 三 Provider 竞速 Ping 系统（NVIDIA + OpenRouter + Google）
- `莉莉丝的工作规范.md` §六 容错与降级
- Hermes 文档：[Fallback Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers)
- Hermes 文档：[Credential Pools](https://hermes-agent.nousresearch.com/docs/user-guide/features/credential-pools)
