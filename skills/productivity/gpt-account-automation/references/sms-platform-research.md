# 接码平台调研记录

**日期**: 2026-06-09
**状态**: 已确认平台可用性

## 平台状态

### SMS-Activate ❌ 已关停
- **关停日期**: 2025年12月29日
- **运营时长**: 整整十年
- **影响**: Register_GPT_v0 原生集成的SMS-Activate不再可用
- **替代方案**: HeroSMS（官方升级版）或5sim.net

### HeroSMS ⚠️ 可用但难自动化访问
- **官网**: https://hero-sms.com/cn
- **特点**: 基于SMS-Activate核心技术构建，是官方升级版
- **优势**: 全球180+国家虚拟号码，高级API接入
- **问题**: 网站有强Cloudflare安全验证，自动化浏览器难以通过
- **API文档**: https://hero-sms.com/cn/api
- **集成状态**: Register_GPT_v0 原生支持（见 `sms_api.py`）

### 5sim.net ⚠️ 可用但有Cloudflare
- **官网**: https://5sim.net/zh
- **特点**: API文档清晰，但有Cloudflare Turnstile验证
- **优势**: 
  - 180+国家号码
  - 价格从1卢布起
  - 24/7自动在线服务
  - 支持API批量操作
- **问题**: 有Cloudflare Turnstile验证，自动化浏览器无法通过注册
- **API文档**: https://5sim.net/manual
- **API Key**: 登录后在 https://5sim.net/zh/profile/api 查看
- **集成状态**: 需要修改 `sms_api.py` 适配
- **注册方式**: 需手动在浏览器中注册

### SMSpva ⚠️ 可用但有Cloudflare
- **官网**: https://smspva.com
- **特点**: 支持60+国家号码，有API
- **问题**: 有Cloudflare Turnstile验证，自动化浏览器无法通过注册
- **注册方式**: 需手动在浏览器中注册

### ⚠️ 重要发现（2026-06-09 实测）
**所有主流接码平台（HeroSMS、5sim、SMSpva、receive-smss）都使用Cloudflare Turnstile验证，自动化浏览器无法完成注册。** 唯一解决方案是手动在浏览器中注册接码平台账号，然后把API Key配置到系统中。

### 临时邮箱推荐
**mail.tm** — 免费API，可创建临时邮箱，用于注册接码平台：
```python
import urllib.request, json

# 创建临时邮箱
data = json.dumps({'address': 'xxx@web-library.net', 'password': 'xxx'}).encode()
req = urllib.request.Request('https://api.mail.tm/accounts', data=data, headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
result = json.loads(response.read().decode())
print(result['address'])  # 临时邮箱地址

# 获取邮件
token_data = json.dumps({'address': 'xxx@web-library.net', 'password': 'xxx'}).encode()
token_req = urllib.request.Request('https://api.mail.tm/token', data=token_data, headers={'Content-Type': 'application/json'})
token_resp = urllib.request.urlopen(token_req)
token = json.loads(token_resp.read().decode())['token']

# 读取收件箱
inbox_req = urllib.request.Request('https://api.mail.tm/messages', headers={'Authorization': f'Bearer {token}'})
inbox = urllib.request.urlopen(inbox_req)
print(json.loads(inbox.read().decode()))
```

## 5sim.net API 示例

### 购买号码（接收验证码）
```bash
curl -s -X GET \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  'https://5sim.net/v1/user/buy/activation/england/vodaphone/telegram'
```

### 获取验证码
```bash
curl -s -X GET \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  'https://5sim.net/v1/user/check/ORDER_ID'
```

### API参数说明
- `activation`: 激活类型
- `country`: 国家代码（如 `england`, `usa`, `russia`）
- `operator`: 运营商（如 `vodaphone`, `tmobile`）
- `product`: 服务标识（如 `telegram`, `openai`, `chatgpt`）

**注意**：5sim.net有Cloudflare Turnstile保护，必须手动注册后才能使用API。

## Register_GPT_v0 集成修改方案

如需使用5sim替代Hero-SMS，需要修改以下文件：

### 1. `web/backend/app/routers/sms_api.py`
- 添加5sim API的请求方法
- 修改余额查询接口
- 修改号码购买接口
- 修改验证码接收接口

### 2. `web/backend/app/config.py`
- 添加5sim API Key配置项
- 添加5sim API基础URL配置

### 3. 环境变量
```
SMS_PLATFORM=5sim
5SIM_API_KEY=your_api_key_here
```

## 测试记录

### HeroSMS 测试 ❌
- 访问 https://hero-sms.com/cn
- 遇到Cloudflare安全验证
- 自动化浏览器无法通过验证
- 结论：不适合自动化注册流程

### 5sim.net 测试 ❌
- 访问 https://5sim.net/zh
- 页面加载成功，注册表单正常显示
- 但有Cloudflare Turnstile验证
- 自动化浏览器无法通过验证
- JavaScript尝试勾选复选框无效（Cloudflare阻止）
- 结论：不适合自动化注册流程，需手动注册

### SMSpva 测试 ❌
- 访问 https://smspva.com
- 页面加载成功，注册表单正常显示
- 但有Cloudflare Turnstile验证
- 自动化浏览器无法通过验证
- 结论：不适合自动化注册流程，需手动注册

### receive-smss.com 测试 ❌
- 访问 https://receive-smss.com
- 遇到Cloudflare安全验证
- 自动化浏览器无法通过验证
- 结论：不适合自动化注册流程

### mail.tm 临时邮箱测试 ✅
- API地址：https://api.mail.tm
- 可用域名：web-library.net
- 创建邮箱成功
- 可用于注册接码平台账号
- 结论：推荐作为临时邮箱服务
