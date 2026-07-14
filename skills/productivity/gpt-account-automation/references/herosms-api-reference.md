# HeroSMS API 完整参考

**日期**: 2026-06-09 实测确认
**状态**: ✅ 已验证可用

## 平台概况

- **官网**: https://hero-sms.com
- **定位**: SMS-Activate官方继任者（2025-12-29 SMS-Activate关停后上线）
- **兼容性**: 100%兼容SMS-Activate API协议
- **覆盖**: 200+国家，500,000+每日新增号码
- **支付**: 支付宝、微信、USDT加密货币
- **KYC**: 不需要实名认证

## 两套API

### Legacy API（接码专用）

| 项目 | 值 |
|------|-----|
| 端点 | `https://hero-sms.com/stubs/handler_api.php` |
| 认证 | `?api_key=KEY` 查询参数 |
| 协议 | SMS-Activate兼容 |
| 用途 | 买号、查状态、完成/取消激活 |

**Register_GPT_v0 使用此API。**

### REST v1 API（新功能）

| 项目 | 值 |
|------|-----|
| 端点 | `https://hero-sms.com/api/v1` |
| 认证 | `Authorization: ApiKey KEY` HTTP头 |
| 用途 | 邮箱管理等新功能 |

## API Key 获取

⚠️ **仪表盘Key ≠ API Key！**

1. 登录 hero-sms.com
2. Profile → API设置
3. 点击"生成API Key"按钮
4. 弹出网址中显示的32位字符串 = 正确的API Key

**如果复制了仪表盘上的Key，会返回 BAD_KEY 错误。**

## Legacy API 操作一览

| 操作 | 参数 | 响应格式 |
|------|------|----------|
| 查余额 | `action=getBalance` | `ACCESS_BALANCE:3` |
| 买号 | `action=getNumber&service=dr&country=6` | `ACCESS_NUMBER:id:phone` |
| 查状态 | `action=getStatus&id=123` | `STATUS_OK:code` 或 `STATUS_WAIT_CODE` |
| 完成 | `action=setStatus&id=123&status=6` | `ACCESS_SET_STATUS` |
| 取消 | `action=setStatus&id=123&status=8` | `ACCESS_SET_STATUS` |
| 国家列表 | `action=getCountries` | JSON数组 |
| 服务列表 | `action=getServicesList&country=0&lang=cn` | `{"services": [...]}` |
| 价格库存 | `action=getPrices&service=dr` | JSON对象 |

## 常用服务标识

| 标识 | 服务 |
|------|------|
| `dr` | OpenAI/ChatGPT |
| `tg` | Telegram |
| `wa` | WhatsApp |
| `go` | Google |
| `ig` | Instagram |
| `fb` | Facebook |

## 错误码

| 错误 | 含义 | 解决 |
|------|------|------|
| `BAD_KEY` | Key无效 | 检查是否复制了正确的API Key |
| `NO_BALANCE` | 余额不足 | 充值 |
| `NO_NUMBERS` | 无可用号码 | 换国家或等一会 |
| `SERVICE_NOT_AVAILABLE` | 服务不可用 | 换服务标识或国家 |

## Python 客户端

### 安装
```bash
pip install herosms  # 或 uv pip install herosms
# 依赖: httpcore, httpx, tenacity
```

### 异步用法
```python
import asyncio
from herosms import HeroSMSClient

async def main():
    async with HeroSMSClient(api_key="YOUR_KEY") as client:
        balance = await client.get_balance()
        activation = await client.activations.create(service="dr", country=6)
        status = await activation.wait_for_sms(timeout=120)
        await activation.complete()

asyncio.run(main())
```

### 同步用法
```python
from herosms import SyncHeroSMSClient

with SyncHeroSMSClient(api_key="YOUR_KEY") as client:
    balance = client.get_balance()
```

## 2026-06-09 实测数据

- 余额: $3.00
- OpenAI服务(dr)总可用号码: 2,602,011
- 可用国家: 130个
- 价格范围: $0.025 ~ $0.20
- 最低充值: $3 USDT/支付宝/微信

## 手机号码获取测试

通过Register_GPT_v0系统成功获取手机号码：

```python
import requests

# 登录获取Token
login_resp = requests.post('http://localhost:1989/api/auth/login', 
    json={'username': 'admin', 'password': 'admin123'})
token = login_resp.json()['token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 获取手机号码
resp = requests.post('http://localhost:1989/api/sms-api/get-numbers', 
    headers=headers,
    json={'service': 'dr', 'country': 4, 'quantity': 1})
result = resp.json()
# 结果: {'got': 1, 'items': [{'id': 1, 'phone': '639567301625', 'activation_id': 472458285}]}
```

**测试结果**：
- 成功获取手机号码: 639567301625
- 国家ID: 4 (最便宜，$0.025)
- 激活ID: 472458285
