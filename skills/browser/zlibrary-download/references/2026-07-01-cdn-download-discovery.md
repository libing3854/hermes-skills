# Z-Library CDN下载发现 (2026-07-01)

## 问题背景
之前的下载流程假设Chrome浏览器点击下载按钮后，文件会自动下载到~/Downloads/。
实际上Chrome下载经常卡住（.crdownload文件停止增长），且navigate_page在书籍详情页上必定失败。

## 关键发现

### 1. Z-Library是SPA框架
- 使用自定义元素 `<z-bookcard>` 展示搜索结果
- Shadow DOM中包含书籍链接
- 内部导航使用 `history.pushState`，不触发完整页面加载
- `navigate_page` CDP命令在书籍详情页上返回 `net::ERR_ABORTED`

### 2. 下载链接重定向链
```
用户点击下载 → /dl/XXXXX (302重定向) → dln1.ncdn.ec/... (CDN文件)
```
- `/dl/XXXXX` 是一次性的，用过返回204
- CDN URL包含过期时间（expires参数）
- CDN无JavaScript反爬虫保护

### 3. curl被JS挑战拦截
Z-Library对非浏览器请求返回JavaScript proof-of-work挑战页面：
```html
<script>
window.onload=async function(){
  // SHA1计算proof-of-work
  // 设置cookie后reload
}
</script>
```
curl无法执行JS，所以直接访问 `/dl/XXXXX` 或书籍页面都会得到这个挑战页。

### 4. 验证过的成功流程
```
搜索(navigate_page) → 提取z-bookcard → new_page打开书籍页 → 
点击下载按钮 → list_network_requests获取CDN URL → 
curl从CDN下载 → 移动到目标目录
```

### 5. 已知CDN域名
- `dln1.ncdn.ec` - 主要CDN
- URL格式: `https://dln1.ncdn.ec/books-files/.../redirection?filename=...&s=davinci&countryCode=sg&md5=...&expires=...`

## 测试数据
成功下载的文件：
- 中国民俗史_宋辽金元卷.pdf (51MB) - 通过CDN curl下载
- 中国民俗文化鬼神_彩图版.pdf (7.9MB) - 通过CDN curl下载  
- 中国民间禁忌风俗.pdf (9.2MB) - 通过CDN curl下载

curl下载速度约 800KB/s-1MB/s，比Chrome浏览器下载更稳定。
