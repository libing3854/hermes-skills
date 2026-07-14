# 免费LLM项目详细目录

> 最后更新: 2026-06-10
> 来源: GitHub搜索 + Web研究 + 实测

## 一、完全免费、无需注册（实测可用）

### LLM7.io ✅ 实测可用

**网站**: https://llm7.io
**API地址**: https://api.llm7.io/v1
**注册要求**: 无
**API Key要求**: 无
**兼容格式**: OpenAI SDK
**实测状态(2026-06-10)**: ✅ 完全可用，无需任何认证

#### 可用模型

| 模型ID | 类型 | 上下文 | 延迟 |
|--------|------|--------|------|
| qwen3-235b | Free | 240K | ~3.7秒 |
| mistral-small-3.2 | Free | - | ~1.2秒 |
| codestral-latest | Free | 32K | ~1.0秒 |
| devstral-small-2:24b | Free | - | ~1.1秒 |
| kimi-k2.6 | Pro | 240K | - |
| minimax-m2.7 | Pro | 180K | - |
| deepseek-v4-flash | Pro | - | 402需付费 |

#### 使用示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.llm7.io/v1",
    api_key="not-needed"  # 任意值即可
)

response = client.chat.completions.create(
    model="qwen3-235b",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    max_tokens=10
)
print(response.choices[0].message.content)  # "4"
```

#### 延迟对比

| 平台 | 典型延迟 |
|------|----------|
| LLM7.io (免费) | 1000-4000ms |
| NVIDIA NIM | 200-500ms |

**结论**: 比NV慢2-7倍，但完全免费且无需注册。适合批量处理、备用API、开发测试。

---

## 二、每日更新Key项目

### alistaitsacle/free-llm-api-keys

**GitHub**: https://github.com/alistaitsacle/free-llm-api-keys
**Stars**: 2.1k | **Forks**: 206
**更新频率**: Bot每天3-5次自动更新
**最后更新**: 2026-06-10 15:22 (UTC+8)
**Commits**: 6,429

#### 可用模型 (2026-06-10)

| 模型 | Key数量 | 预算 | Rate Limit | 有效期 |
|------|---------|------|------------|--------|
| GPT-5.5 | 5 | $11-17/个 | 5 RPM | 24-48h |
| Claude Opus 4.7 | 2 | $20/个 | 5 RPM | 24h |
| Gemini 2.5 Flash | 6 | $20/个 | 20 RPM | 24h |
| Kimi K2.5 | 4 | $12-19/个 | 10 RPM | 48h |
| DeepSeek V4 Pro | 1 | $20 | 10 RPM | 24h |
| OpenRouter/owl-alpha | 1 | $20 | 10 RPM | 24h |
| Qwen 3.6 Flash | 1 | $20 | 10 RPM | 24h |

#### 使用示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key="sk-xxx"  # 从README获取最新Key
)

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### 注意事项

- Key是公开的，预算可能被其他人消耗
- 建议每天获取最新Key
- 关注X账号 @getkeyway 获取最新Key推送
- 项目有Playground可在线验证Key: https://alistaitsacle.github.io/free-llm-api-keys/

---

### completions.me ⚠️ 演示API

**网站**: https://completions.me/
**类型**: 免费无限AI API
**注册**: 需要注册账号获取Key
**实测状态(2026-06-10)**: ⚠️ 所有模型返回同一个Rickroll回复，是演示API，不是真正模型代理

#### 支持模型（声称）

- **Anthropic**: Claude Opus 4.6, Sonnet 4.5
- **OpenAI**: GPT-5, GPT-4o
- **Google**: Gemini
- **xAI**: Grok

#### 实测结果

| 测试 | 结果 |
|------|------|
| 注册账号 | ✅ 成功，无需邮箱验证 |
| 获取API Key | ✅ 成功，格式 `sk-cp_...` |
| API调用 | ✅ 返回200 OK |
| 模型推理 | ❌ 所有模型返回同一个Rickroll回复 |
| usage字段 | ❌ 全部为0（无实际token计数） |

#### 结论

completions.me是一个**演示API**，用于展示其前端界面和Claude Code代理功能，**并非真正提供模型推理服务**。不要用于实际项目。

#### 已注册账号 (2026-06-10)

- **用户名**: bingge2026
- **密码**: LLS!&147
- **API Key**: `sk-cp_fa01ea9ac01d8753214fead26bce7d2027e42c0d78f28107`
- **状态**: 可登录但API为演示模式，不可用于实际推理

---

## 二、本地部署网关项目

### ProxyGateLLM

**GitHub**: https://github.com/mulkymalikuldhrs/ProxyGateLLM
**Stars**: 34
**版本**: v6.0.0
**依赖**: 4个 (express, dotenv, @heyputer/puter.js, @anthropic-ai/sdk)
**License**: MIT

#### 22个Provider完整列表

**FREE - 无需Key (10个)**

| # | Provider | 模型 | 特点 |
|---|----------|------|------|
| 1 | Pollinations AI | GPT-4o Mini, Mistral, Llama, DeepSeek R1, Qwen | OpenAI兼容，流式，最稳定 |
| 2 | DuckDuckGo AI Chat | GPT-4o Mini, Claude 3 Haiku, Llama 3.1 70B, Mixtral | VQD token auth，隐私优先 |
| 3 | LLM7.io | GPT-4o, DeepSeek Chat/R1, Llama 3.3 70B, Qwen Coder | OpenAI兼容，30+模型 |
| 4 | DeepAI | Free chat mode | 无需登录 |
| 5 | FreeGPT | GPT-4o, GPT-4o Mini, GPT-4 | 模拟流式 |
| 6 | Api.airforce | GPT-4o, DeepSeek, Llama | 55+免费模型 |
| 7 | Venice.ai | Llama 3.3 70B, DeepSeek R1, Qwen Coder, Gemma 3 | 隐私优先 |
| 8 | G4F/FreeGPT | GPT-4o, GPT-4o Mini, Claude 3.5 Sonnet | Python，较脆弱 |
| 9 | Blackbox AI | Blackbox AI, Blackbox AI Pro | 逆向工程 |
| 10 | Phind | Phind 70B | 代码专家 |

**FREE KEY - 需注册 (8个)**

| # | Provider | 免费额度 |
|---|----------|----------|
| 11 | Puter.js SDK | 500+模型 |
| 12 | OpenRouter Free | 337+免费模型 |
| 13 | Google AI Studio | 1500请求/天 |
| 14 | Groq | 30 RPM |
| 15 | Cerebras | 1M tokens/天 |
| 16 | Cloudflare Workers AI | 10K neurons/天 |
| 17 | Cohere | 免费Tier |
| 18 | HuggingFace | 免费推理API |

**BYOAPI - 需付费Key (4个)**

| # | Provider | 免费额度 |
|---|----------|----------|
| 19 | Together AI | $5免费 |
| 20 | SambaNova | $5免费 |
| 21 | Scaleway | 按量付费 |
| 22 | Inference.net | $10免费 |

#### 部署方法

```bash
git clone https://github.com/mulkymalikuldhrs/ProxyGateLLM
cd ProxyGateLLM
npm install
npm start
# 本地端口3333
```

#### API格式

- OpenAI兼容: `http://localhost:3333/v1/chat/completions`
- Anthropic兼容: `http://localhost:3333/v1/messages`
- 支持SSE流式
- 内置PWA Dashboard

