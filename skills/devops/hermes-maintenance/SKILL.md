---
name: hermes-maintenance
description: Hermes Agent 配置维护 — SOUL.md人格管理、工作规范更新、Profile/Alias清理、Dashboard识别、版本更新、GitHub仓库维护。冰哥的Hermes环境日常维护指南。
version: 1.0
triggers:
  - SOUL.md / 人格 / 灵魂文件
  - 工作规范 / 莉莉丝的工作规范
  - Profile / 配置 / Alias / 别名
  - Dashboard / web工具 / 网页界面
  - hermes update / 版本更新
  - hermes doctor / 诊断
  - config.yaml / 配置文件
  - GitHub 仓库 / 仓库状态 / 批量更新 / 上游分歧
---

# Hermes 配置维护 (Hermes Maintenance)

## 核心原则
- **改配置前先问冰哥**（安全底线，memory中已有记录）
- **小问题直接patch**，不走看板
- **改完重启gateway**让配置生效
- **知识库 vs Skill区分**：知识库（knowledge）存具体操作经验/工具使用记录；Skill存可复用的工作流程/模式。API key写入方法等一次性操作经验放知识库，不放skill。

## 一、SOUL.md 人格管理

### 文件位置
- 默认profile：`~/.hermes/SOUL.md`
- 其他profile：`~/.hermes/profiles/<name>/SOUL.md`

### 当前人格架构
莉莉丝是默认人格，其他profile有各自人格定义：
- **莉莉丝**（default）：温柔可爱、情感丰富、记忆智能、像真人助手
- **大莉D**（dalid）：简洁客观、代码审查/技术方案
- **大莉M**（dalim）：简洁客观、长文分析/一致性检查
- **莉莉**（lili）：简洁客观、审核者
- **闪莉**（shanli）：严格执行、看板任务

### 更新SOUL.md流程
1. 读取当前SOUL.md
2. 与冰哥确认修改方向
3. 写入新内容
4. 重启gateway：`hermes gateway restart`

### 人格与技能的关系
- SOUL.md 定义**人格特质**（风格、情感、行为模式）
- 工作规范定义**工作流程**（审核、分段、校验）
- 技能定义**具体操作**（写作、审核、搜索）
- 三者互补，不重复

## 二、工作规范更新

### 文件位置
- `~/.hermes/莉莉丝的工作规范.md`

### 常见更新模式
1. **模型引用过时** — 决策树中的模型名可能过期（如 LongCat → mimo-v2.5）
2. **流程缺失** — 如遗漏了记忆知识库查阅步骤
3. **任务变更** — 定时任务增删改

### 更新后必须
- 重启gateway让新规范生效
- 验证修改没有引入矛盾

## 三、Profile / Alias 管理

### 查看profile状态
```bash
hermes doctor  # 检查profile和alias状态
hermes profile list  # 列出所有profile
```

### 清理孤立Alias
当 `hermes profile alias <name> --remove` 报错 "Profile does not exist" 时：
```bash
# 手动删除 ~/.local/bin/ 下的alias脚本
ls ~/.local/bin/ | grep -i "<alias_name>"
rm ~/.local/bin/<alias_name>
```

### 创建新Profile（推荐方法）

```bash
# 1. 从default克隆（推荐，自动注册profile + 创建wrapper脚本）
hermes profile create <name> --clone --description "描述"

# 2. 修改模型配置
python3 -c "
import yaml
with open(os.path.expanduser('~/.hermes/profiles/<name>/config.yaml')) as f:
    cfg = yaml.safe_load(f)
cfg['model'] = {'default': '<model-name>', 'provider': '<provider-name>'}
with open(os.path.expanduser('~/.hermes/profiles/<name>/config.yaml'), 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
"

# 3. 验证
hermes profile list  # 确认新profile出现
head -5 ~/.hermes/profiles/<name>/config.yaml  # 确认model配置正确
```

**⚠️ 不要用手动mkdir方式创建profile** — 只创建目录+写config.yaml不会注册profile，`hermes profile list`看不到。

### 修改现有Profile的模型

```bash
# 直接修改config.yaml中的model块
python3 -c "
import yaml, os
path = os.path.expanduser('~/.hermes/profiles/<name>/config.yaml')
with open(path) as f:
    cfg = yaml.safe_load(f)
cfg['model']['default'] = '<new-model>'
cfg['model']['provider'] = '<new-provider>'
with open(path, 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
"
```

