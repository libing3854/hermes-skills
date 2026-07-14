# 浏览器获取卡牌图片工作流

## 适用场景
当需要为HTML可视化获取真实卡牌图片时使用。

## 官方数据库地址
- 中文版：https://db.yugioh-card-cn.com/
- 日文版：https://www.db.yugioh-card.com/

## 工作流程

### 1. 导航到卡片检索页面
```
browser_navigate → https://db.yugioh-card-cn.com/
browser_click → "卡片检索" 链接
```

### 2. 搜索卡名
```
browser_type → 搜索框，输入卡名（如"烙印融合"）
browser_click → 搜索按钮
```

### 3. 点击进入卡片详情
```
browser_click → 搜索结果中的卡片
```

### 4. 获取图片URL
```
browser_get_images → 返回所有图片URL
# 找到卡片图片（通常 width=200, height=290）
# URL格式：https://www.db.yugioh-card.com/yugiohdb/get_image.action?type=1&ciid=1&cid=XXXXX&enc=XXX&lang=ja
```

### 5. 下载图片
```bash
curl -o "卡牌图片/卡名.jpg" "图片URL"
```

## URL参数说明
| 参数 | 说明 |
|------|------|
| type=1 | 卡片图片 |
| ciid=1 | 版本ID |
| cid=XXXXX | 卡片ID（每张卡唯一） |
| enc=XXX | 加密参数（可能有时效性） |
| lang=ja | 日文版；lang=zh 中文版 |

## 已下载的卡牌图片示例
```
卡牌图片/
├── 烙印融合.jpg        (cid=17066)
├── 阿不思的落胤.jpg    (cid=14590)
├── 白龙之落胤.jpg      (cid=15245)
├── 吞食圣痕之龙.jpg    (cid=17259)
├── 教导的圣女 艾克莉西娅.jpg (cid=13543)
├── 白之圣女 艾克莉西娅.jpg  (cid=16197)
├── 赫之圣女 卡尔特西娅.jpg  (cid=22148)
├── 引导的圣女 奎姆.jpg     (cid=22144)
├── 冰剑龙 幻冰龙.jpg      (cid=17413)
├── 烙印断罪.jpg          (cid=11160)
└── 落胤与圣女.jpg        (cid=13183)
```

## 批量下载模式
当需要下载多张卡牌图片时：
1. 先用浏览器搜索每张卡，记录cid和enc
2. 用curl批量下载
3. 保存到统一的 `卡牌图片/` 目录

## 注意事项
- `enc` 参数可能有时效性，过期后需要重新获取
- 如果curl下载的文件大小为0或很小，说明URL已过期，需要重新用浏览器获取
- 图片格式通常为jpg，但有时可能是png
