# 多Agent对照实验 & NV模型兼容性（2026-06-26 实测）

## 一、SOUL.md vs Skills 分工

原则：SOUL.md = 人格定义，Skills = 工作细则。

冰哥原话："这些应该写到一个技能里，只是灵魂文件的范围，这是工作细则"

| 内容类型 | 放哪里 | 示例 |
|---------|--------|------|
| 身份、角色、风格、原则 | SOUL.md | "你是审核者，简洁客观" |
| 审核维度、检查清单、修复流程 | 技能SKILL.md | "7项审核维度：字数/禁用词/..." |
| 具体工具用法、配置方法 | 技能SKILL.md | "用patch工具替换，不要用sed" |

## 二、对照实验工作流

### 必须隔离工作目录

三个agent共用同一目录会导致先完成的修改了文件，后面的读到已修改版本，无法公平对比。

```bash
mkdir -p _对照实验/{shanli,nvlinshi,agnes}
cp 第八卷_破晓之前/第*.md _对照实验/shanli/
cp 第八卷_破晓之前/第*.md _对照实验/nvlinshi/
cp 第八卷_破晓之前/第*.md _对照实验/agnes/

hermes kanban create "对照实验-闪莉" --assignee shanli \
  --workspace "dir:/path/_对照实验/shanli" ...
```

对比维度：完成度 / 正确性 / 遗漏 / 副作用 / 速度 / 协议遵守

## 三、Kanban Profiles 配置

问题：新profile在自己config里配了kanban profiles，但dispatch不识别。

根因：dispatch读取的是运行profile（default）的config.yaml中kanban.profiles列表。

解决：在default config中添加所有profiles：
```yaml
kanban:
  profiles: '["lili", "shanli", "nvlinshi", "shanli-agnes20flash"]'
```

## 四、NV模型kanban协议兼容性

| 模型 | kanban协议 | 任务完成 |
|------|-----------|---------|
| Qwen3.5 122B (NV) | ❌ 6次崩溃 | 文件有时被修改 |
| DeepSeek V4 Flash (NV) | ⚠️ 间歇性 | 简单任务能完成 |
| LongCat (shanli) | ✅ 正常 | ✅ |
| Agnes 2.0 Flash | ✅ 正常 | ✅ |

Workaround：SOUL.md+任务body双重提醒kanban协议；手动kanban complete收尾。

## 五、第八卷对照实验结果（2026-06-26 更新）

### 修改对照实验（grep替换类任务）

| 修改项 | 闪莉 | nvlinshi | agnes |
|--------|:----:|:--------:|:-----:|
| 爱琳娜→艾琳娜(388章) | ✅ 0处 | ❌ 20处 | ❌ 20处 |
| 维克拉多→维克多(422章) | ✅ 0处 | ❌ 2处 | ✅ 0处 |
| 希尔薇娅→西尔薇娅(387章) | ✅ 0处 | ❌ 6处 | ✅ 0处 |
| 艾琳→艾琳娜(428章) | ✅ 0处 | ❌ 2处 | ✅ 0处 |
| 处罝→处置(380章) | ✅ 0处 | ✅ 0处 | ✅ 0处 |
| 西区→城西(4章) | ❌ 4处 | ❌ 4处 | ✅ 0处 |
| **总完成率** | **4/5 (80%)** | **1/5 (20%)** | **5/5 (100%)** |

**结论：** agnes(5/5) > 闪莉(4/5) >> nvlinshi(1/5)

### 三路审核对比（50章全卷）

| 评分 | 莉莉 | 大莉M | 大莉D |
|------|:----:|:-----:|:-----:|
| 总分 | 90/100 | 90/100 | 7.5/10 |
| P0数 | 3处 | 2处 | 3处 |
| 最大发现 | 西区×3 | 角色名错误 | 388章身份冲突 |

**三路互补：** 不同模型擅长不同维度。大莉D最严格，抓到深层角色身份冲突。
