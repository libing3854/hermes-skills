---
name: zlibrary-download
description: >
  从Z-Library批量下载书籍并按书名建文件夹组织。支持单本下载和多本并行下载。
  覆盖：搜索→详情页→下载→文件整理→格式转换的完整流程。
trigger:
  - 用户要求从Z-Library下载书籍/电子书
  - 用户要求批量下载PDF/EPUB资源
  - 搜索"z-library"、"zlibrary"、"电子书下载"
---

# Z-Library 批量下载

## 前置条件

1. **登录账号**：Z-Library需要登录才能下载。账号信息：
   - 邮箱：[REDACTED]
   - 密码：[REDACTED]
   - 高级会员（每日限额10本）
   - 登录URL：https://zh.z-library.sk/login
2. **Chrome DevTools MCP**：必须有 `mcp_chrome_devtools_*` 工具集
3. **代理**：Z-Library可能需要代理访问（ClashX端口7890）

## 核心工作流

### ⚡ 验证过的下载流程（CDN绕过方案）

Z-Library是SPA框架，有JavaScript反爬虫保护。curl直接访问会被JS挑战拦截。
**正确方案**：用Chrome DevTools获取CDN URL，再用curl从CDN下载。

```
对于每本书，执行以下步骤：

1. 搜索：mcp_chrome_devtools_navigate_page → https://zh.z-library.sk/s/?q=关键词
   （navigate_page对搜索页可用）

2. 提取书籍信息：mcp_chrome_devtools_evaluate_script
   () => {
     const cards = document.querySelectorAll('z-bookcard');
     return Array.from(cards).slice(0, 10).map(c => ({
       id: c.getAttribute('id'),
       href: c.getAttribute('href'),
       download: c.getAttribute('download'),
       ext: c.getAttribute('extension'),
       size: c.getAttribute('filesize')
     }));
   }

3. 打开书籍详情页：mcp_chrome_devtools_new_page → 书籍URL
   ⚠️ 必须用 new_page，navigate_page 会 ERR_ABORTED！

4. 选择新标签页：mcp_chrome_devtools_select_page

5. 点击下载按钮获取CDN URL：
   mcp_chrome_devtools_evaluate_script
   () => {
     const dl = document.querySelector('a[href*="/dl/"]');
     if (dl) { dl.click(); return dl.href; }
     return 'no download link';
   }

6. 等3秒后获取CDN URL：mcp_chrome_devtools_list_network_requests
   从结果中找到 dln1.ncdn.ec 开头的URL

7. 用curl从CDN下载（绕过JS挑战）：
   curl -L -o 目标路径 \
     -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
     -H "Referer: https://zh.z-library.sk/" \
     --max-time 120 \
     "CDN_URL"

8. 验证文件：file 目标路径 确认是PDF/EPUB
9. 移动到目标目录
```

### ❌ 不可行的方法（已验证失败）

| 方法 | 失败原因 |
|------|---------|
| curl直接访问 /dl/XXXXX | 被JS挑战拦截，返回HTML页面 |
| navigate_page打开书籍详情页 | ERR_ABORTED（SPA拦截） |
| window.location.href跳转 | URL变了但DOM不更新（SPA） |
| 浏览器原生下载（click触发） | Chrome下载经常卡住不动 |
| XHR fetch下载 | 返回204 No Content（一次性链接） |

### 批量下载策略

当前最高效的方式是**在当前会话中逐本操作**（不建议delegate_task，因为子代理无法共享浏览器会话）。

如果要并行，每个子代理需要独立的Chrome标签页，且必须用 `new_page` 打开书籍页面。

## ⚠️ 关键陷阱

### 1. navigate_page vs new_page 的区别（SPA框架）
**搜索页**：`navigate_page` 可用 → `https://zh.z-library.sk/s/?q=关键词`
**书籍详情页**：`navigate_page` 必定失败（ERR_ABORTED）→ 必须用 `new_page`

原因：Z-Library是SPA（Single Page Application），书籍详情页的URL会触发浏览器下载行为，CDP的navigate命令无法处理。

**正确操作**：
```python
# 搜索页 - navigate_page可用
mcp_chrome_devtools_navigate_page(url="https://zh.z-library.sk/s/?q=关键词", type="url")

# 书籍详情页 - 必须用new_page
mcp_chrome_devtools_new_page(url="https://zh.z-library.sk/book/ID/书名.html")
mcp_chrome_devtools_select_page(pageId=新页面ID)
```

