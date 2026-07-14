---
name: novel-cover-design
description: >
  为小说设计AI生成封面。分析平台热门封面风格，生成多版本提示词，用Agnes生图2.0生成封面图片。
  覆盖：平台风格分析→多版本提示词生成→AI生图→封面目录管理的完整流程。
trigger:
  - 用户要求设计小说封面
  - 用户要求生成多个风格的封面
  - 用户提到"多封面推荐"、"封面设计"、"AI生图"
---

# 小说封面AI设计

## 前置条件

1. **Agnes AI生图**：已配置 `image_generate` 工具（agnes-image-2.0-flash）
2. **平台账号**：番茄小说等平台的作者后台访问权限
3. **封面存储目录**：`/Users/libing/Desktop/临时文件-0001/脑洞文/封面/`

## 核心工作流

### 1. 平台热门封面风格分析

用浏览器工具访问平台书库，分析热门封面的视觉特征：

```
步骤：
1. browser_navigate → 平台书库页面
2. browser_get_images → 获取封面图片URL列表
3. vision_analyze → 详细分析封面风格（构图、色调、人物、字体、氛围）
4. 总结：配色方案、构图方式、字体风格、人物立绘特点
```

**vision_analyze分析模板**：
```
分析这张番茄小说封面的风格特点：构图、色调、人物形象、文字排版、整体氛围。
这是[类型]类小说的封面。
```

**番茄小说热门封面风格总结（2026-07验证）：**

| 类型 | 色调 | 构图 | 字体 |
|------|------|------|------|
| 暗黑/悬疑/奇幻 | 暗色调（黑/深紫/深蓝）+ 高饱和亮色（红/橙/金） | 场景氛围型 或 人物+氛围型 | 扭曲/棱角分明的创意字体 |
| 女频古言/甜宠 | 明亮浅色系（浅粉/暖橙/青绿） | 柔和二次元立绘 | 圆润少女字体 |
| 仙侠/玄幻 | 水墨淡雅色调（灰蓝/淡墨） | 飘逸古风人物+写意场景 | 书法风格字体 |
| 女频古风世情 | 暖柔和谐色调（暖黄/浅橙/淡紫） | 分层意境构图 或 意象留白 | 书法字体/竖排手写体 |

### 2. 多版本封面提示词生成

根据小说类型，生成5-7个不同风格的提示词：

**提示词模板结构：**
```
[风格类型] novel cover, [核心视觉元素], [背景描述], [光效/氛围], [艺术风格], [技术参数], 2:3 aspect ratio, book cover design
```

**从现有封面中提取元素创作新提示词的方法：**
1. 分析热门封面的构图技巧（分层、留白、局部特写）
2. 提取色调方案（主色、点缀色、对比关系）
3. 借鉴意象符号（花卉、器物、建筑元素）
4. 融合到自己的小说主题中

**暗黑奇幻类常用元素：**
- 神秘人物：`a mysterious figure in a long dark robe`
- 魔法元素：`glowing magical runes`, `circular magical formation`, `dark energy`
- 场景：`dark abyssal portal`, `antique office desk`, `ancient temple gate`
- 光效：`golden and orange glowing`, `blue and purple magical glow`
- 艺术风格：`epic fantasy art style`, `detailed digital painting`, `cinematic lighting`

**技术参数：**
- 尺寸：`2:3 aspect ratio`（竖版，适合手机端）
- 品质：`detailed digital painting`, `cinematic lighting`
- 风格：根据目标受众选择 `anime-influenced realistic style` 或 `Chinese ink wash painting style`

### 3. AI生图执行

```python
# 每个风格生成1-2张备选
image_generate(
    prompt="[完整提示词]",
    aspect_ratio="portrait"  # 2:3竖版
)

# 生成的图片保存在 ~/.hermes/cache/images/ 目录
# 文件名格式：agnes_[model]_[timestamp]_[hash].png
```

### 4. 封面目录管理

```
/Users/libing/Desktop/临时文件-0001/脑洞文/封面/
├── 封面提示词.md          # 所有提示词的文档
├── agnes_xxx_风格1.png    # AI生成的封面
├── agnes_xxx_风格2.png
└── ...
```

**操作步骤：**
```bash
# 创建目录
mkdir -p /Users/libing/Desktop/临时文件-0001/脑洞文/封面/

# 移动生成的图片
mv ~/.hermes/cache/images/agnes_*.png /Users/libing/Desktop/临时文件-0001/脑洞文/封面/

# 保存提示词文档
mv 封面提示词.md /Users/libing/Desktop/临时文件-0001/脑洞文/封面/
```

## 从已有提示词批量生成封面

当提示词文件已存在时（如 `封面提示词.md`），执行批量生成：

