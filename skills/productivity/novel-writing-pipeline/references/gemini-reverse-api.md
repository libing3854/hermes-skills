# Gemini 逆向 API 项目汇总

## 项目对比（2026-06-17 调研）

| 项目 | Stars | 特点 | 安全性 | 推荐度 |
|------|-------|------|--------|--------|
| HanaokaYuzu/Gemini-API | 3.2k | Python异步库，功能最全 | ★★★★☆ | 长期使用 |
| Sophomoresty/gemini-web2api | 1.8k | 单文件零依赖，OpenAI兼容 | ★★★★★ | 快速搭建 |
| Amm1rr/WebAI-to-API | 1.3k | FastAPI，多后端 | ★★★☆☆ | 不推荐 |

## gemini-web2api 详解（已验证）

### 匿名模式（白嫖）
- 走 Gemini 公开 StreamGenerate 端点，不需要登录
- 实际都是 Flash 级别（即使请求 Pro 也会降级）
- 不消耗 Pro 额度，网站不显示用量
- 风险：Google 随时可能关闭匿名端点

### Pro 模式（需要 cookie）
- 从 Chrome 提取 `__Secure-1PSID` 和 `__Secure-1PSIDTS`
- 保存到 cookie 文件，config.json 配置 `cookie_file`
- cookie 会过期，需要定期更新

### 可用模型
| 模型 | 输出上限 | 需要认证 |
|------|---------|---------|
| gemini-3.5-flash | ~1.2万字 | 否 |
| gemini-3.5-flash-thinking | ~2万字 | 否 |
| gemini-3.1-pro | ~1.2万字 | 是（否则降级Flash） |
| gemini-flash-lite | ~1万字 | 否 |

### 搭建步骤
```bash
cd /tmp && git clone --depth 1 https://github.com/Sophomoresty/gemini-web2api.git
cd gemini-web2api && python3.12 -m venv gemini-env && source gemini-env/bin/activate
pip install httpx
# 创建 config.json（见下方模板）
python3 gemini_web2api.py  # 启动在 localhost:8081
```

### config.json 模板
```json
{
  "port": 8081,
  "host": "0.0.0.0",
  "default_model": "gemini-3.5-flash",
  "api_keys": [],
  "cookie_file": null,
  "log_requests": true
}
```

## HanaokaYuzu/Gemini-API 详解（大莉M审查结论）

### 安全性
- Cookie 仅发往 Google 官方域名，无数据外泄
- 依赖链可信（curl-cffi, loguru, orjson, pydantic）
- 配了 Dependabot 自动更新

### 稳定性风险
- 单人维护，但社区有贡献
- Google 反制风险高（逆向 API 天然脆弱）
- 建议用独立 Google 账号，不要用主力号

### 使用方式
```bash
pip install gemini_webapi
```
```python
from gemini_webapi import GeminiClient
client = GeminiClient(PSID, PSIDTS)
await client.init()
response = await client.generate_content("Hello")
```

## Chrome DevTools MCP 注意事项

### 限制
- MCP 连接的是**无头 Chrome**（headless），不是用户桌面 Chrome
- 无法直接操控用户已登录的浏览器
- Cookie 注入可能被 Google 安全机制拦截

### AppleScript 操控桌面 Chrome
- 需要先启用：Chrome → 显示 → 开发者 → 允许 Apple 事件中的 JavaScript
- 启用后需要重启 Chrome
- 可以用 `keystroke` 打字，但准确性有限
- 不如直接用 API 方式可靠
