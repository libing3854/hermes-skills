# MiMo Code 配置错误调试记录

## 2026-06-13: ConfigInvalidError 修复

### 问题描述
MiMo Code 启动失败，日志显示 `ConfigInvalidError`。

### 根因
`~/.config/mimocode/mimocode.json` 被修改为错误格式：
```json
{
  "provider": {
    "agnes": {
      "models": {
        "agnes-2.0-flash": {
          "limit": {
            "context": 1000000
          }
        }
      }
    }
  },
  "model": {
    "default": "agnes-2.0-flash",
    "provider": "agnes"
  }
}
```

**错误点**: `model` 字段是对象，应该是字符串。

### 修复过程
1. 查看日志：`tail -20 ~/.local/share/mimocode/log/*.log`
2. 发现错误：`ERROR service=server error=ConfigInvalidError`
3. 定位配置：`~/.config/mimocode/mimocode.json`
4. 修复：重写为正确格式 `{"model": "mimo/mimo-auto"}`

### 关键日志行
```
ERROR 2026-06-13T11:09:28 +3ms service=config path=/Users/libing/.config/mimocode/mimocode.json loading
ERROR 2026-06-13T11:09:28 +3ms service=server error=ConfigInvalidError failed
```

### 教训
- MiMo Code 的 `model` 配置必须是字符串格式 `"provider/model"`
- 不能使用对象格式 `{"default": "...", "provider": "..."}`
- Agnes 模型不能直接在 MiMo Code 中使用
- 配置文件位置：`~/.config/mimocode/mimocode.json`（全局）
