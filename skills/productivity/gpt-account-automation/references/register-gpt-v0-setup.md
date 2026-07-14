# Register_GPT_v0 搭建记录

**日期**: 2026-06-09
**状态**: ✅ Web服务启动成功，HeroSMS API已配置

## 项目位置

```
~/Desktop/GPT账号管理系统/AI-Account-Toolkit/Register_GPT_v0/
```

## 搭建过程

### 1. 依赖安装

```bash
cd ~/Desktop/GPT账号管理系统/AI-Account-Toolkit/Register_GPT_v0
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r web/backend/requirements.txt
uv pip install requests  # 遗漏的依赖
```

### 2. 启动服务

```bash
source .venv/bin/activate
cd web && python3.11 run_web.py
# 服务运行在 http://localhost:1989
```

### 3. 遇到的问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `TypeError: unsupported operand type(s) for \|: 'type' and 'NoneType'` | Python 3.9不支持 `str \| None` 语法 | 使用 Python 3.11 创建venv |
| `ModuleNotFoundError: No module named 'requests'` | requirements.txt遗漏requests | `uv pip install requests` |
| 启动脚本找不到 | 错误路径 `web/backend/run_web.py` | 正确路径 `web/run_web.py` |
| pip安装被拒绝 | Python 3.11由uv管理 | 使用 `uv pip install` 或创建venv |
| 端口占用 `Address already in use` | 旧进程未完全退出 | `lsof -ti :1989 \| xargs kill -9` |

## SMS API配置（HeroSMS）

### 配置方式：直接操作SQLite数据库

配置存储在 `data/admin.db` 的 `system_settings` 表中。

```bash
cd ~/Desktop/GPT账号管理系统/AI-Account-Toolkit/Register_GPT_v0

python3.11 -c "
import sqlite3

db_file = './data/admin.db'
conn = sqlite3.connect(db_file)
c = conn.cursor()

# 配置HeroSMS API
api_key = 'YOUR_HEROSMS_API_KEY'
api_url = 'https://hero-sms.com/stubs/handler_api.php'

c.execute('UPDATE system_settings SET value = ? WHERE key = ?', (api_key, 'sms_api_key'))
c.execute('UPDATE system_settings SET value = ? WHERE key = ?', (api_url, 'sms_api_url'))
c.execute('UPDATE system_settings SET value = ? WHERE key = ?', ('dr', 'sms_openai_service'))
c.execute('UPDATE system_settings SET value = ? WHERE key = ?', ('0.55', 'sms_max_price'))

conn.commit()

# 验证
c.execute('SELECT key, value FROM system_settings WHERE key LIKE \"sms_%\"')
for key, value in c.fetchall():
    print(f'{key}: {value}')

conn.close()
"
```

### system_settings 表结构

| key | 说明 | 示例值 |
|-----|------|--------|
| `sms_api_url` | SMS API地址 | `https://hero-sms.com/stubs/handler_api.php` |
| `sms_api_key` | API密钥 | `401A56ccb0d93f2809b66913d46bd75f` |
| `sms_openai_service` | OpenAI服务标识 | `dr` |
| `sms_max_price` | 最大单价 | `0.55` |
| `phone_bind_limit` | 手机号绑定次数 | `1` |

### 验证配置

```bash
# 重启服务后测试
curl -s http://localhost:1989/api/sms-api/balance \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 项目结构

```
Register_GPT_v0/
├── web/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py          # FastAPI主入口
│   │   │   ├── config.py        # 配置（从环境变量加载）
│   │   │   ├── database.py      # SQLite数据库
│   │   │   ├── routers/         # API路由
│   │   │   │   ├── auth.py      # 认证
│   │   │   │   ├── sms_api.py   # Hero-SMS/SMS-Activate集成
│   │   │   │   ├── register.py  # 注册API
│   │   │   │   └── ...
│   │   │   └── services/
│   │   │       └── hotmail007.py # 邮箱服务
│   │   └── requirements.txt
│   ├── run_web.py               # 启动脚本
│   └── docker-compose.yml       # Docker配置
├── data/
│   └── admin.db                 # SQLite数据库（配置+账号）
├── protocol_register.py         # 注册协议（65KB）
├── protocol_sora_phone.py       # 手机验证协议（91KB）
├── protocol_sentinel.py         # 哨兵协议
├── main_protocol.py             # 主协议
├── scripts/                     # 辅助脚本
├── tools/                       # 工具
└── docs/                        # 文档
```

## 关键文件

- `web/backend/app/routers/sms_api.py` — Hero-SMS/SMS-Activate API集成
- `web/backend/app/config.py` — 配置（从环境变量加载admin账号等）
- `data/admin.db` — SQLite数据库（所有配置和账号数据）
- `protocol_register.py` — 完整注册流程（含OTP+手机验证）
- `protocol_sora_phone.py` — 手机验证协议

## 默认配置

- **Web端口**: 1989
- **默认账号**: admin
- **默认密码**: admin123
- **数据库**: `data/admin.db` (SQLite)
- **数据目录**: `data/`

## 服务管理

```bash
# 启动服务
cd ~/Desktop/GPT账号管理系统/AI-Account-Toolkit/Register_GPT_v0
source .venv/bin/activate
cd web && python3.11 run_web.py

# 停止服务（解决端口占用）
lsof -ti :1989 | xargs kill -9