#### 特性

- 4状态断路器 (CLOSED → DEGRADED → OPEN → HALF_OPEN)
- 预估成本 (30+模型)
- 智能路由 (健康+成本+优先级)
- 自动故障转移

---

### GoDiao/Free-Way

**GitHub**: https://github.com/GoDiao/Free-Way
**Stars**: 21
**语言**: TypeScript
**License**: MIT

#### 支持Provider

openrouter, groq, github, cloudflare, siliconflow, cerebras, mistral, cohere, nvidia, llm7, kilo, zhipu, opencode, zenmux

#### 部署方法

```bash
npx @godiao/free-way
# 或
npm install -g @godiao/free-way
freeway
# 本地端口8787
```

#### 特点

- BYOK (Bring Your Own Key) 本地优先
- OpenAI + Anthropic兼容
- 故障转移路由
- Provider控制台 (浏览器配置)
- 跟踪免费Tier变化

---

## 三、资源索引项目

### zebbern/no-cost-ai

**GitHub**: https://github.com/zebbern/no-cost-ai
**Stars**: 1.6k

#### 无需注册 (27个聊天 + 5个媒体 + 3个语音)

**聊天界面精选**

| 网站 | 免费模型 | 限制 |
|------|----------|------|
| lmarena.ai | 40+ | 无限 |
| g4f.dev | 200+本地模型 | 无限 |
| meta.ai | Llama 4 | 无限 |
| sharedchat.cn | GPT-4o, o3, o4-mini | 无限（响应可能慢）|
| phind.com | Phind-70B | 无限 |
| groq.com | 15+ | 30 RPM |
| chatgpt.com | GPT-3.5, GPT-4o | 5-10条GPT-4o |
| chat.mistral.ai | Le Chat | 10条/24h |
| perplexity.ai | GPT-3.5, GPT-4.1, Claude 4.0 | 3 Pro搜索/天 |
| grok.com | Grok 3 | 3条/2h |
| kimi.com | K2, K1.5 | 有限使用 |
| gemini.google.com | Gemini-2.5-fast | 32K tokens/天 |
| copilot.microsoft.com | GPT-5 | 无限，1图/天 |

**媒体生成**

| 网站 | 免费模型 | 限制 |
|------|----------|------|
| runwayml.com | Gen-4 | 无限 |
| pollinations.ai | 多种模型 | 无限 |
| Vheer.com | 自有AI | 无限，无水印 |

**开发者API**

| 网站 | 免费模型 | 限制 |
|------|----------|------|
| uncloseai.com | Hermes AI, Qwen 3 Coder | 无限，OpenAI兼容 |
| ollama.com | 大量模型 | 无限（本地/云端）|
| g4f.dev | 多种 | 无限 |

