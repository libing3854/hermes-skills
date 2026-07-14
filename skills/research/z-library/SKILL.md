---
name: z-library
description: "在 Z-Library 搜索、下载电子书，组织到知识库。覆盖账号管理、搜索、单本/批量下载、文件夹组织。"
triggers:
  - "下载电子书"
  - "Z-Library"
  - "z-lib"
  - "下载PDF书籍"
  - "搜索参考资料"
  - "下载典籍"
tools:
  - browser
  - terminal
  - delegation
---

# Z-Library 电子书下载与管理

在 Z-Library (zh.z-library.sk) 上搜索、下载电子书，并组织到知识库中。

## 触发条件
- 用户要求下载电子书、PDF、学术资料
- 用户提到 Z-Library、z-lib、电子图书馆
- 用户要求搜索并下载参考资料、工具书、典籍

## 前置条件
- Chrome 浏览器已登录 Z-Library（账号信息见 memory）
- 网络可访问 zh.z-library.sk（可能需要代理）

## 核心流程

### 单本下载（可靠流程）

每一步都用 `evaluate_script` 而非 snapshot，因为 snapshot 经常 >100KB 且响应慢。

**步骤 1：搜索**
```
navigate_page → https://zh.z-library.sk/s/{关键词}
```

**步骤 2：等待并读取搜索结果**
```
evaluate_script: async () => {
  await new Promise(r => setTimeout(r, 3000));
  const cards = document.querySelectorAll('z-bookcard');
  return Array.from(cards).map(c => ({
    href: c.getAttribute('href'),
    download: c.getAttribute('download'),
    title: c.querySelector('[slot="title"]')?.textContent?.trim(),
    extension: c.getAttribute('extension'),
    filesize: c.getAttribute('filesize'),
  }));
}
```
z-bookcard 是自定义 Web Component，没有内嵌的 `<a>` 标签。书籍链接在 `href` 属性中（格式 `/book/{id}/{slug}.html`），下载路径在 `download` 属性中（格式 `/dl/{code}`）。

**步骤 3：进入详情页**
```
navigate_page(type="url") → https://zh.z-library.sk{card.href}
```
⚠️ 不要用 `navigate_page` 直接跳到 `/dl/` 链接（会 Bad Gateway）。必须走详情页。

**步骤 4：在详情页找到下载链接并点击**
```
evaluate_script: async () => {
  await new Promise(r => setTimeout(r, 2000));
  const links = document.querySelectorAll('a');
  for (const link of links) {
    if (link.href && link.href.includes('/dl/')) {
      link.click();
      return { clicked: true, href: link.href };
    }
  }
  return { error: 'no dl link', title: document.title };
}
```

**步骤 5-6：等待下载 + 移动文件**
```
terminal: sleep 20-30 && ls -lt ~/Downloads/ | head -3
terminal: mv "旧文件名" "目标文件夹/"
terminal: ls -lh "目标文件夹/"   # 确认到位
```

### 批量下载（推荐用子代理并行）
1. 整理书籍列表（书名|搜索关键词|目标文件夹）
2. 每5本一批，用 `delegate_task` 派子代理并行下载
3. 子代理负责：搜索→下载→移动到目标文件夹
4. 每批完成后可通知用户

### 文件夹组织规范
```
/Users/libing/Desktop/临时文件-0001/知识库/{主题}/
├── 书名1/
│   └── 书名1 (作者) (z-library.sk, ...).pdf
├── 书名2/
│   └── 书名2 (作者) (z-library.sk, ...).pdf
└── ...
```
**每本书一个文件夹**，文件夹名用书名（去掉副标题和标点）。

## 关键 Pitfalls

> **参考**：`references/reliable-download-pattern.md` 包含 2026-07-01 验证通过的可靠下载流程和已知书籍 ID 列表。

### ⚠️ 直接访问 /dl/ 链接会 Bad Gateway
直接用 `mcp_chrome_devtools_navigate_page` 打开 `https://zh.z-library.sk/dl/{code}` 会返回 "Bad Gateway"。
**正确做法**：必须通过书籍详情页点击下载链接触发下载。

### ⚠️ 书籍详情页 URL 格式
URL 格式为 `/book/{id}/{slug}.html`，但 ID 是短码（如 `ZjKa821qO0`），不是纯数字。
如果只知道 ID，用搜索页面找到书籍再点击更可靠。

### ⚠️ 每日下载限额（实测 2026-07-01）
- 未登录：每天 10 本
- 登录（BASIC）：每天 10 本
- 高级会员（Premium，注册赠送 2 周）：**也是每天 10 本**（不是无限制！）
- 只有额外捐款升级到更高等级才能到 999/天
- 限额在 UTC 午夜（北京时间 08:00）重置
- **账号轮换策略**：用多个邮箱注册多个账号，每个都有 10/天，限额用完切换
- **子代理批量下载时**：每个子代理共享浏览器 session，下载次数累加到同一账号限额

**实测数据**：一个高级会员账号一天下载 10 本后，第 11 本点击下载会跳转到"每日限额已用完"页面，显示 BASIC: 10/10。

