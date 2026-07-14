---
name: visual-reference-research
description: >
  为创意项目收集视觉参考素材。从免费图库、专业摄影站、档案馆批量下载参考图片，
  按项目分类整理。覆盖：搜索策略→批量下载→质量验证→目录管理的完整流程。
  触发条件：用户要求收集参考图片、下载素材图、建立视觉素材库、"找些照片参考"。
---

# 视觉参考素材收集

## 适用场景

- 小说写作需要场景描写的视觉参考（建筑、街巷、室内、自然风光）
- 角色设计需要人物/服饰参考
- 世界观设定需要地图/城市/废墟参考
- 封面设计前的风格调研（与 novel-cover-design 配合）

## 核心工作流

### 1. 确定素材分类

根据项目需求，将素材分成 3-5 个目录。命名用 `中文-英文` 混合，方便检索：

```
~/Desktop/hermes_sucai/
├── 老建筑/          # 描写质感参考
├── 城隍庙-古庙/     # 特定场景参考
└── 废弃建筑-灵界/   # 氛围/环境参考
```

### 2. 搜索策略（按可靠性排序）

**Tier 1 — 可程序化下载（curl 直接可用）：**
- **Unsplash**：`https://images.unsplash.com/photo-{ID}?w=1200` 直接构造 URL 即可下载高清图
  - 搜索方式：用 `mcp_anysearch_search` 搜 `site:unsplash.com [关键词]` 获取 photo ID
  - 或用 browser 访问 `https://unsplash.com/s/photos/[关键词]` 提取图片 URL
  - URL 格式：`images.unsplash.com/photo-{13位ID}?w=1200`（w 参数控制宽度）

**Tier 2 — 需浏览器交互（可能被反爬）：**
- **Magnific (原Freepik)**：免费照片，需浏览器访问
- **Pexels**：⚠️ 被 Cloudflare CAPTCHA 拦截，需手动验证
- **Pixabay**：⚠️ 同样被 Cloudflare 拦截

**Tier 3 — 专业/付费来源：**
- **汇图网** (huitu.com)：中国摄影师原创高清图，付费
- **光厂VJshi** (vjshi.com)：专业摄影素材，单张 20-250 元
- **Shutterstock**：全球最大图库，需订阅

**Tier 4 — 特殊来源：**
- **天下老照片网** (laozhaopian5.com)：历史老照片档案，可下载 PDF 影集
- **民国图片资源库** (minguotupian.com)：民国时期建筑/人物照片
- **数字敦煌** (ip.e-dunhuang.com)：敦煌石窟数字素材
- **chinaruins.eg2.fr**：专门记录中国废墟的 urbex 网站

### 3. 批量下载执行

**方式 A：Python 脚本 + curl（推荐，适合 Tier 1 来源）**

```python
import urllib.request, ssl, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

photos = [
    ('https://images.unsplash.com/photo-{ID}?w=1200', '描述性文件名_01.jpg'),
    # ...
]

for url, fn in photos:
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req, timeout=30, context=ctx).read()
        if len(data) > 50000:  # 至少 50KB，过滤缩略图/错误页
            open(fn, 'wb').write(data)
            print(f'OK {fn} ({len(data)//1024}KB)')
        else:
            print(f'SKIP {fn} too small ({len(data)}B)')
    except Exception as e:
        print(f'FAIL {fn}: {str(e)[:60]}')
```

**方式 B：并行子代理（适合多分类同时下载）**

```
delegate_task(tasks=[
    {goal: "下载10张老建筑照片到 ~/Desktop/hermes_sucai/老建筑/", toolsets: ["browser", "terminal", "file"]},
    {goal: "下载10张古庙照片到 ~/Desktop/hermes_sucai/古庙/", toolsets: ["browser", "terminal", "file"]},
    {goal: "下载10张废弃建筑照片到 ~/Desktop/hermes_sucai/废墟/", toolsets: ["browser", "terminal", "file"]},
])
```

注意：子代理可能因为反爬机制下载失败，需要事后检查并补下载。

### 4. 质量验证（必须步骤）

下载后必须清理坏文件：

```bash
# 删除低于 30KB 的文件（缩略图/错误页/损坏文件）
cd ~/Desktop/hermes_sucai/目标目录/
for f in *.jpg *.png; do
  size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
  [ "$size" -lt 30000 ] && echo "删除: $f (${size}B)" && rm "$f"
done

# 统计有效文件
ls *.jpg *.png 2>/dev/null | wc -l
```

### 5. 目录命名规范

```
{中文描述}_{英文关键词}_{序号}.jpg

示例：
shaoxing_old_street_01.jpg          # 绍兴老街
chinese_courtyard_grey_tiled_01.jpg  # 中式灰瓦庭院
abandoned_hospital_dark_hallway.jpg  # 废弃医院走廊
```

## ⚠️ 关键陷阱

### 1. Pexels/Pixabay 被 Cloudflare 拦截
**现象**：browser_navigate 访问 Pexels/Pixabay 时出现 "正在进行安全验证" CAPTCHA。
**解决**：优先用 Unsplash（直接 URL 构造最可靠），或改用 Tier 3/4 来源。
**2026-07 验证**：此问题持续存在，不要浪费时间重试。

### 2. Unsplash URL 构造的 404 问题
**现象**：部分 photo ID 返回 404（ID 不存在或已删除）。
**解决**：脚本中已用 try/except 处理，跳过 404 继续下载。准备比目标数量多 30% 的 URL 列表。

### 3. 缩略图冒充高清图
**现象**：Hippopx、Pixy.org 等站的"下载"按钮实际返回 15KB 缩略图。
**解决**：始终检查 `len(data) > 50000`，低于 50KB 的一律跳过。

### 4. 子代理下载成功率不稳定
**现象**：并行子代理遇到反爬时可能整个分类 0 张下载。
**解决**：子代理完成后必须检查每个目录的文件数量，空目录需要手动补下载。

### 6. 素材必须匹配项目具体地点（2026-07 冰哥纠正）
**问题**：素材库里的图片是通用的亚洲城市/寺庙/巷子，和小说设定的具体地点完全不匹配。例如用户需要"无锡南长街水巷""平遥城隍庙殿宇结构""重庆十八梯垂直阶梯"，但素材库里只有泛泛的"老巷子""寺庙""废弃建筑"。
**解决**：收集素材前，先确认小说设定中的具体地点（城市名、地标名、建筑类型），然后针对性搜索。不要用"中国老街"这种泛关键词，要用"无锡南长街""清名桥""平遥城隍庙""重庆十八梯"等具体地名搜索。
**验证方法**：让用户检查素材是否和设定匹配。如果不匹配，重新搜集。

### 7. 版权注意
- Unsplash：免费商用，无需署名
- Pexels：免费商用，无需署名
- Pixabay：免费商用
- 汇图网/光厂/Shutterstock：需付费购买授权
- 个人参考用途通常不受版权限制，但发布/商用需确认
