# Tool Handler 签名陷阱 — 实测案例

## 背景

2026-05-27 插件全面测试中发现两个插件的 tool handler 签名有问题，导致调用时报 TypeError。

## 案例 1：model-selector — 缺 **kwargs

### 错误现象

```
Tool execution failed: TypeError: _handle_model_select() got an unexpected keyword argument 'task_id'
```

### 出错的 handler 签名

```python
def _handle_model_select(task: str, session_id: str = "",
                          hint_category: str = "", report_failure: bool = False) -> str:
```

### 根因

Hermes 工具框架在调用 tool handler 时，除了 schema 中定义的参数外，还传了额外的 `task_id` 关键字参数。handler 没有用 `**kwargs` 吸收它。

### 修复

```python
def _handle_model_select(task: str, session_id: str = "",
                          hint_category: str = "", report_failure: bool = False,
                          **kwargs) -> str:
```

## 案例 2：delegate-duo — **_** 无法吸收位置参数

### 错误现象

```
Tool execution failed: TypeError: _handle_dalim() takes 0 positional arguments but 1 was given
```

### 出错的 handler 签名

```python
def _handle_dalim(**_) -> str:
```

### 根因

该工具的 schema 定义为空参数（`"properties": {}`），框架仍然传了一个位置参数给 handler。`**_**` 只能吸收关键字参数，不能吸收位置参数。

### 修复

```python
def _handle_dalim(*args, **_) -> str:
```

## 教训

1. **所有 tool handler 签名末尾加 `**kwargs`** — 防止框架传入意外关键字参数
2. **空参数工具另加 `*args`** — 防止框架传入位置参数
3. 插件代码修改后必须 `/reset` 或重启 Hermes 才能生效
4. `hermes plugins list` 只显示注册状态，不意味着 handler 能正常被调用——必须实际调用测试