### ⚠️ 浏览器批量下载效率
逐本下载每本 1-2 分钟。批量下载时：
- **必须用子代理并行**（delegate_task，每批 5 本）
- 不要串行逐本下载
- 一个子代理共享一个浏览器 session，所以同一批次内的书会串行

### ⚠️ 搜索结果页的 snapshot 超大
Z-Library 搜索结果页的 snapshot 常超过 100KB。
**推荐**：用 `mcp_chrome_devtools_evaluate_script` 做 JS 查询提取链接，而不是解析完整 snapshot。

### ⚠️ URL 搜索（/s/关键词）会被自动重定向
`navigate_page` 到 `https://zh.z-library.sk/s/{关键词}` 经常被 Z-Library 自动重定向到不相关的搜索结果页（如搜 "中国史话" 跳到 "中国少数民族民俗大辞典"）。
**推荐做法**：从首页开始，用 `fill` + `click` 操作搜索表单（而非 URL 导航），搜索结果页的 URL 会是 `/s/?q=...` 格式，这更稳定。

### ⚠️ 直接导航到书籍详情页

**两种URL格式都可靠**（2026-07-01 验证）：

| 格式 | 示例 | 可靠性 |
|------|------|--------|
| `/book/{id}/` | `https://zh.z-library.sk/book/8vl8MVLave/` | ✅ 可靠 |
| `/book/{id}/{slug}.html` | `https://zh.z-library.sk/book/8vl8MVLave/中国民俗史-宋辽金元卷.html` | ✅ 可靠 |

用 `navigate_page(type="url")` 直接打开这两种格式都可以。如果遇到重定向，通常是因为 book ID 无效或书籍已被移除。

⚠️ 但 **不推荐**直接跳到 `/dl/` 链接（会 Bad Gateway 或下载错误文件）。必须经过详情页触发下载。

### ⚠️ snapshot 点击下载链接不可靠
用 `mcp_chrome_devtools_click` 点击下载链接时，元素可能已从 DOM 中消失（页面跳转、重新渲染）。**推荐**：一律用 `evaluate_script` 查找 `a[href*="/dl/"]` 并调用 `.click()`，不做 snapshot。

### ⚠️ 下载前检查"已下载"标记
搜索结果中标记为"已下载"的书之前已下载过。先检查目标文件夹和 `~/Downloads/` 是否已有该文件，避免重复下载。用 `terminal: find` 或 `ls` 确认。

### ⚠️ select_page 的 pageId 可能失效
当页面被导航覆盖或关闭后，`chrome_devtools_select_page(pageId=N)` 会返回 "No page found"。
**推荐**：导航前先 `list_pages` 确认目标页面仍存在。如果需要在新 tab 中打开（不覆盖当前 tab），使用 `new_page(url=...)`。

### ⚠️ 下载触发后的文件确认
download 触发后浏览器开始写入文件，文件名可能临时显示为 `未确认 XXXXX.crdownload`，下载完成后才变成正式文件名。大文件（50MB+）可能需要 30-60 秒。参考 32MB PDF 实际耗时约 20 秒。
**推荐**：sleep 20-30 秒后检查 `~/Downloads/`，如果还有 `.crdownload` 文件则继续等待。

### ⚠️ 搜索结果页 snapshot 可能触发幽灵跳转
已知 Z-Library 的页面 JavaScript 在 a11y accessibility tree 遍历（即 `take_snapshot`）时偶尔会触发页面跳转到不相关的搜索页面。这与 snapshot 无关，是 Z-Library 的前端实现 bug。
**推荐**：搜索结果页一律用 `evaluate_script` 提取数据，不要调用 `take_snapshot`。只在必要时（视觉确认、调试）使用 `take_screenshot`。

### ⚠️ 搜索前确认格式偏好
z-bookcard 元素的 `extension` 属性透出文件格式（`pdf`、`epub` 等）。在进入详情页之前先检查格式：如果用户指定 PDF，但搜索结果只有 EPUB，要么接受 EPUB 要么换一本。避免进入详情页后才发现没有目标格式。

## 账号信息

### 账号1（主账号）
- 邮箱：[REDACTED]
- 密码：[REDACTED]
- 状态：已有账号（2026-06-30 注册）
- 高级会员：到 2026-07-14（注册时赠送 2 周）
- 每日限额：10 本（已用完时需切换账号）

### 账号2（备用）
- 邮箱：[REDACTED]
- 密码：lb[REDACTED]
- 状态：已有账号
- 每日限额：10 本

### 账号轮换策略
当一个账号的每日限额用完时，切换到另一个账号继续下载。
操作：退出当前账号 → 登录另一个账号 → 继续下载。

**注意**：密码可能需要用户确认，不要在skill中硬编码过期密码。如果登录失败（"Incorrect email or password"），询问用户获取正确密码。

### Gmail+N 别名策略
Gmail 支持 `user+N@gmail.com` 别名（如 `libing19950105+2@gmail.com`），所有别名都收到同一邮箱。可用于注册多个 Z-Library 账号。但 Z-Library 可能检测并拒绝某些别名格式。

## 与其他技能的配合
- 下载完成后，PDF 可交由 **闪莉 (shanli profile)** 转换为 Markdown
- 转换后的 MD 文件可用于小说写作的知识库参考
- 参考：`novel-writing-pipeline` 技能中的知识库管理流程
