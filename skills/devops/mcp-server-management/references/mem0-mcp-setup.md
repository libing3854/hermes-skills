# Mem0 MCP Server — 本地自托管配置

## 背景
Mem0官方MCP Server（mem0-mcp-server）只支持云API（MemoryClient）。
我们用本地Memory类写了一个自托管版本。

## 依赖
```bash
python3.12 -m pip install --break-system-packages mem0ai sentence-transformers
```

## 配置要点
- LLM: DeepSeek V4 Flash（通过OpenAI兼容接口）
- Embedding: sentence-transformers/all-MiniLM-L6-v2（本地，384维）
- 向量存储: Qdrant本地
- **关键：`embedding_model_dims: 384`**（默认1536会报维度不匹配）

## 服务端文件
`~/.hermes/mcp-servers/mem0-local/server.py`

## 多平台配置
- Hermes: `~/.hermes/mcp-servers/mem0-local/config.json`
- Claude Code: `~/.claude/settings.json` → `mcpServers.mem0`
- MiMo Code: `~/.config/mimocode/mimocode.json` → `mcpServers.mem0`

## 工具列表
- `add_memory(content, user_id)` — 添加记忆
- `search_memories(query, user_id, limit)` — 语义搜索
- `get_all_memories(user_id)` — 获取全部
- `update_memory(memory_id, content)` — 更新
- `delete_memory(memory_id)` — 删除

## Mem0 v2 API变更（2026-06-28发现）

Mem0 v2.0+的`search()`和`get_all()`不再接受`user_id`作为顶层参数，改用`filters`：
```python
# ❌ 旧写法（v1.x）
results = m.search('查询', user_id='binge')
all_mem = m.get_all(user_id='binge')

# ✅ 新写法（v2.0+）
results = m.search('查询', filters={'user_id': 'binge'})
all_mem = m.get_all(filters={'user_id': 'binge'})
```

`add()`方法仍然直接接受`user_id`参数。

## 测试
```bash
python3.12 -c "
from mem0 import Memory
config = {
    'llm': {'provider': 'openai', 'config': {'model': 'deepseek-v4-flash', 'api_key': 'KEY', 'openai_base_url': 'https://api.deepseek.com/v1'}},
    'embedder': {'provider': 'huggingface', 'config': {'model': 'sentence-transformers/all-MiniLM-L6-v2'}},
    'vector_store': {'provider': 'qdrant', 'config': {'collection_name': 'mem0_hermes', 'embedding_model_dims': 384, 'path': '/tmp/mem0_hermes'}}
}
m = Memory.from_config(config)
r = m.add('测试', user_id='test')
print(r)
"
```