# 后台运行
cd web && nohup python3.11 run_web.py > /tmp/register_gpt.log 2>&1 &
```

### HeroSMS API Key 获取方式（⚠️ 重要坑点）

**仪表盘上的Key ≠ API Key！** 用户容易复制错误的Key。

**正确获取步骤**：
1. 登录 hero-sms.com
2. 进入 **Profile（个人资料）** → **API设置**
3. 点击 **"生成API Key"** 按钮
4. 弹出的网址中显示的32位字符串才是真正的API Key
5. 格式示例：`8eb11fd182A4b1b85A9AA048ed915cbA`

**如果复制了仪表盘上的Key（而非API Key），会一直返回 BAD_KEY 错误。**

### HeroSMS 两套API

HeroSMS有两套独立的API，用途不同：

**Legacy API（接码专用，兼容SMS-Activate）**：
- 端点：`https://hero-sms.com/stubs/handler_api.php`
- 认证：`?api_key=KEY` 查询参数
- 用途：查余额、买号、查状态、完成/取消激活
- Register_GPT_v0 使用此API

**REST v1 API（新功能）**：
- 端点：`https://hero-sms.com/api/v1`
- 认证：`Authorization: ApiKey KEY` HTTP头
- 用途：邮箱管理等新功能

### HeroSMS API 测试结果（2026-06-09 最终确认）

使用正确的API Key测试：

```bash
# 余额查询
curl "https://hero-sms.com/stubs/handler_api.php?api_key=正确Key&action=getBalance"
# 响应: ACCESS_BALANCE:3

# OpenAI服务(dr)库存
curl "https://hero-sms.com/stubs/handler_api.php?api_key=正确Key&action=getPrices&service=dr"
# 总可用号码: 2,602,011
# 可用国家: 130个
# 价格: $0.025 ~ $0.20
```

**官方Python包**：
```bash
uv pip install herosms  # herosms 0.1.1 + httpcore + httpx + tenacity
```
```python
from herosms import SyncHeroSMSClient
with SyncHeroSMSClient(api_key="正确Key") as client:
    balance = client.get_balance()
    print(f'Balance: {balance}')  # Balance: 3.0
```

### 错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `BAD_KEY` | 复制了仪表盘Key而非API Key | 去Profile→API设置生成正确的Key |
| `NO_BALANCE` | 账户余额不足 | 充值（最低$3 USDT/支付宝/微信） |
| `ROUTE_NOT_FOUND` | 使用了REST v1的错误路径 | 使用Legacy端点 `handler_api.php` |
| `Unauthorized` | Key无效或过期 | 重新生成API Key |

### 建议操作

1. ~~登录HeroSMS后台 (hero-sms.com)~~
2. ~~查看API文档或设置页面~~
3. ~~确认API Key的完整格式~~
4. ~~检查API访问权限是否已激活~~
5. ~~确认账户余额情况~~
6. ✅ 确认使用的是正确的API Key（Profile→API设置→生成）

---

## 登录API说明

**端点**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "token": "eyJhbG...cwbk",
  "username": "admin"
}
```

**使用方式**: 在后续请求中携带JWT Token：
```
Authorization: Bearer eyJhbG...cwbk
```

**Token有效期**: 24小时

---

## 后续步骤

1. ✅ 配置HeroSMS API Key（已通过数据库配置，Key验证成功）
2. ✅ HeroSMS余额确认：$3.00
3. ✅ OpenAI服务(dr)库存确认：2,602,011个号码，130个国家
4. ✅ 手机号码获取测试：成功获取639567301625（国家ID=4，$0.025）
5. 配置代理（建议美国住宅IP，当前台湾IP可能被风控）
6. 测试完整注册流程（邮箱+密码+手机验证）
7. 如成功，可配置批量注册参数

## 完整验证流程

```python
import requests
import json

# 1. 登录获取Token
login_resp = requests.post('http://localhost:1989/api/auth/login', 
    json={'username': 'admin', 'password': 'admin123'})
token = login_resp.json()['token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2. 查询SMS余额
resp = requests.get('http://localhost:1989/api/sms-api/balance', headers=headers)
print(f"余额: {resp.json()}")  # {'balance': 3.0}

# 3. 查询OpenAI服务可用性
resp = requests.get('http://localhost:1989/api/sms-api/openai-availability', headers=headers)
data = resp.json()
print(f"总可用号码: {data['total_count']}")  # 2,621,039
print(f"可用国家: {len(data['by_country'])}")  # 130

# 4. 获取手机号码（测试）
resp = requests.post('http://localhost:1989/api/sms-api/get-numbers', 
    headers=headers,
    json={'service': 'dr', 'country': 4, 'quantity': 1})
result = resp.json()
print(f"获取到: {result['items'][0]['phone']}")  # 639567301625
```

**验证结果**：余额$3.00，OpenAI可用号码2,621,039个，成功获取手机号码639567301625。

## 服务管理

```bash
# 查看所有Python进程
ps aux | grep -E "python|run_web" | grep -v grep

# 查看端口占用
lsof -i :1989  # Register_GPT_v0
lsof -i :9119  # Hermes Dashboard
lsof -i :8801  # oMLX Server

# 停止指定进程
kill -9 <PID>

# 批量停止（谨慎使用）
lsof -ti :9119 | xargs kill -9  # 停止Dashboard
lsof -ti :8801 | xargs kill -9  # 停止oMLX
```

## 与其他工具的对比

Register_GPT_v0 是唯一集成手机验证的工具。2026年OpenAI注册必须手机验证，其他工具（openai_register、chatgpt_register_duckmail等）缺少此步骤，注册必然失败。