### 2. z-bookcard Shadow DOM 提取
搜索结果在 `<z-bookcard>` 自定义元素中，`title` 属性为null，信息在其他属性中：
```javascript
() => {
  const cards = document.querySelectorAll('z-bookcard');
  return Array.from(cards).slice(0, 10).map(c => ({
    id: c.getAttribute('id'),
    href: c.getAttribute('href'),       // 书籍详情页URL
    download: c.getAttribute('download'), // /dl/XXXXX 下载链接
    ext: c.getAttribute('extension'),    // pdf/epub/fb2
    size: c.getAttribute('filesize'),    // 文件大小
    publisher: c.getAttribute('publisher')
  }));
}
```

### 3. curl无法绕过JS挑战（重要！）
**问题**：Z-Library对curl等非浏览器客户端返回JavaScript挑战页面（需要执行JS计算proof-of-work），curl无法执行JS。
**验证**：`curl -L -o file "https://zh.z-library.sk/dl/XXXXX"` → 返回HTML而非文件。
**解决**：必须通过Chrome DevTools获取CDN URL后，用curl从CDN下载。CDN无JS挑战。

### 4. CDN URL获取方法
点击书籍页面的下载按钮后，CDN URL出现在网络请求中：
```python
mcp_chrome_devtools_list_network_requests(resourceTypes=["document"])
# 从结果中找 dln1.ncdn.ec 开头的URL
```
CDN URL格式：`https://dln1.ncdn.ec/books-files/.../redirection?filename=...&s=davinci&...`

### 5. 浏览器原生下载可能卡住
**问题**：Chrome点击下载按钮后，.crdownload文件可能停止增长（卡在某个大小）。
**解决**：不要等浏览器下载完成。点击下载按钮只是为了触发CDN重定向获取URL，实际下载用curl。

### 5b. 下载链接返回200而非302（07-01新发现）
**问题**：部分书籍的 `/dl/XXXXX` 链接返回HTTP 200（直接响应）而非302（重定向到CDN）。此时：
- network requests中只有一条 `GET /dl/XXXXX [200]`，没有CDN URL
- 浏览器可能显示文件内容但不触发下载
- ~/Downloads/中无新文件
**症状**：`list_network_requests` 结果中找不到 `dln1.ncdn.ec` 开头的URL
**解决**：返回搜索页，换一个版本的同名书籍重试。200响应通常出现在txt/小文件格式的书籍上。PDF/EPUB大文件通常返回302。

### 6. /dl/ 链接是一次性的
**问题**：`/dl/XXXXX` 链接使用一次后失效（返回204 No Content）。
**解决**：每次下载都需要重新从书籍页面获取新的下载链接。

### 9. Tab管理：及时关闭不需要的标签页
**问题**：每本书用 `new_page` 打开详情页会创建新标签页，12本书就累积了50+标签页，导致：
- Chrome内存占用飙升
- `select_page` 时页面列表过长难以定位
- 后期 `new_page` 更容易失败（ERR_ABORTED）
**解决**：每本书下载完成后关闭详情页标签：
```python
mcp_chrome_devtools_close_page(pageId=详情页ID)
```
保留搜索结果页，关闭书籍详情页。每次下载完立即清理。

### 10. 搜索URL格式
使用 `?q=` 参数格式：`https://zh.z-library.sk/s/?q=关键词`
URL编码中文关键词：`https://zh.z-library.sk/s/?q=%E4%B8%AD%E5%9B%BD%E6%B0%91%E4%BF%97`

### 8. 下载格式选择
- 优先下载PDF（兼容性最好）
- 如果只有EPUB/FB2，也可以下载
- 在z-bookcard的 `extension` 属性中查看格式

## 目录结构规范

```
/Users/libing/Desktop/临时文件-0001/知识库/{主题}/
  ├── 书名A/
  │   └── 书名A (作者).pdf
  ├── 书名B/
  │   └── 书名B (作者).epub
  └── ...
```

每本书一个文件夹，用 `mkdir -p` 创建。

## 转换流程（下载后）

下载完成后直接用脚本批量转换为MD，无需等闪莉。

**工具**：pymupdf4llm（PDF）+ html2text（EPUB），均已安装。
**脚本**：`scripts/convert_to_md.py` — 扫描知识库目录，自动转换所有PDF/EPUB为MD。
**用法**：`python3 scripts/convert_to_md.py`（后台运行，大文件可能需要10-15分钟）

注意：大PDF（>100MB）转换耗时较长，建议用 `terminal(background=true, notify_on_complete=True)` 运行。

## 账号轮换策略（突破每日限额）

Z-Library 的"高级帐户"（Premium）仍然有每日10次下载限额。要下载更多，需要轮换账号。

**Gmail 别名技巧**：Gmail 支持 `+` 别名，`user+1@gmail.com` 和 `user@gmail.com` 收同一个邮箱。Z-Library 将它们视为不同账号。

