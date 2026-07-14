# Mem0 本地MCP Server 完整配置

## 依赖安装（Python 3.12）

```bash
# 安装Mem0和embedding模型
python3.12 -m pip install --break-system-packages mem0ai sentence-transformers

# sentence-transformers依赖torch（~2GB），首次安装较慢
# 如果安装超时，手动在终端运行：
python3.12 -m pip install --break-system-packages sentence-transformers
```

## 配置参数

```python
config = {
    'llm': {
        'provider': 'openai',
        'config': {
            'model': 'deepseek-v4-flash',
            'api_key': '<DEEPSEEK_API_KEY>',
            'openai_base_url': 'https://api.deepseek.com/v1'  # 注意参数名
        }
    },
    'embedder': {
        'provider': 'huggingface',
        'config': {
            'model': 'sentence-transformers/all-MiniLM-L6-v2'
        }
    },
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'collection_name': 'mem0_hermes',
            'embedding_model_dims': 384,  # 必须！默认1536会报错
            'path': '/tmp/mem0_hermes'
        }
    }
}
```

## MCP Server脚本

位置：`~/.hermes/mcp-servers/mem0-local/server.py`

使用FastMCP + stdio传输，暴露5个工具：
- `add_memory(content, user_id)` — 添加记忆
- `search_memories(query, user_id, limit)` — 语义搜索
- `get_all_memories(user_id)` — 获取所有
- `update_memory(memory_id, content)` — 更新
- `delete_memory(memory_id)` — 删除

## 多平台配置

已配置到：
- Hermes: `~/.hermes/mcp-servers/mem0-local/config.json`
- Claude Code: `~/.claude/settings.json` → mcpServers.mem0
- MiMo Code: `~/.config/mimocode/mimocode.json` → mcpServers.mem0

## 常见问题

### 1. 维度冲突 (shapes (0,1536) and (384,))
QdrantConfig默认1536维（OpenAI），HuggingFace输出384维。
解决：显式设置`embedding_model_dims: 384`

### 2. search API变更 (v2.0)
旧：`m.search('q', user_id='x')`
新：`m.search('q', filters={'user_id': 'x'})`

### 3. base_url参数名
Mem0 OpenAI LLM配置中，base_url参数名是`openai_base_url`，不是`base_url`

### 4. Python 3.9不兼容
mem0ai v2.0+和sentence-transformers需要Python 3.10+
