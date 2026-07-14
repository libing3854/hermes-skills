# Gemini Web-to-API 项目汇总

## 背景

Google Gemini Pro（$19.99/月）订阅与官方 API 是独立计费体系：
- **Pro 会员**: gemini.google.com 网页/App + Workspace 集成
- **Google AI Studio API**: 免费层有额度，超出按 token 计费
- 两者不互通，Pro 配额不能用于 API 调用

逆向方案通过浏览器 Cookie 模拟网页请求，让 Pro 额度可以 API 形式使用。

## 安全审查结论（2026-06-17 大莉M深度审查）

以 HanaokaYuzu/Gemini-API 为样本的源码审查结论：

**安全性 ✅ 安全**
- 所有 HTTP 请求目标仅 6 个 Google 官方域名（gemini.google.com, accounts.google.com, content-push.googleapis.com, www.google.com）
- 无任何向第三方服务器发送 Cookie 或用户数据的代码
- 无 telemetry / analytics / phone-home 机制
- Cookie 缓存文件权限 0o600（仅所有者可读写）
- curl_cffi 的 impersonate="chrome" 仅用于 TLS 指纹伪装，不发送额外数据

**依赖链 ✅ 可信**
- 4 个直接依赖均为千万级/亿级下载量的知名库：curl-cffi, loguru, orjson, pydantic
- 使用 Dependabot 自动更新
- PyPI 发布使用 Trusted Publishing（OIDC）

**稳定性 ⚠️ 中等风险（逆向项目固有）**
- Google 已在主动反制（代码处理了 IP_TEMPORARILY_BLOCKED 等状态码）
- 单人维护项目，但社区有贡献
- TLS 指纹伪装可能被更严格验证击败
- 类似项目历史上频繁被打断

## 项目排名（安全 > 星数）

### 1. Sophomoresty/gemini-web2api ⭐ 1.8k, Fork 420（最安全）
- **GitHub**: github.com/Sophomoresty/gemini-web2api
- **特点**: 单文件 Python 脚本，零依赖，代码量极小
- **安全优势**: 代码少 = 攻击面小，最容易审查
- **兼容**: OpenAI API 格式
- **最适合**: 安全优先、本地运行

### 2. HanaokaYuzu/Gemini-API ⭐ 3.2k, Fork 506（最成熟）
- **GitHub**: github.com/HanaokaYuzu/Gemini-API
- **语言**: Python，PyPI 包名 gemini-webapi
- **特点**: 最流行的逆向 Gemini API
- **功能**: 多轮对话、Gem、System Prompt、流式输出、图片/视频/音频生成、Deep Research、CLI
- **依赖**: curl-cffi, loguru, orjson, pydantic（均为知名库）
- **认证**: __Secure-1PSID + __Secure-1PSIDTS Cookie，或 browser-cookie3 自动读取
- **Cookie 自动刷新**: 默认启用，后台持续运行
- **Python 要求**: 3.10+
- **许可证**: AGPL-3.0（copyleft，修改后分发需开源）
- **最适合**: 功能需求多、长期使用

### 3. Amm1rr/WebAI-to-API ⭐ 1.3k
- **GitHub**: github.com/Amm1rr/WebAI-to-API
- **特点**: FastAPI 框架，Apache 2.0 协议
- **缺点**: 集成 gpt4free 等多后端，依赖多，审查成本高

### 4. ntthanh2603/gemini-web-to-api ⭐ ~240
- **GitHub**: github.com/ntthanh2603/gemini-web-to-api
- **特点**: 兼容 OpenAI / Gemini / Claude 格式

### 5. PublicAffairs/openai-gemini
- **GitHub**: github.com/PublicAffairs/openai-gemini
- **特点**: Serverless 部署，Gemini→OpenAI API 代理

### 6. SiaLabs/Free-API-Server
- **GitHub**: github.com/SiaLabs/Free-API-Server
- **特点**: OpenAI 兼容 API 服务器，无需 API Key
- **模型**: Gemini 3.1 Pro, Gemini 3.0 Flash

### 7. AndyShaman/gemini-webapi-mcp
- **GitHub**: github.com/AndyShaman/gemini-webapi-mcp
- **特点**: MCP Server，支持图片生成/编辑/对话

## Cookie 获取方法

1. 浏览器登录 gemini.google.com
2. 打开开发者工具 (F12) → Network 标签
3. 刷新页面，找到任意请求
4. 复制 Cookie 头中的关键值（通常是 `__Secure-1PSID`、`__Secure-1PSIDTS` 等）
5. 注意：Cookie 有效期通常 1-7 天，过期需重新获取

## 配置到 Hermes 的示例

以 HanaokaYuzu/Gemini-API 为例，本地部署后可配置为 Hermes custom_provider:

```yaml
custom_providers:
- api_key: "any-value"  # 逆向项目不需要真正的 API Key
  base_url: "http://localhost:8080/v1"  # 本地代理端点
  model: "gemini-3.1-pro"  # 或 gemini-2.5-pro
  name: "Gemini Web Pro"
```

## 使用建议

1. **用独立 Google 账号**，别用主力号（降封号风险）
2. **订阅 GitHub Release 通知**，及时跟进更新
3. **准备备用方案**（官方 Gemini API 免费额度也不少）
4. **不要作为唯一 AI 接入方式**
5. **不适合生产/商业环境**，适合个人实验和个人助手
6. **安全优先选 Sophomoresty/gemini-web2api**（单文件零依赖）
7. **功能优先选 HanaokaYuzu/Gemini-API**（最成熟功能最全）

## 风险与限制

1. **稳定性**: Google 随时可能更新网页接口导致逆向失效
2. **Cookie 过期**: 需定期刷新 Cookie（1-7天），但 Gemini-API 有自动刷新
3. **ToS 风险**: 可能违反 Google 服务条款，有封号可能
4. **速率限制**: 网页版有自己的限速，不等于无限调用
5. **不适合生产**: 仅适合个人开发/测试/白嫖
6. **安全风险**: 选代码量小的项目（如 gemini-web2api）更容易审查

## 相关搜索关键词

```
GitHub Gemini web API reverse
Gemini web to API proxy
Gemini cookie API
free Gemini API no key
gemini-webapi
```
