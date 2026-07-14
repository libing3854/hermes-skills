# GitHub Monorepo 推送工作流

将新创建的技能推送到 `libing3854/hermes-skills` 仓库的完整步骤，以及更新已有技能的方法。

## 背景

冰哥的所有技能统一放在一个 GitHub 仓库中：
- **仓库**: `libing3854/hermes-skills`
- **结构**: `skills/<category>/<skill-name>/`
- **Token 认证**: HTTPS URL 嵌入 Token（Token 缺 `read:org` 时不能用 `gh CLI`）

## 前置条件

- GitHub Token 已配置（ghp_...，60天有效期）
- 技能已创建并 `git init` 本地版本管理

## Step 1: 克隆仓库

```bash
cd /tmp
rm -rf hermes-skills 2>/dev/null
git clone https://<username>:<token>@github.com/libing3854/hermes-skills.git
cd hermes-skills
git config user.name "李冰"
git config user.email "libing@users.noreply.github.com"
```

> ⚠️ **CWD 陷阱**：后续步骤中如果删除 `/tmp/hermes-skills`，shell 的 CWD 会变成失效路径。解决方法：在 `execute_code()` 中运行，或在每条命令前加 `cd ~ &&`。

## Step 2: 复制技能到仓库

### 首次推送新技能

```bash
mkdir -p skills/<category>/<skill-name>
cp -r ~/.hermes/skills/<category>/<skill-name>/* skills/<category>/<skill-name>/
rm -rf skills/<category>/<skill-name>/.git   # 移除本地 git
```

### 更新已有技能

```bash
# 只复制改过的文件
cp ~/.hermes/skills/<category>/<skill-name>/SKILL.md skills/<category>/<skill-name>/SKILL.md

# 或整体同步（自动处理新增/修改/删除）
rsync -a --exclude='.git' ~/.hermes/skills/<category>/<skill-name>/ skills/<category>/<skill-name>/

# 删除文件需手动 rm
rm -f skills/<category>/<skill-name>/references/<old-file>.md
```

## Step 3: 提交并推送

```bash
git add -A
git commit -m "feat(<skill-name>): <描述>"
git push origin main
```

**Commit message 风格：**
| 场景 | 格式 |
|------|------|
| 首次添加 | `feat: add <skill-name> v<version> — <描述>` |
| 修改已有技能 | `feat(<skill-name>): <描述>` |
| 回滚 | `revert(<skill-name>): <描述>` |

## Step 4: 验证并清理

```bash
cd ~  # 先切出 /tmp，避免删除后 CWD 失效
rm -rf /tmp/hermes-skills
```

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| Token 缺 `read:org` | 不用 gh CLI，`git push` 直连 |
| Token 过期 | 重新生成 ghp_... |
| `git push` 被拒绝（non-fast-forward） | `git pull --rebase origin main` 后再推 |
| `pwd: error retrieving current directory` | `cd ~` 重置，或在 `execute_code()` 中运行 |
| `cp -r` 文件嵌套 | 用 `rsync -a --exclude='.git'` 替代 |
| 子代理无法写文件 | 在 goal 中加 `toolsets=['terminal','file']` |
