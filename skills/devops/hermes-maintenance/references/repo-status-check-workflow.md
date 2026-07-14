# GitHub 仓库状态检查与批量更新工作流

## 冰哥的仓库结构

### hermes-skills 仓库
- **位置**：`~/.hermes/`（skills 子目录是 git 仓库的一部分）
- **远程**：`origin` → `https://github.com/libing3854/hermes-skills.git`
- **用途**：存储自定义 skills（productivity、devops 等分类）

### hermes-agent 仓库
- **位置**：`~/.hermes/hermes-agent/`
- **远程**：
  - `origin` → `https://github.com/NousResearch/hermes-agent.git`（上游）
  - `personal` → `https://github.com/libing3854/hermes-agent.git`（冰哥的 fork）
- **用途**：Hermes Agent 主代码库，包含 gateway、desktop 等

## 检查仓库状态的标准流程

```bash
# 1. 列出冰哥的所有仓库
gh repo list libing19950105 --limit 50 --json name,updatedAt,isPrivate,defaultBranchRef

# 2. 检查 hermes-skills 状态
cd ~/.hermes
git status --short          # 查看修改的文件
git log --oneline -3        # 最近提交
git remote -v               # 确认远程 URL

# 3. 检查 hermes-agent 状态
cd ~/.hermes/hermes-agent
git status --short
git log --oneline -3
git remote -v
```

## 批量提交与推送

### hermes-skills 更新流程

```bash
cd ~/.hermes

# 1. 添加修改的 skills 文件（不要添加 untracked 的配置/缓存文件）
git add skills/productivity/<skill-name>/SKILL.md
git add skills/devops/<skill-name>/SKILL.md

# 2. 提交
git commit -m "📝 更新skills: <skill1>, <skill2>, <skill3>"

# 3. 推送
git push origin main
```

### hermes-agent 更新流程

```bash
cd ~/.hermes/hermes-agent

# 1. 添加修改的文件
git add gateway/platforms/qqbot/adapter.py

# 2. 提交
git commit -m "fix(qqbot): add is_reconnect parameter to connect() method"

# 3. 推送到 personal fork（不要直接推到 origin/upstream）
git push personal main
```

## 处理上游分歧

### 症状
```
Your branch and 'origin/main' have diverged,
and have 1 and 2215 different commits each, respectively.
```

### 原因
本地分支落后上游太多（2215 个提交），或者本地有未推送的提交。

### 解决策略

**策略 A：Rebase（推荐，保持历史干净）**
```bash
git fetch origin
git rebase origin/main
# 解决冲突后
git push personal main
```

**策略 B：Merge（保留本地提交历史）**
```bash
git fetch origin
git merge origin/main
# 解决冲突后
git push personal main
```

**策略 C：强制推送个人 fork（谨慎使用）**
```bash
# 只在确认 personal fork 是最新的本地版本时使用
git push personal main --force
```

## 识别构建产物 vs 源代码

### 大文件变更检查

当看到类似 `17788 ++++++++++++++++++++++++-----------` 的大 diff 时：

```bash
# 1. 检查文件类型
file apps/desktop/electron/main.cjs

# 2. 检查 git 历史
git log --oneline apps/desktop/electron/main.cjs | head -5

# 3. 检查 .gitignore
cat .gitignore | grep -i "main.cjs\|electron\|dist\|build"
```

### 判断标准

| 特征 | 源代码 | 构建产物 |
|------|--------|----------|
| git 历史 | 有多个有意义的提交 | 无历史或只有"build: update"类提交 |
| 文件内容 | 可读的源码 | 打包/压缩后的代码 |
| .gitignore | 未被忽略 | 应该被忽略 |
| 变更模式 | 小范围逻辑修改 | 大范围重新生成 |

### 处理建议

- **源代码**：正常提交
- **构建产物**：
  1. 添加到 `.gitignore`
  2. `git rm --cached <file>` 从跟踪中移除
  3. 提交 `.gitignore` 变更

## Pitfalls

1. **不要推送未测试的代码到 origin** — hermes-agent 的 origin 是上游（NousResearch），推送前确认是推到 personal fork
2. **大 diff 需要先同步上游** — 本地分支和上游分歧太大时，先 rebase/merge 再处理本地修改
3. **构建产物不要提交** — `main.cjs`、`dist/`、`build/` 等通常是构建产物，检查 `.gitignore`
4. **untracked 文件太多时用精确 add** — 不要用 `git add .`，精确指定要提交的文件路径
5. **GitHub token 过期** — `gh auth login` 重新配置，详见 memory 中的"环境恢复教训"