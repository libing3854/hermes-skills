# Mem0 本地部署指南

## 安装依赖（Python 3.12必须）

```bash
# Python 3.9不兼容（X|None语法）
python3.12 -m pip install --break-system-packages mem0ai sentence-transformers
```

## 关键配置

```python
config = {
    'llm': {
        'provider': 'openai',
        'config': {
            'model': 'deepseek-v4-flash',
            'api_key': '<从.env读取>',
            'openai_base_url': 'https://api.deepseek.com/v1'  # 注意是openai_base_url不是base_url
        }
    },
    'embedder': {
        'provider': 'huggingface',
        'config': {'model': 'sentence-transformers/all-MiniLM-L6-v2'}
    },
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'collection_name': 'mem0_hermes',
            'embedding_model_dims': 384,  # 必须！默认1536会维度冲突
            'path': '/tmp/mem0_hermes'
        }
    }
}
```

## 坑

1. **embedding_model_dims必须设为384** — HuggingFace all-MiniLM-L6-v2输出384维，Qdrant默认1536（OpenAI），不设会报`shapes (0,1536) and (384,) not aligned`
2. **openai_base_url不是base_url** — Mem0 v0.1.x的OpenAIConfig用`openai_base_url`参数
3. **search API变了** — v2.0用`filters={'user_id': '...'}`而不是`user_id='...'`
4. **旧数据冲突** — 换embedding模型后必须删旧collection（`rm -rf /tmp/mem0_hermes`）
5. **PostHog超时** — Mem0会连us.i.posthog.com做遥测，国内可能超时，不影响功能
6. **spaCy/fastembed警告** — 可忽略，BM25关键词搜索不可用但语义搜索正常
