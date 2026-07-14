# 敏感信息检测与清理指南

## 快速检查（推荐）

使用自动化脚本检查敏感信息：

```bash
# 检查当前仓库
bash ~/.hermes/skills/devops/hermes-maintenance/scripts/check-sensitive.sh

# 检查指定目录
bash ~/.hermes/skills/devops/hermes-maintenance/scripts/check-sensitive.sh /path/to/repo
```

**脚本功能：**
- ✅ 自动检查 API Key、邮箱、密码、凭证等敏感信息
- ✅ 自动排除示例格式（如 `sk-XXX...XXXX`）
- ✅ 检查仓库可见性（公开仓库风险更高）
- ✅ 彩色输出，清晰显示问题位置

**脚本位置：** `~/.hermes/skills/devops/hermes-maintenance/scripts/check-sensitive.sh`

如果脚本报告发现问题，按下面的流程清理。

---

## 手动检查流程

### 触发场景
- GitHub Secret Scanning 阻止推送
- 冰哥要求检查仓库是否有泄露
- 定期安全审计
- 推送前主动扫描（公开仓库必须做）

## 第一步：检查仓库可见性

```bash
gh repo view <owner/repo> --json isPrivate,visibility
```

⚠️ 公开仓库的泄露比私有仓库严重得多。即使是私有仓库，密码也不应该放在代码里。

## 检测模式

### 1. API Key / Token 模式
```bash
git grep -n "ghp_[A-Za-z0-9]\{36\}\|sk-[A-Za-z0-9]\{20,\}\|as_sk_[A-Za-z0-9]\{20,\}\|tp-[A-Za-z0-9]\{20,\}" -- '*.md' '*.json' '*.yaml' '*.yml' '*.py' '*.js'
```

### 2. 邮箱地址
```bash
git grep -n "libing19950105@gmail.com\|541812906@qq.com" -- '*.md'
```

### 3. 密码 / 凭证
```bash
git grep -n "1472291855" -- '*.md' '*.json' '*.yaml' '*.yml'
```

### 4. 用户名 + 密码组合
```bash
# SMB 格式 user%password
git grep -n "541812906%1472291855" -- '*.md'
```

### 5. 环境变量名（通常安全）
```bash
git grep -n "XIAOMI_API_KEY\|DEEPSEEK_API_KEY" -- '*.md'
```
⚠️ 这些通常是文档中的配置说明，不是泄露。但需确认值是 `***` 或 `[REDACTED]`。

## 清理流程

### Step 1: 定位问题文件
```bash
cd ~/.hermes
git grep -l "<敏感信息>" -- '*.md' '*.json' '*.yaml' '*.yml' '*.py' '*.js'
```

### Step 2: 批量替换（工作目录）
```bash
# 用 sed 替换所有匹配的文件
for f in $(git grep -l "<敏感信息>" -- '*.md'); do
  sed -i '' 's/<敏感信息>/[REDACTED]/g' "$f"
done
```

### Step 3: 提交修复
```bash
git add <修改的文件>
git commit -m "🔒 fix: remove sensitive credentials"
```

### Step 4: 清理 git 历史（关键！）

**两种场景，用不同的 filter：**

#### 场景 A：整个文件需要移除
```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch <problem-file>' \
  --prune-empty --tag-name-filter cat -- --all
```

#### 场景 B：文件中的部分内容需要替换（密码、邮箱嵌在文档中）
```bash
# ⚠️ 必须用 --tree-filter（不是 --index-filter），这样才能修改文件内容
# ⚠️ 如果有未提交的更改，先 git stash
cd ~/.hermes && git stash

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force \
  --tree-filter 'find . -type f -name "*.md" -print0 | xargs -0 sed -i "" "s/1472291855/[REDACTED]/g; s/541812906@qq.com/[REDACTED]/g"' \
  --prune-empty --tag-name-filter cat -- --all

# 验证历史中已无敏感信息
git log --all -p -- '*.md' | grep -c "<敏感信息>"

# 强制推送
git push origin main --force
```

⚠️ `--index-filter` 只能移除文件，不能修改文件内容。要替换文件内的密码/邮箱，必须用 `--tree-filter`。
⚠️ `tree-filter` 会 checkout 每个 commit 到临时目录，比 `index-filter` 慢很多但能做内容替换。
⚠️ 多个替换模式用分号分隔：`s/pattern1/replacement/g; s/pattern2/replacement/g`

## 冰哥的敏感信息清单

| 类型 | 示例 | 替换为 |
|------|------|--------|
| Z-Library 主号邮箱 | libing19950105@gmail.com | [REDACTED] |
| Z-Library 备用邮箱 | 541812906@qq.com | [REDACTED] |
| QQ号 / SMB用户名 | 541812906 | [REDACTED] |
| 通用密码 | 1472291855 | [REDACTED] |
| GitHub Token | ghp_xxxx | ghp_xx... |
| API Key 示例 | sk-XXX...XXXX | 保留（安全示例） |

## Pitfalls

1. **邮箱也是敏感信息** — 不仅是 API key，邮箱地址也需要替换
2. **用户名+密码组合** — SMB 共享格式 `user%password` 也需要清理
3. **sed 替换会修改所有匹配** — 确认替换不会破坏文档结构
4. **filter-branch 耗时** — commit 越多越慢，完成后必须 `--force` 推送
5. **替换后验证** — `git grep` 再跑一遍确认没有遗漏
6. **检查仓库可见性** — 公开仓库泄露更严重，即使后来改了密码，git历史中的旧密码仍可能被利用
7. **tree-filter 比 index-filter 慢** — tree-filter 会 checkout 每个 commit，适合内容替换；index-filter 只操作索引，适合文件移除
8. **stash 未提交更改** — filter-branch 要求工作目录干净，有未提交更改会报错
9. **敏感信息不止 API key** — 邮箱、QQ号、SMB密码、Z-Library密码、内网IP都是敏感信息
10. **修改密码后仍需清理历史** — 即使当前文件已修复，git 历史中仍有旧密码，必须用 filter-branch 清理