```
步骤：
1. 读取提示词文件，提取每个风格的 prompt 文本
2. 逐个调用 image_generate(prompt=..., aspect_ratio="portrait")
3. 从 ~/.hermes/cache/images/ 复制到封面目录，命名为 风格X_描述名.png
4. 更新提示词文件，在每个风格末尾添加 **生成图片**：`文件名.png`
```

**命名规范**：`风格{序号}_{中文风格名}.png`（如 `风格1_暗黑魔法阵.png`）

**批量复制脚本**：
```python
import shutil, os
target_dir = "/Users/libing/Desktop/临时文件-0001/脑洞文/封面"
for src, name in zip(source_images, target_names):
    shutil.copy2(src, os.path.join(target_dir, name))
```

## ⚠️ 关键陷阱

### 1. 提示词可以包含中文标题和作者名
**2026-07验证**：Agnes AI (agnes-image-2.0-flash) 能正确渲染中文文字。
**提示词写法**：`large 3D metallic bronze-gold Chinese title text "书名" at the top` + `author name "作者名" in elegant silver text at the bottom`
**注意**：文字渲染不保证100%准确，可能有少量错字。生图后建议人工检查文字。

### 2. 竖版比例必须明确指定
**问题**：不指定比例会生成方形图片，不适合小说封面。
**解决**：始终使用 `aspect_ratio="portrait"`（2:3竖版）。

### 3. 多封面推荐功能的平台要求
**番茄小说**：
- 需要5-7个不同风格的封面
- 每个封面面向不同偏好的读者
- 效果排名每天12:00更新
- 通过"多书名实验"或"多封面推荐"功能配置

### 4. 后期处理必要性
**问题**：AI生成的封面没有书名文字，需要后期添加。
**解决**：使用Canva（在线）或Photoshop添加：
- 书名（大字，居中或顶部）
- 作者名（小字，底部）
- 可选：副标题、标签

### 5. 使用vision_analyze分析封面风格
**技巧**：用vision_analyze工具详细分析封面的构图、色调、人物形象、文字排版、整体氛围。
**模板**：`分析这张番茄小说封面的风格特点：构图、色调、人物形象、文字排版、整体氛围。这是[类型]类小说的封面。`
**价值**：可以提取具体的设计元素和构图技巧，用于创作新的封面提示词。

### 6. 从现有封面中提取元素创作新提示词
**方法**：
1. 分析热门封面的构图技巧（分层、留白、局部特写）
2. 提取色调方案（主色、点缀色、对比关系）
3. 借鉴意象符号（花卉、器物、建筑元素）
4. 融合到自己的小说主题中
**示例**：从番茄古风世情封面中提取"分层意境构图"，创作"暗黑山水"风格封面。

### 7. 跨类型封面灵感借鉴（2026-07验证）
**方法**：从其他类型的热门封面中提取构图/排版技巧，应用到自己的小说类型。
**成功案例**：
- 从古风世情的"分层意境构图" → 创作"暗黑山水"风格（前景废墟人物+中景暗河+远景血色山脉）
- 从古风世情的"意象留白" → 创作"意象氛围"风格（魔法物品悬浮+纯黑背景+极简构图）
- 从古风世情的"局部特写" → 创作"局部特写"风格（手部+魔法戒指+暗黑能量）
**步骤**：
1. 用 vision_analyze 分析目标类型的封面（构图、色调、人物、排版、氛围）
2. 提取构图技巧和排版方式（不提取色调，因为不同类型的色调差异大）
3. 将构图技巧与自己小说的暗黑元素融合，创作新提示词

### 8. 番茄小说搜索页的限制（2026-07验证）
**问题**：番茄小说搜索页（fanqienovel.com/search）有以下限制：
- 搜索结果文字显示乱码/截断（SPA渲染问题）
- 点击搜索结果无法跳转到书籍详情页（JavaScript事件未正确绑定）
- 搜索API不对外公开（无可用的API端点）
**解决方案**：
- 用排行榜页面（/rank）代替搜索页获取封面参考
- 如果必须搜索，用 Chrome DevTools MCP 手动操作浏览器（比 browser_* 工具更稳定）
- 或者用其他平台（起点、晋江）搜索同类型书籍作为封面参考

## 目录结构规范

```
脑洞文/封面/
├── 封面提示词.md           # 提示词文档
├── [风格名]_[序号].png     # AI生成的封面图片
└── README.md              # 封面说明（可选）
```

## 已知账号

番茄小说作者后台：需登录后访问

## 参考资源

- `references/fanqie-cover-styles.md` — 番茄小说热门封面风格详细分析
- `references/cover-prompt-templates.md` — 各类型小说的封面提示词模板库（不含文字）
- `references/cover-prompts-with-text.md` — 含标题+作者名的封面提示词模板（Agnes AI验证可用）
