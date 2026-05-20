# rf-string / f-string JS 花括号转义指南

> 2026-05-19 创建
> 痛点：gen_v5.py 使用 `rf'''...'''` 模板嵌入 JavaScript，花括号转义导致频繁的 Python 编译错误

## 核心规则

在 Python `rf'''...'''` 字符串中：

| 目标输出 | Python 写法 | 说明 |
|---------|------------|------|
| `{` | `{{` | 所有 JS 花括号双写 |
| `}` | `}}` | 所有 JS 花括号双写 |
| `{variable}` | `{variable}` | Python 变量插值用单括号 |
| `{{key: value}}` | `{{{{key: value}}}}` | JS 对象字面量需要四层转义 |

## 常见错误模式

### 错误：忘记转义函数体花括号
```python
# ❌ 报错 f-string: invalid syntax
template = rf'''
<script>
k.forEach(function(x) {
  return x.c;
});
</script>'''
```

### 正确：双写花括号
```python
# ✅ 正确
template = rf'''
<script>
k.forEach(function(x) {{
  return x.c;
}});
</script>'''
```

## 转义矩阵

| JS 代码片段 | 在 rf 中应写成 | 正确性 |
|------------|---------------|:------:|
| `{` | `{{` | ✅ |
| `}` | `}}` | ✅ |
| `{a:1, b:2}` | `{{a:1, b:2}}` | ✅ |
| `function(x){return x;}` | `function(x){{return x;}}` | ✅ |
| `if(a){b}else{c}` | `if(a){{b}}else{{c}}` | ✅ |
| `try{a}catch(e){b}` | `try{{a}}catch(e){{b}}` | ✅ |
| `{{a}}` (JS 双花括号模板) | `{{{{a}}}}` | ✅ |
| `{Dstr}` (Python 变量) | `{Dstr}` | ✅ 保持单括号 |
| `{json.dumps(data)}` | `{json.dumps(data)}` | ✅ 保持单括号 |

## 验证方法

```bash
# 1. Python 编译检查（最快速）
python -c "
import py_compile
py_compile.compile('gen_v5.py', doraise=True)
print('✅ Python syntax OK!')
"

# 2. 生成 HTML 后检查生成的 JS 是否符合预期
grep -c '{{' output.html  # 应该为 0（所有 {{ 都已被展开）
grep -c '}}' output.html  # 应该为 0

# 3. 浏览器打开 HTML，检查控制台无 JS 错误
```

## 通用排查步骤

1. 修改后运行 `py_compile.compile(file, doraise=True)`
2. 如果报 `f-string: invalid syntax` → 找到报错行附近的花括号，确认是否漏了双写
3. 如果报错行看起来正确 → 检查前一行是否有未闭合的花括号
4. 如果 Python 语法通过但浏览器报 JS 错误 → 检查生成 HTML 中是否有残留的 `{{` 或 `}}`
5. 生成 HTML 中 `grep '{{'` 应该返回 0 结果

## 最佳实践

1. **不要**在 rf 模板中直接嵌入大段复杂 JS 逻辑
2. **推荐**：先用 `.py` 文件写好 JS 代码，再用 `.replace()` 注入到模板中
3. **推荐**：复杂 JS 逻辑先写成单独的 `.js` 文件，运行时读取并嵌入
4. **对比**：`rf'''...'''` vs `'''...'''.replace(...)` — 后者无转义问题，更易维护
