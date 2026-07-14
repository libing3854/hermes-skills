# LongCat 大模型（美团）

## 当前状态（2026-06-30）

### 可用模型
| 模型名 | 类型 | 说明 |
|--------|------|------|
| `LongCat-2.0` | 正式版 | 万亿参数，1M上下文，原生工具调用，深度适配 Claude Code/Hermes |
| `LongCat-2.0-Preview` | 内测版 | 限量开放，每日09:00和21:00(UTC+8)放名额 |

### 已下线模型（2026-05-29起停服）
- ❌ LongCat-Flash-Chat
- ❌ LongCat-Flash-Thinking
- ❌ LongCat-Flash-Thinking-2601
- ❌ LongCat-Flash-Lite
- ❌ LongCat-Flash-Omni-2603
- ❌ LongCat-Flash-Chat-2602-Exp

## API 信息
- **Base URL**: `https://longcat.chat/v1`（需确认实际端点）
- **兼容格式**: OpenAI Chat Completions
- **文档**: https://longcat.chat/platform/docs/zh

## 计费方式（2026-06-30新增）
1. **Token 资源包** — 一次性购买固定额度，30天有效
2. **API 按量计费** — 先充值后扣费

## 配置示例
```yaml
custom_providers:
- base_url: https://longcat.chat/v1
  key_env: LONGCAT_API_KEY
  model: LongCat-2.0
  name: LongCat 2.0
```

## 注意事项
- LongCat-2.0 深度适配 Agent 工具调用场景
- 免费额度每日限量，用完即止
- 旧模型名称全部不可用，必须迁移到 LongCat-2.0

## 更新日志
- **2026-06-30**: LongCat-2.0 正式发布，推出计费服务
- **2026-05-29**: 6个老模型下线，集中资源到 LongCat-2.0-Preview
- **2026-04-20**: LongCat-2.0-Preview 发布