**注册流程**：
1. `mcp_chrome_devtools_navigate_page → https://zh.z-library.sk/registration`
2. `take_snapshot` 获取表单 uid
3. `fill_form` 填写邮箱(user+1@gmail.com)、密码、昵称
4. 点击"创建账户"
5. 如果提示"已存在"，直接去登录页面用该邮箱+密码登录

**轮换策略**：
- 账号A下载10本后，切换到账号B继续
- 每个账号注册后自动获得2周高级会员
- 记录所有账号信息（邮箱|密码|昵称）供后续使用

**已知账号**（冰哥提供）：
- [REDACTED] | [REDACTED] | 奇谭书 | 已确认可用 | 每日10本限额已用完
- [REDACTED] | [REDACTED] | 已确认可用 | 新账号，有下载额度

**⚠️ 重要：Z-Library"高级帐户"≠ 无限下载**
即使登录页面显示"高级帐户"（Premium），实际上仍然是 BASIC 级别，每日限额10次。只有通过捐款升级到真正的 PREMIUM 才能获得999次/天。判断方法：访问下载页面，如果显示"每日限额 10/10"就是 BASIC。

### 6. ⚠️ delegate_task 模型配置陷阱（2026-07-01 血泪教训 - ¥112）

**问题**：`delegate_task` **不会**自动使用 `delegation` 配置中的 provider/model。即使 config.yaml 设置了 `delegation.provider: xiaomi`，delegate_task 仍然使用当前会话的默认模型（通常是 deepseek-v4-pro）。

**后果**：一次批量下载任务派出 10+ 个子代理，每个子代理用 deepseek-v4-pro 调用 50 次 = **671 次调用，5575 万 tokens，¥112**。

**根因**：delegate_task 的 `model` 参数必须在调用时显式传入，delegation config 只影响其他场景。

**正确用法**：
```python
# ❌ 错误 - 不指定 model，使用默认的 deepseek-v4-pro（贵！）
delegate_task(goal="下载书籍", toolsets=["browser", "terminal"])

# ✅ 正确 - 显式指定免费模型
delegate_task(tasks=[{
    "goal": "下载书籍",
    "model": {"model": "agnes-2.0-flash"},
    "toolsets": ["browser", "terminal"]
}])

# ✅ 或用 xiaomi（免费）
delegate_task(tasks=[{
    "goal": "下载书籍",
    "model": {"model": "mimo-v2.5"},
    "toolsets": ["browser", "terminal"]
}])
```

**冰哥偏好**：子代理优先用 agnes-2.0-flash（免费且质量好）。备选 xiaomi/mimo-v2.5。

**诊断方法**：如果子代理连续返回 `HTTP 402: Insufficient Balance`，立即停止并检查：
1. 子代理日志中的 `model=` 参数
2. 对应 provider 的 API key 余额
3. 不要盲目重试——先诊断根因！

### 7. ⚠️ 不要盲目重试失败的子代理

**问题**：子代理失败后（如 HTTP 402），立即派出新子代理执行相同任务，陷入无限循环。
**后果**：浪费时间 + 浪费 API 调用（即使失败也消耗 token）。
**正确做法**：
1. 子代理失败 → 检查失败原因（日志中的 error message）
2. 如果是模型/API key 问题 → 停止，告诉冰哥，修复后再继续
3. 如果是 Z-Library 限额问题 → 切换账号或等待明天
4. **冰哥说"停"= 立即停止所有操作，不要继续**

## 技术细节参考
- `references/2026-07-01-cdn-download-discovery.md` — CDN绕过方案的详细技术发现、JS挑战机制、验证数据
- `references/2026-07-01-batch-download.md` — 批量下载经验
- `references/2026-07-01-delegate-task-debugging.md` — delegate_task模型配置调试

## 已知限制

- 高级会员每日限额10本（即使显示"高级帐户"）
- 大文件（>100MB）下载较慢，需等待更长时间
- 部分书籍可能只有EPUB/MOBI格式，无PDF
- Z-Library页面偶有自动重定向，需要多次重试
- "发送到Telegram/邮箱"等选项也受每日限额限制
- Telegram限50MB，邮箱限17.5MB

## 已知账号

| 邮箱 | 密码 | 昵称 | 状态 |
|------|------|------|------|
| [REDACTED] | [REDACTED] | 奇谭书 | 高级会员到2026-07-14，每日10本限额 |
| [REDACTED] | [REDACTED] | 不朽的毁灭之王 | 新账号，有下载额度 |

**⚠️ "高级帐户"≠ 无限下载**
Z-Library 登录页面显示"高级帐户"（Premium）但实际仍是 BASIC 级别，每日限额10次。
只有通过捐款升级到真正的 PREMIUM 才能获得999次/天。
判断方法：访问下载页面，如果显示"每日限额 10/10"就是 BASIC。
