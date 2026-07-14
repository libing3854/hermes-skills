# API Key写入.env被截断

**发现时间：** 2026-06-26

## 症状

向`~/.hermes/.env`写入新API key时，key被自动截断为13字符（如`fc-d8c...8320`），导致API认证失败（UnauthorizedError）。

## 原因

Hermes v0.17.0的 `security.redact_secrets: true` 会识别并屏蔽所有疑似API key格式的输出和写入。Firecrawl的`fc-`前缀触发此机制。

## 解决方法（必须严格按顺序）

```bash
# 1. 临时关掉redact_secrets
hermes config set security.redact_secrets false

# 2. 写入key到.env
echo "API_KEY=*** >> ~/.hermes/.env

# 3. 恢复redact_secrets
hermes config set security.redact_secrets true

# 4. 重启gateway使配置生效
hermes gateway restart
```

## 注意事项

- 不能跳过任何一步
- 关闭后key才能完整写入
- 写入后必须恢复安全配置
- gateway重启后需要检查Dashboard(9119)和Workspace(3000)是否恢复
