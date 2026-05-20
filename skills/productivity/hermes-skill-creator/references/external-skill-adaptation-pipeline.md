# 外源技能适配流水线（CICD for Skills）

从 GitHub / Hub 等外部来源适配技能到 Hermes Agent 的完整流程。本会话中多次使用此流程，已验证可行。

---

## 流水线概览

```
1. 获取源码 → 2. 安全审查 → 3. verdict 决策 → 4. 适配 → 5. 验证 → 6. 交付
```

## Step 1: 获取源码

从 GitHub 拉取原始 SKILL.md 和所有关联文件：

```bash
# SKILL.md
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/main/path/to/SKILL.md"

# 检查目录结构
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/path/to/skill"
```

注意 symlink：有些仓库的 `scripts/` 和 `data/` 是 symlink，需要追到实际路径获取文件。

## Step 2: 安全 5 维度审查

| 维度 | 检查项 | 危险信号 |
|------|--------|----------|
| 🔐 来源可信度 | 发布者身份、stars、fork、社区收录 | 个人仓库无可信背书 |
| 🔍 代码内容 | 是否含 shell 注入、后门、数据外泄 | 执行外部命令、发网络请求 |
| 🛡️ 原则无意外 | 描述与实际行为是否一致 | 描述说 A 实际做 B |
| 📋 依赖风险 | npm/bun/npx/API Key/外部服务 | 需要对外部服务的 API Key |
| 🪪 许可检查 | MIT / Apache-2.0 | 无许可 / GPL / 不明来源 |

## Step 3: verdict 决策

| verdict | 含义 | 处理方式 |
|---------|------|----------|
| safe_to_use | 5 维度全通过 | 直接快速复用 |
| review_needed | 1-2 项有问题 | 完整适配 + 人工报告 |
| unsafe | 3+ 项有问题或已知 CVE | 跳过 |

**特别约定：**
- 有已知 CVE 漏洞的 → unsafe
- 使用逆向工程 API 的（如 danger- 前缀）→ unsafe
- 需要社交平台 API Key 的 → 标记 review_needed，询问用户是否需要
- 纯指令文件（无脚本无依赖）→ 通常 safe_to_use

## Step 4: 适配

### 4a: 创建目录结构

```
~/.hermes/skills/<category>/<name>/
├── SKILL.md
├── scripts/        (可选，安全脚本)
├── data/           (可选，知识库 CSV)
└── references/     (可选，参考文档)
```

### 4b: SKILL.md 格式转换

| 原平台（Claude Code） | Hermes Agent |
|----------------------|-------------|
| `claude -p "..."` | `delegate_task({goal: "..."})` |
| `imagegen` 工具 | `image_generate` 工具 |
| `.claude/skills/` 路径 | `~/.hermes/skills/<category>/<name>/` |
| 斜杠命令 `/xxx` | 自然语言触发 |
| Claude 内置技能引用（ai-artist 等） | 移除或替换为通用描述 |

### 4c: 排除不安全组件

检查 scripts/ 和 data/ 中的每个文件。如果有已知 CVE 或明确风险的脚本：

```python
# 排除规则示例
EXCLUDE = {
    "tailwind_config_gen.py": "CVE-2026-7595 代码注入",
    "generate-slide.py": "CVE-2026-7596 XSS",
}
```

### 4d: 复制安全脚本

纯 Python 标准库脚本通常可以直接复制。TypeScript/bun 脚本需要替代方案。

### 4e: 复制知识库数据

CSV、JSON、Markdown 等纯数据文件直接复制，无风险。

## Step 5: 验证

```bash
# 验证 SKILL.md 格式
python3 ~/.hermes/skills/productivity/hermes-skill-creator/scripts/quick_validate.py ~/.hermes/skills/<category>/<name>/

# 检查 Hermes 识别
hermes skills list | grep <name>
```

## Step 6: 交付

### 6a: 起中文名

在 SKILL.md 标题和 description 中加入中文名，风格参考：灵匠、寻技、美学工匠、设计百宝箱。

### 6b: 来源追溯

在 YAML 前端中添加 `metadata.source`，包含 commit 和 file_hash：

```yaml
source:
  name: original-skill-name
  repo: https://github.com/author/repo
  path: skills/<name>/SKILL.md
  commit: abcdef123456
  commit_date: "2026-05-14"
  file_hash: abc123...  # sha256sum of upstream SKILL.md
  adapted_by: Lily (Hermes Agent)
  adapted_at: "2026-05-14"
```

### 6c: 创建更新检查脚本

`scripts/check_upstream_updates.py` 内容：

```python
# 读取 SKILL.md 中的 source.commit
# 请求 GitHub API 获取最新 commit
# 比较 SHA，输出差异 URL
# 可选：--update 自动更新 metadata
```

参考灵匠的 `scripts/check_upstream_updates.py` 作为模板（去掉 --update 以外的大部分功能即可，约 60 行）。

### 6d: Git 初始化

```bash
cd ~/.hermes/skills/<category>/<name>/
git init
git config user.name "Lily"
git config user.email "lily@hermes.local"

# .gitignore
echo "__pycache__/" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "*.py[cod]" >> .gitignore
# 如果 data/ 下有生成脚本，也排除：
echo "data/_sync_all.py" >> .gitignore

git add -A
git commit -m "feat: <中文名> v0.1.0 初始提交"
git tag -a v0.1.0 -m "<中文名> v0.1.0 — 初始提交"
```

### 6e: 验证清单

- [ ] 中文名已在 title 和 description 中
- [ ] quick_validate.py 验证通过
- [ ] Hermes 识别为 enabled
- [ ] source 元数据完整（commit + file_hash + 路径）
- [ ] check_upstream_updates.py 已创建
- [ ] 排除的文件（有 CVE 的脚本）未包含
- [ ] .gitignore 配置正确（排除 __pycache__ 等）
- [ ] git tag 版本号与 SKILL.md version 一致

---

## 常见陷阱

1. **子代理超时**：大任务（SKILL.md 44KB+ / 多个文件 / 大量 CSV）可能超时（600s）。遇到超时不要重试，转为手动分步执行：先拉源码审查，再逐个写文件，最后验证。

2. **GitHub symlink**：仓库中的 `scripts/` 和 `data/` 可能是 symlink。`curl` 获取目录列表时见到的可能是 `{"target": "../real/path"}`，需要追踪到实际路径。

3. **Hub 安装技能不可修改 YAML 前端**：从 `hermes skills install` 安装的技能，SKILL.md 的 YAML 前端非常精简（只有 name/description/license）。不要试图添加 metadata.source 等字段，因为 Hub 更新可能会覆盖。改为在正文中添加来源注释。

4. **API Key 风险**：需要 API Key 的技能（post-to-wechat 等）必须明确标记，不可静默要求用户提供凭证。

5. **bun/TypeScript 脚本**：baoyu 系列的很多技能依赖 bun 运行 TypeScript 脚本。如果用户没有 bun 环境，这些脚本不可用。应内联替代方案或使用纯 Python 重写。