---

### awesome-free-llm-apis

**GitHub**: https://github.com/mnfst/awesome-free-llm-apis

#### Provider APIs (模型训练/微调公司)

| Provider | 免费额度 | 关键模型 | Base URL |
|----------|----------|----------|----------|
| AI21 Labs | $10注册送 | Jamba Large/Mini | api.ai21.com/studio/v1 |
| Alibaba Cloud | 1M tokens/模型 | Qwen3-Max/Plus | dashscope-intl.aliyuncs.com |
| Cohere | 1000 API调用/月 | Command A/R+ | api.cohere.com/v2 |
| DeepSeek | 5M tokens | V3.2, R1 | api.deepseek.com/v1 |
| Google Gemini | 5-15 RPM | Gemini 2.5 Pro/Flash | generativelanguage.googleapis.com |
| Mistral AI | ~1B tokens/月 | Mistral Large 3 | api.mistral.ai/v1 |
| xAI | $25注册送 | Grok 4.3 | api.x.ai/v1 |
| Z AI (智谱) | 永久免费 | GLM-4.7-Flash | open.bigmodel.cn/api/paas/v4 |

#### Inference Providers (第三方推理平台)

| Provider | 免费额度 | 关键模型 | Base URL |
|----------|----------|----------|----------|
| Cerebras | 1M tokens/天 | Llama 3.3, Qwen 3 | api.cerebras.ai/v1 |
| Cloudflare | 10K neurons/天 | 50+模型 | api.cloudflare.com/client/v4/accounts/{id}/ai/run |
| GitHub Models | 10-50 RPD | GPT-5, GPT-4.1 | models.github.ai/inference |
| Groq | 30 RPM | Llama 3.3, Kimi K2 | api.groq.com/openai/v1 |
| HuggingFace | 100K credits/月 | 数千模型 | router.huggingface.co/v1 |
| Kilo Code | ~200 req/hr | Grok, MiniMax | api.kilo.ai/api/gateway |
| LLM7.io | 30 RPM | 30+模型 | api.llm7.io/v1 |
| Nebius | $1注册送 | 60+开源模型 | api.studio.nebius.com/v1 |
| Nscale | $5注册送 | Llama 3.3 | inference.api.nscale.com/v1 |

---

## 四、各平台免费攻略速查

### 硅基流动 SiliconFlow (国内推荐)

**官网**: https://cloud.siliconflow.cn
**特点**: 国内访问快，有永久免费模型
**免费额度**: 注册送2000万tokens + 16元代金券
**注册方式**: 手机号验证 + 图形验证码(CAPTCHA)
**兼容性**: OpenAI API兼容
**实测状态(2026-06-10)**: ⚠️ 注册需要解决图形验证码（依次点击汉字），自动化困难

### ChatGPT/GPT

| 渠道 | 免费额度 | 获取方式 |
|------|----------|----------|
| GitHub Models | GPT-5 10 RPM, 50 RPD | GitHub账号 |
| completions.me | GPT-5 API | 注册 |
| free-llm-api-keys | GPT-5.5 Key | 每天获取 |
| chatgpt.com | GPT-5.5 5-10条/5h | 官网 |

### Claude

| 渠道 | 免费额度 | 获取方式 |
|------|----------|----------|
| completions.me | Claude Opus 4.6 API | 注册 |
| free-llm-api-keys | Claude Opus 4.7 Key | 每天获取 |
| claude.ai | Sonnet 4.5 每5h重置 | 官网 |
| writesonic.com | Claude Sonnet 3.5 | 150+国家，10000积分/月 |

### Gemini

| 渠道 | 免费额度 | 获取方式 |
|------|----------|----------|
| Google AI Studio | 1500 RPM | Google账号 |
| free-llm-api-keys | Gemini 2.5 Flash Key | 每天获取 |
| gemini.google.com | 128K tokens/天 | 官网（注册后更多）|

### Grok

| 渠道 | 免费额度 | 获取方式 |
|------|----------|----------|
| xAI | $25注册送 | xAI账号（无需信用卡）|
| ProxyGateLLM | Grok 3 | 本地部署 |
| grok.com | 3条/2h | 官网 |

### DeepSeek

| 渠道 | 免费额度 | 获取方式 |
|------|----------|----------|
| DeepSeek官方 | 5M tokens | 注册 |
| ProxyGateLLM | DeepSeek R1 | 本地部署 |
| LLM7.io | DeepSeek R1/V3 | 免费 |

---

## 五、搜索关键词库

### GitHub搜索

```
free-llm
free-ai
free-api
free-llm-api-keys
no-cost-ai
awesome-free-llm-apis
```

### Web搜索

```
free LLM API key 2026
GitHub free AI API proxy self-host
白嫖 大模型 API 免费
free Claude GPT Gemini API
free AI API no credit card
```

### 中文社区

```
linux.do 免费API
V2EX 白嫖 AI
知乎 免费大模型
```