#### Pitfalls
- **不要遗漏providers块** — 新模型的provider必须在providers中有完整配置（base_url, api_key/key_env, default_model, models列表）
- **验证脚本用临时文件** — 写入 /var/folders/.../T/hermes-verify-XXXXXX.py，执行后立即清理
- **SOUL.md需单独创建** — 复制config.yaml不会自动带SOUL.md，如需自定义人格要单独写入
- **⚠️ Profile名称不能包含点号** — `hermes profile create` 要求名称匹配 `[a-z0-9][a-z0-9_-]{0,63}`。`mimov2.5`会报错，正确写法是`mimo-v2-5`或`mimov25`。
- **⚠️ 只创建目录+config.yaml不够** — `~/.hermes/profiles/<name>/config.yaml` 存在不代表profile已注册。必须用 `hermes profile create --clone` 创建，否则 `hermes profile list` 看不到、`hermes -p <name>` 报错。
- **⚠️ delegate_task用的是delegation config，不是当前session模型** — delegation使用config.yaml中`delegation.key_env`指定的API key（默认AGNES_API_KEY），与当前session的model/provider无关。`delegate_dalim`切换的是模型选择器，但delegate_task仍用delegation config的API。如需用小米API的mimo-v2.5-pro执行任务，必须用`hermes -p mimo-v2-5 chat`方式，不能用delegate_task。

### Profile SOUL.md检查
检查各profile的SOUL.md是否与现有技能功能重复：
```bash
find ~/.hermes/profiles -name "SOUL.md" -type f
# 逐个读取检查
```

## 四、Dashboard / Web工具识别

### ⚠️ 冰哥说的"web工具"特指：
- **Hermes Dashboard**：端口 9119，启动命令 `hermes dashboard --port 9119 --no-open`
- **Hermes Workspace**：端口 3000，代码在 `/Users/libing/hermes-workspace/`，启动命令 `cd hermes-workspace && vite dev --host 127.0.0.1 --port 3000`

### 启动Dashboard
```bash
hermes dashboard --port 9119 --no-open  # 后台运行
hermes dashboard --port 8080  # ❌ 这不是冰哥要的
```

### 检查端口状态
```bash
lsof -i :9119  # Dashboard
lsof -i :3000  # Workspace
```

## 五、Desktop 桌面应用

### 启动流程
```bash
# 1. 安装主依赖（如已安装跳过）
cd /Users/libing/.hermes/hermes-agent && npm ci

# 2. 安装desktop依赖
cd /Users/libing/.hermes/hermes-agent/apps/desktop && npm ci

# 3. 启动桌面应用（首次会自动打包）
hermes desktop

# 4. 如果 --skip-build 失败，需先打包
cd apps/desktop && npm run pack
```

#
- Desktop连接的是**Gateway端口**（动态分配，如57064），不是Dashboard的9119
- 首次启动会自动打包，可能需要几分钟
- 如果连接超时，检查Gateway是否正常运行：`hermes gateway status`
- 网络问题可能导致Electron依赖下载失败，需开代理

## 六、版本更新

### 更新流程
```bash
hermes update  # 更新到最新版本
hermes gateway restart  # 重启gateway
hermes doctor  # 检查状态
```

### 更新后检查
- 版本号确认：`hermes --version`
- 配置版本：`hermes doctor` 查看是否有配置迁移提示
- 新功能：查看git log了解更新内容

## 七、MCP Server 多Agent配置

### 配置流程（2026-06-26 验证）

安装MCP Server并同时配置到Hermes + Claude Code + MiMo Code：

```bash
# 1. 安装MCP server（npm或pip）
npm install -g @brave/brave-search-mcp-server  # 或 pip install mem0-mcp-server

# 2. 创建Hermes MCP配置目录
mkdir -p ~/.hermes/mcp-servers/<name>

# 3. 写入config.json
cat > ~/.hermes/mcp-servers/<name>/config.json << 'EOF'
{
  "command": "npx",
  "args": ["-y", "tavily-mcp"],
  "env": {"API_KEY": "${API_KEY_FROM_ENV}"},
  "timeout": 30
}
EOF

# 4. 配置到Claude Code
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
with open(path) as f:
    cfg = json.load(f)
cfg['mcpServers']['<name>'] = {'command': '...', 'args': [...], 'env': {...}}
with open(path, 'w') as f:
    json.dump(cfg, f, indent=2)
"

# 5. 配置到MiMo Code
python3 -c "
import json
path = '~/.config/mimocode/mimocode.json'
# 同上
"
```

### 已配置的MCP Servers

| MCP Server | 用途 | 状态 |
|------------|------|------|
| chrome-devtools | Chrome浏览器控制 | ✅ |
| sqlite | SQLite数据库操作 | ✅ |
| prompt-optimizer | 提示词优化 | ✅ |
| mem0-local | 统一记忆层（本地Qdrant） | ✅ |
| tavily | 高质量搜索（已有API Key） | ✅ |
| ghidra-mcp | 逆向工程分析 | ✅（需先启动Ghidra） |

