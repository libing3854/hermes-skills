# Hotmail007 邮箱服务配置

## 注册信息（2026-06-09）

- 网站: https://hotmail007.com
- 账号: gptregister@web-library.net
- 密码: LLS！&147\99（冰哥通用密码）
- Client Key: 19d3436bd1314d2fa1fe1c9077c1713e233799
- 余额: $0（需充值）

## API

- Base URL: https://gapi.hotmail007.com
- 余额: GET /api/user/balance?clientKey=KEY
- 库存: GET /api/mail/getStock?mailType=outlook
- 获取邮箱: GET /api/mail/getMail?clientKey=KEY&mailType=xxx&quantity=n

## 邮箱类型

| 类型 | 价格 | 有效期 |
|------|------|--------|
| outlook/hotmail | $0.002 | 1-3小时 |
| outlook/hotmail premium | $0.003 | 1-3小时 |
| outlook/hotmail Trusted | $0.02 | 3-6个月（推荐） |

## Register_GPT_v0 配置

系统设置 → 邮箱 API:
- API地址: https://gapi.hotmail007.com
- KEY: 19d3436bd1314d2fa1fe1c9077c1713e233799
- 邮箱类型: outlook Trusted

## 数据格式

API返回: `Account:Password:Refresh_token:Client_id`
