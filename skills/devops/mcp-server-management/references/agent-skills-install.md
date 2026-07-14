# Agent Skills 安装方法

## npx skills add（Vercel标准）
Vercel Labs的skills.sh提供标准化的skill安装方式：

```bash
# 安装单个skill
npx skills add <owner>/<repo> --skill <name>

# 示例：安装Matt Pocock的teach skill
npx skills add mattpocock/skills --skill teach
```

## 已安装的Agent Skills

| Skill | 来源 | 路径 |
|-------|------|------|
| teach | mattpocock/skills | ~/.hermes/skills/productivity/teach/ |

## 手动安装（GitHub克隆）
```bash
# 克隆repo
git clone --depth 1 https://github.com/<owner>/<repo>.git /tmp/<repo>

# 复制SKILL.md到Hermes skills目录
mkdir -p ~/.hermes/skills/<category>/<skill-name>/
cp /tmp/<repo>/skills/<skill-name>/SKILL.md ~/.hermes/skills/<category>/<skill-name>/

# 复制关联文件（references/examples/scripts）
cp -r /tmp/<repo>/skills/<skill-name>/*.md ~/.hermes/skills/<category>/<skill-name>/
```

## Matt Pocock Skills（135.8K stars）
仓库：github.com/mattpocock/skills
- teach — 教学系统（跨session有状态）
- safe — 安全检查
- design-an-interface — 接口设计
- diagnose — 问题诊断
- tdd — 测试驱动开发
- 共29个skills

## Google Stitch Skills（6.1K stars）
仓库：github.com/google-labs-code/stitch-skills
- 主要是Stitch设计平台专用
- design-md我们已有（从这里来的）
- 格式参考价值 > 实用价值

## Skills.sh / SkillsMP
- skills.sh — Vercel的skills注册表
- skillsmp.com — 社区skills目录
- 可搜索安装命令和skill列表
