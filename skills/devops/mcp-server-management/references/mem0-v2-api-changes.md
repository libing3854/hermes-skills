# Mem0 v2.0 API 变更速查

## search/get_all API变更

```python
# ❌ 旧版 (v0.x)
m.search('query', user_id='xxx')
m.get_all(user_id='xxx')
m.add('content', user_id='xxx')  # add没变

# ✅ 新版 (v2.0+)
m.search('query', filters={'user_id': 'xxx'})
m.get_all(filters={'user_id': 'xxx'})
m.add('content', user_id='xxx')  # add仍然是直接传参
```

## OpenAI LLM配置参数名

```python
# ❌ 错误
'config': {'model': '...', 'api_key': '...', 'base_url': '...'}

# ✅ 正确
'config': {'model': '...', 'api_key': '...', 'openai_base_url': '...'}
```

## 默认embedding维度

| Provider | 默认维度 |
|----------|---------|
| OpenAI | 1536 |
| HuggingFace (all-MiniLM-L6-v2) | 384 |

使用非OpenAI embedding时，必须在vector_store.config中显式设置正确的`embedding_model_dims`。