### Mem0本地MCP配置要点
- LLM: DeepSeek V4 Flash
- Embedding: sentence-transformers/all-MiniLM-L6-v2（本地，384维）
- 向量存储: Qdrant本地（/tmp/mem0_hermes）
- **必须显式设置`embedding_model_dims: 384`**，否则默认1536导致维度冲突
- Python 3.12（3.9不兼容）
- MCP Server脚本: `~/.hermes/mcp-servers/mem0-local/server.py`

### Pitfalls

1. **MCP配置目录不存在** — `~/.hermes/mcp-servers/<name>/` 需要先 `mkdir -p`，否则写入失败
2. **API Key在config.json中** — 直接写明文即可（MCP config不像.env那样被redact_secrets拦截）
3. **重启后生效** — Hermes MCP配置写入后需重启gateway；Claude Code/MiMo Code需重启各自进程

## 八、Gateway重启级联问题（2026-06-28发现）

### 症状
`hermes gateway restart` 会连带kill Dashboard(9119)和Workspace(3000)进程。

### 恢复流程
Gateway重启后必须立即重启Dashboard和Workspace：
```bash
# 1. 启动Dashboard
hermes dashboard --port 9119 --no-open &

# 2. 启动Workspace
cd /Users/libing/hermes-workspace && NODE_OPTIONS="--max-old-space-size=2048" node_modules/.bin/vite dev --host 127.0.0.1 --port 3000 &

# 3. 验证
sleep 5
curl -s -o /dev/null -w "%{http_code}" http://localhost:9119  # Dashboard
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000  # Workspace
curl -s -o /dev/null -w "%{http_code}" http://localhost:8642/health  # Gateway
```

### 桌面版连接
桌面版显示"Runtime not ready"或"网关离线"时，检查三个端口(8642/9119/3000)是否都200。

## 九、QQ Bot Adapter `is_reconnect` Bug（2026-06-28发现）

### 症状
Gateway日志反复报：
```
WARNING: Reconnect qqbot error: QQAdapter.connect() got an unexpected keyword argument 'is_reconnect', next retry in 300s
```

### 原因
Hermes v0.17.0的Gateway重连逻辑传了`is_reconnect`参数，但hermes-qqbot插件的`connect()`方法不支持此参数。

### 修复方法
给QQ adapter的`connect()`方法加上`is_reconnect`参数：
```bash
sed -i '' 's/async def connect(self) -> bool:/async def connect(self, *, is_reconnect: bool = False) -> bool:/' ~/.hermes/hermes-agent/gateway/platforms/qqbot/adapter.py
hermes gateway restart
```

### 状态
- ✅ 已修复（2026-06-28）
- 其他adapter（signal/webhook/yuanbao/api_server）已支持此参数，QQ adapter是唯一落后的

## 十、GitHub 仓库维护

### 冰哥的仓库结构
- **hermes-skills**（`~/.hermes/`）：自定义 skills 仓库，remote → `libing3854/hermes-skills.git`
- **hermes-agent**（`~/.hermes/hermes-agent/`）：Hermes 主代码库
  - `origin` → `NousResearch/hermes-agent.git`（上游）
  - `personal` → `libing3854/hermes-agent.git`（冰哥的 fork）

### 标准检查流程
```bash
# 列出所有仓库
gh repo list libing19950105 --limit 50 --json name,updatedAt,isPrivate,defaultBranchRef

# 检查本地状态
cd ~/.hermes && git status --short && git log --oneline -3
cd ~/.hermes/hermes-agent && git status --short && git log --oneline -3
```

### 批量提交工作流
1. **精确 add**：指定文件路径，不用 `git add .`
2. **描述性 commit**：`📝 更新skills: xxx, yyy` 或 `fix(module): description`
3. **推送到正确的 remote**：skills → `origin`，agent → `personal`

### 处理上游分歧
当本地分支和 `origin/main` 分歧过大时（如"1 and 2215 different commits"）：
```bash
git fetch origin
git rebase origin/main  # 或 git merge origin/main
# 解决冲突后
git push personal main
```

**详细工作流**：参见 `references/repo-status-check-workflow.md`

## Pitfalls

1. **不要混淆Dashboard端口** — 9119是冰哥要的，8080不是
2. **Gateway重启级联kill** — restart会带掉Dashboard和Workspace，必须一起重启（见第八节）
3. **QQ Bot `is_reconnect` bug** — v0.17.0的QQ adapter不支持此参数，已修复（见第九节）
4. **Python 3.9兼容性** — 现代包（crawl4ai/mem0ai/mcp等）需Python 3.12，详见 `references/python39-compatibility.md`
5. **GitHub 推送目标** — hermes-agent 的 `origin` 是上游（NousResearch），本地修改推到 `personal` fork
6. **大 diff 先同步** — 本地分支和上游分歧太大时，先 rebase/merge 再处理本地修改
