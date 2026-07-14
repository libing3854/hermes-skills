# delegate_task 模型选择调试记录（2026-07-01）

## 问题现象

批量下载Z-Library书籍时，子代理连续返回 `HTTP 402: Insufficient Balance` 错误。

## 时间线

| 时间 | 事件 | 使用模型 | 状态 |
|------|------|----------|------|
| 00:19 | 子代理调用 | deepseek-v4-pro | ❌ 失败 |
| 10:16 | 子代理调用 | deepseek-v4-pro | ❌ 失败 |
| 11:34 | 子代理调用 | deepseek-v4-pro | ❌ 失败 |
| 11:49 | 配置修改为 xiaomi/mimo-v2.5 | - | 配置文件已更新 |
| 11:49之后 | 子代理调用 | deepseek-v4-pro | ❌ 仍然失败 |
| 11:55 | 子代理调用 | mimo-v2.5-pro | ✅ 成功 |

## 根因分析

### 1. delegate_task 不使用 delegation 配置
- delegation 配置（provider/model/key_env）只影响其他场景
- delegate_task 必须显式传入 `model` 参数
- 不传 model = 使用当前会话的默认模型（deepseek-v4-pro）

### 2. Gateway 配置不会自动重载
- 修改 config.yaml 后必须 `hermes gateway restart`
- Gateway 使用缓存的配置，不是文件中的配置
- 11:49 修改配置 → 11:55 重启 Gateway → 配置生效

### 3. 盲目重试导致循环
- 子代理失败后立即派出新子代理
- 没有检查失败原因
- 每次失败都消耗 token（即使 HTTP 402）

## 正确做法

### delegate_task 调用
```python
# ❌ 错误 - 不指定 model
delegate_task(goal="下载书籍", toolsets=["browser", "terminal"])

# ✅ 正确 - 显式指定免费模型
delegate_task(tasks=[{
    "goal": "下载书籍",
    "model": {"model": "agnes-2.0-flash"},
    "toolsets": ["browser", "terminal"]
}])
```

### 配置修改后
```bash
# 1. 修改配置
hermes config set delegation.provider agnes-2.0-flash
hermes config set delegation.model agnes-2.0-flash

# 2. 重启 Gateway（必须！）
hermes gateway restart

# 3. 确认配置生效
cat ~/.hermes/config.yaml | grep -A 10 "^delegation:"
```

### 遇到失败时
1. 检查日志中的 `model=` 参数
2. 检查对应 provider 的 API key 余额
3. 不要盲目重试——先诊断根因
4. 冰哥说"停"= 立即停止所有操作

## 成本影响

- 671 次 deepseek-v4-pro 调用
- 5575 万 tokens
- **¥112**

## 教训

1. **delegate_task 必须显式指定 model 参数**
2. **修改配置后必须重启 Gateway**
3. **遇到失败要先检查原因，不要盲目重试**
4. **冰哥说"停"= 立即停止**
