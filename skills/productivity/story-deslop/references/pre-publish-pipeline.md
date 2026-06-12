# 小说预发布 QA 检查清单

## 完整流水线

### Step 1：大莉剧情审查
```
delegate_task(
  goal="深度审查第X卷全文剧情连贯性和bug",
  toolsets=["terminal","file"]
)
```
检查项：剧情连贯性、角色一致性、设定逻辑、明确bug、可疑项

### Step 2：闪莉修复
```
delegate_task(
  goal="修复第X卷剧情bug，参考大莉审查报告",
  toolsets=["terminal","file"]
)
```
注意：闪莉修bug时不同时做去AI味，两步分开

### Step 3：闪莉去AI味（story-deslop）
```
delegate_task(
  goal="第X卷全文去AI味处理，按story-deslop原则",
  toolsets=["terminal","file"]
)
```
- 禁用词替换（微微/轻轻/缓缓/一丝等）
- 结尾去升华
- 心理描写外化
- 对话去腔调
- 比喻堆砌打散

### Step 4：逐章检查错别字+AI味
每章发布前单独检查：
```
delegate_task(
  goal="检查第XXX章的错别字和AI味，直接修复",
  toolsets=["terminal","file"]
)
```

### Step 5：发布到番茄
```bash
node ~/.hermes/skills/fanqie-publisher/scripts/publish_fanqie.js \
  --file "/path/to/第XXX章_标题.md" \
  --mode immediate \
  --confirm-publish
```

## 性能参考
- 大莉审查45章：约5分钟
- 闪莉修复bug：约5分钟
- 闪莉去AI味45章：约6分钟
- 逐章检查错别字+AI味：约2-3分钟/章
