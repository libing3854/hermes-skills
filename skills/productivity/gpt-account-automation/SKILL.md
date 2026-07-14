---
name: gpt-account-automation
version: 1.2.0
description: |
  ChatGPT/OpenAI 账号批量注册、Token管理与账号池维护工具集。
  包含工具对比、搭建流程、常见问题解决方案。
  触发方式：/gpt账号、/批量注册、/账号池、"注册GPT账号"、"搭建账号管理系统"
tags: [gpt, openai, account, automation, token]
metadata:
  openclaw:
    source: AI-Account-Toolkit
---

# GPT账号自动化管理

ChatGPT/OpenAI 账号批量注册、Token管理与账号池维护的完整工具集。

---

## 2026年OpenAI注册风控现状

**重要警告（2026-06-09 实测确认）**：

OpenAI在2026年加强了注册风控，自动化注册面临以下挑战：

| 问题 | 说明 |
|------|------|
| 临时邮箱被识别 | mailtm、duckmail等临时邮箱被OpenAI拒绝 |
| IP限制 | 非住宅IP（如数据中心、代理IP）被限制 |
| 设备指纹检测 | 自动化工具被检测，返回400错误 |
| 错误代码 | `account_creation_failed`（状态码400） |

**成功案例的关键**：
- 使用美国住宅IP（不是数据中心IP）
- 使用美区虚拟卡（配合订阅）
- 更"干净"的注册环境

---

## 工具对比

### 🏆 推荐工具

| 工具 | 功能 | 邮箱服务 | 手机验证 | 需要API Token | Web界面 | 2026成功率 |
|------|------|---------|---------|--------------|---------|-----------|
| **⭐ Register_GPT_v0** | GPT注册+手机验证 | 多种 | ✅ Hero-SMS/5sim | ✅ 接码平台 | ✅ | **高** |
| **openai_register** | OpenAI Codex注册 | TempMail.lol | ❌ | ❌ 不需要 | ❌ | 低 |
| **chatgpt_register_duckmail** | ChatGPT批量注册 | DuckMail | ❌ | ✅ 需要 | ❌ | 低 |
| **GPT_register+duckmail+CPA** | ChatGPT注册+Sub2Api | DuckMail | ❌ | ✅ 需要 | ✅ | 低 |
| **openai_pool_orchestrator-V6** | 账号池管理 | 多种邮箱 | ❌ | ❌ 不需要 | ✅ | 低 |

**2026年关键结论**：只有 `Register_GPT_v0` 集成了手机验证（Hero-SMS/5sim），这是2026年OpenAI注册成功的必要条件。其他工具缺少手机验证步骤，注册必然失败。⚠️ SMS-Activate已于2025年底关停，HeroSMS是官方继任者，100%兼容。

### ⚠️ 复杂度警告（2026-06-09 用户反馈）

**Register_GPT_v0 虽然功能最全，但配置极其复杂，需要5+个外部服务**。用户实际体验后明确表示"这和我想的不太一样"并要求删除换更简单的方案。

**完整运行需要的外部服务**：
1. HeroSMS API Key（接码）
2. Hotmail007 Client Key（邮箱，需充值）
3. 2Captcha API Key（打码，需手动注册有Cloudflare）
4. OpenAI OAuth Client ID（需开发者平台）
5. 代理服务器（美国住宅IP）

**冰哥的工作风格**：先查源头再动手，不盲目试错。如果项目需要太多配置，用户倾向于放弃换更简单的方案。

**用户明确反馈（2026-06-09）**："太麻烦了"、"这和我想的不太一样"。冰哥对配置复杂度容忍度低，5个外部服务配置已超出预期。

**建议策略**：
- **先评估复杂度再推荐**：在搭建前告诉用户需要多少个外部服务配置
- **提供替代方案**：如果配置太多，主动推荐更简单的替代方案（如Chrome插件、购买账号、API服务）
- **分步验证**：每配置完一个服务就验证，不要等全部配完才发现不行
- **不要默认全自动**：用户可能接受半自动（Chrome插件辅助手动注册）
- **白嫖优先**：冰哥明确要求"白嫖攻略"，优先推荐免费方案（GPT免费版、Gemini学生优惠、镜像站），付费方案作为备选
- **复杂度红线**：超过3个外部服务配置时，必须先告知用户复杂度并提供简化替代方案，不要等用户说"太麻烦了"才停

### ⭐ 首选：Register_GPT_v0（手机验证版）

**2026年唯一可行方案** — 集成了 Hero-SMS / 5sim 手机接码API（⚠️ SMS-Activate已关停）。

**优点**：
- ✅ 支持手机验证（Hero-SMS / 5sim）
- ✅ Web管理界面（端口1989）
- ✅ 完整注册协议（含OTP+手机验证流程）
- ✅ 支持代理配置

**位置**：`AI-Account-Toolkit/Register_GPT_v0/`

**搭建步骤**（⚠️ 需要 Python 3.10+）：

```bash
cd ~/Desktop/GPT账号管理系统/AI-Account-Toolkit/Register_GPT_v0

# 1. 创建Python 3.11虚拟环境（系统默认3.9不支持str|None语法）
uv venv .venv --python 3.11
source .venv/bin/activate

# 2. 安装依赖（含遗漏的requests）
uv pip install -r web/backend/requirements.txt
uv pip install requests

# 3. 启动Web服务
cd web && python3.11 run_web.py
# 访问 http://localhost:1989
```

**默认账号**：admin / admin123

**⚠️ 搭建坑点**：
1. **Python版本**：代码使用 `str | None` 语法，需要 Python 3.10+，系统默认3.9会报 `TypeError`
2. **启动脚本位置**：在 `web/run_web.py`，不是 `web/backend/run_web.py`
3. **遗漏依赖**：`requirements.txt` 缺少 `requests`，需要单独安装
4. **uv管理的Python**：不能用 `pip install`，需要用 `uv pip install` 或创建venv

**后续配置**：
1. 配置接码平台API Key（推荐HeroSMS）：
   - **方式A（推荐）**：直接操作SQLite数据库 `data/admin.db`，更新 `system_settings` 表中的 `sms_api_key` 和 `sms_api_url`（详见 `references/register-gpt-v0-setup.md`）
   - **方式B**：在Web界面设置中配置（可能需要先启动服务）
2. 配置邮箱API（Hotmail007）：
   - 注册 Hotmail007 账号（需手动，有Cloudflare验证）
   - 获取 Client Key（登录后仪表板页面）
   - 充值后通过API获取邮箱
   - 详见 `references/hotmail007-setup.md`
3. 配置代理（建议美国住宅IP）
4. 配置2Captcha（需手动注册，有Cloudflare验证）
5. 配置OAuth Client ID
6. 测试完整注册流程

---

## 接码平台选择（2026-06-09 实测）

| 平台 | 状态 | API | Cloudflare | 推荐度 |
|------|------|-----|------------|--------|
| **SMS-Activate** | ❌ 已关停（2025-12-29） | — | — | 不可用 |
| **HeroSMS** | ✅ 运营中 | ✅ 兼容SMS-Activate | ⚠️ 强Cloudflare验证 | ⚠️ 难自动化访问 |
| **5sim.net** | ✅ 运营中 | ✅ REST API | ⚠️ 有Cloudflare验证 | ⚠️ 难自动化访问 |
| **SMSpva** | ✅ 运营中 | ✅ REST API | ⚠️ 有Cloudflare验证 | ⚠️ 难自动化访问 |

**关键发现（2026-06-09 实测更新）**：
- SMS-Activate 已于2025年12月29日永久关停，运营了整整十年
- HeroSMS、5sim.net、SMSpva **全部**有Cloudflare Turnstile验证，自动化浏览器无法通过
- **所有主流接码平台都使用Cloudflare Turnstile验证**，目前无法通过自动化方式注册
- **2Captcha（打码服务）注册也有Cloudflare验证**，同样需要手动完成
- **解决方案**：需要手动在浏览器中注册这些平台账号，然后把API Key配置到Register_GPT_v0
- **临时邮箱推荐**：mail.tm API（`https://api.mail.tm`）可免费创建临时邮箱，用于注册接码平台

**5sim.net API 用法**：
```bash
# 获取API Key：登录后在 https://5sim.net/zh/profile/api 查看
# 购买号码示例（接收Telegram验证码）
curl -s -X GET -H 'Authorization: Bearer YOUR_API_KEY' \
  'https://5sim.net/v1/user/buy/activation/england/vodaphone/telegram'
```

**Register_GPT_v0 集成情况**：
- 项目原生支持 Hero-SMS（见 `web/backend/app/routers/sms_api.py`）
- SMS-Activate已关停，不推荐使用
- 如需使用5sim，需修改 `sms_api.py` 适配5sim的API格式
- 5sim API文档：https://5sim.net/manual

**HeroSMS 官方Python包**（2026-06-09 发现）：
- PyPI包名：`herosms`（版本 0.1.1）
- 安装：`uv pip install herosms`（或 `pip install herosms`）
- 依赖：httpcore, httpx, tenacity
- 支持异步和同步两种客户端
- 兼容SMS-Activate API协议
- 示例：
```python
from herosms import SyncHeroSMSClient
with SyncHeroSMSClient(api_key="YOUR_API_KEY") as client:
    balance = client.get_balance()
```
- ⚠️ 注意：即使使用官方包，如果API Key本身有问题（未激活/未充值），仍会返回 Unauthorized

**HeroSMS API端点说明**（2026-06-09 实测确认）：

HeroSMS有**两套独立的API**：

| API | 端点 | 认证方式 | 用途 |
|-----|------|----------|------|
| **Legacy** (兼容SMS-Activate) | `https://hero-sms.com/stubs/handler_api.php` | `?api_key=KEY` 查询参数 | 接码/买号/查余额 |
| **REST v1** (新版) | `https://hero-sms.com/api/v1` | `Authorization: ApiKey KEY` HTTP头 | 邮箱等新功能 |

**⚠️ 关键坑点：API Key获取方式**

HeroSMS后台可能显示多个Key，用户容易复制错误的：
- 后台仪表盘可能显示的是**账号标识/Session Token**（不是API Key）
- **真正的API Key**需要在 Profile → API设置 页面**点击"生成API Key"按钮**获取
- 点击后会弹出一个网址，显示的就是正确的32位API Key
- 如果复制了错误的Key，会一直返回 `BAD_KEY`

**BAD_KEY错误的根因**（2026-06-09 确认）：
- ❌ 不是"需要激活API权限"（不需要额外激活）
- ❌ 不是"端点不对"（端点是正确的）
- ✅ **是复制了错误的Key**（仪表盘Key ≠ API Key）
- ✅ 或者账户余额为0（但错误信息会是 `NO_BALANCE`，不是 `BAD_KEY`）

**正确配置后的验证**：
```python
import requests
r = requests.get('https://hero-sms.com/stubs/handler_api.php', 
    params={'api_key': '正确Key', 'action': 'getBalance'})
# 成功响应: ACCESS_BALANCE:3
```

**白嫖攻略（GPT/Gemini免费方案）**：见 `references/gpt-gemini-free-strategies.md`

**详细搭建记录**：见 `references/register-gpt-v0-setup.md`

**HeroSMS API完整参考**：见 `references/herosms-api-reference.md`（含两套API说明、Key获取方式、错误码、Python客户端用法）

**Hotmail007邮箱服务配置**：见 `references/hotmail007-setup.md`（账号信息、API端点、邮箱类型、Register_GPT_v0配置方法）

### 完整验证流程（2026-06-09 实测）

搭建完成后，按以下步骤验证系统可用性：

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

---

## 完整注册所需配置（2026-06-09 确认）

Register_GPT_v0 完整注册流程需要以下配置，仅配置HeroSMS不足以完成注册：

| 配置项 | 状态 | 用途 | 需要什么 |
|--------|------|------|----------|
| 手机号接码 API | ✅ 已完成 | 获取手机号验证 | HeroSMS API Key |
| 代理 IP | ⚠️ 默认 | 避免风控 | 美国住宅IP |
| 邮箱 API | ❌ 未配置 | 获取邮箱用于注册 | Hotmail007 Client Key |
| 打码 API | ❌ 未配置 | 解决hCaptcha验证码 | 2Captcha API Key |
| OAuth | ❌ 未配置 | 自动获取Token | OpenAI OAuth Client ID |
| 银行卡 API | ❌ 可选 | Plus订阅 | 银行卡API |

### Web界面设置页面

登录 http://localhost:1989 → 系统设置，包含以下配置卡片：

1. **手机号接码 API** — HeroSMS配置（已就绪）
2. **邮箱 API** — Hotmail007（需Client Key）
3. **银行卡 API** — 可选，用于Plus订阅
4. **代理 IP** — 单代理地址或代理API
5. **打码 API** — 2Captcha（解决hCaptcha）
6. **OAuth / 注册换 Token** — OAuth Client ID + Redirect URI
7. **运行参数** — 线程数、重试次数、每卡使用次数

### 数据库表结构

完整的注册流程涉及以下表：

| 表名 | 用途 | 需要数据 |
|------|------|----------|
| `accounts` | 已注册账号 | 系统自动写入 |
| `emails` | 邮箱池 | **需要先填充**（从Hotmail007拉取） |
| `phone_numbers` | 手机号池 | 从HeroSMS获取 |
| `run_logs` | 运行日志 | 系统自动写入 |
| `system_settings` | 系统配置 | 需要配置 |

### 注册流程（完整）

```
1. 从Hotmail007拉取邮箱 → emails表
2. 从HeroSMS获取手机号 → phone_numbers表
3. 调用protocol_register.py执行注册
4. 包含：邮箱验证 + 手机验证 + OAuth Token获取
5. 成功 → accounts表
6. 可选：激活Sora/Plus
```

### 服务管理

清理不必要的后台进程：

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

**保留的核心服务**：
- Register_GPT_v0 Web服务 (端口1989)
- Hermes Agent Gateway (shanli)
- Hermes Agent Gateway (default)

**可选服务**（按需保留）：
- Hermes Dashboard (端口9119)
- oMLX Server (端口8801)
- MCP SQLite Server

### 🥈 备选：openai_register（TempMail.lol版，2026年成功率低）

**优点**：
- ✅ 功能最全面（DuckMail + OAuth + Sub2Api）
- ✅ Web管理界面
- ✅ 自动上传Token

**缺点**：
- ❌ 需要DuckMail API Token

**位置**：`AI-Account-Toolkit/GPT_register+duckmail+CPA+autouploadsub2api/`

---

## 搭建流程

### 1. 克隆项目

```bash
mkdir -p ~/Desktop/GPT账号管理系统
cd ~/Desktop/GPT账号管理系统
git clone https://github.com/adminlove520/AI-Account-Toolkit.git
```

### 2. 安装依赖

```bash
# 主要依赖
pip3 install curl_cffi

# Register_GPT_v0（需要Python 3.10+）
cd AI-Account-Toolkit/Register_GPT_v0
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r web/backend/requirements.txt
uv pip install requests  # 注意：requirements.txt遗漏此依赖

# 启动Web服务
cd web && python3.11 run_web.py
# 访问 http://localhost:1989

# 如果使用openai_pool_orchestrator
cd AI-Account-Toolkit/openai_pool_orchestrator-V6
uv sync  # 或 pip install -e .
```

### 3. 配置代理

在代码或配置文件中设置代理地址：
```python
PROXY_URL = "http://127.0.0.1:7890"  # Clash默认端口
```

### 4. 运行测试

```bash
# 测试openai_register
cd ~/Desktop/GPT账号管理系统/AI-Account-Toolkit/openai_register
python3 register-openai.py
```

---

## 常见问题

### 问题0：Register_GPT_v0 搭建失败（TypeError / ModuleNotFoundError）

**错误信息**：
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
ModuleNotFoundError: No module named 'requests'
```

**原因**：Register_GPT_v0 使用 Python 3.10+ 语法（`str | None`），系统默认 Python 3.9 不支持

**解决方案**：
# Register_GPT_v0（需要Python 3.10+）
cd AI-Account-Toolkit/Register_GPT_v0
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r web/backend/requirements.txt
uv pip install requests  # 注意：requirements.txt遗漏此依赖

# 启动Web服务
cd web && python3.11 run_web.py
# 访问 http://localhost:1989
cd web && python3.11 run_web.py
```

**坑点**：
- 启动脚本在 `web/run_web.py`，不是 `web/backend/run_web.py`
- uv管理的Python不能用 `pip install`，必须用 `uv pip install`
- `requirements.txt` 遗漏了 `requests`，需单独安装

### 问题1：注册失败（状态码400）

**错误信息**：
```
Failed to create account. Please try again.
account_creation_failed
```

**原因**：OpenAI加强了注册风控

**解决方案**：
1. 更换为美国住宅IP
2. 使用DuckMail替代mailtm
3. 手动注册一个账号

### 问题2：代理连接失败

**错误信息**：
```
Connection refused to proxy 127.0.0.1:7897
```

**原因**：代理端口不正确

**解决方案**：
1. 检查代理软件（Clash/V2Ray）的端口配置
2. 常见端口：7890（Clash）、1080（V2Ray）
3. 在Web界面中点击"检测"验证代理可用性

### 问题3：DuckMail需要API Token

**解决方案**：
1. 注册DuckMail账号获取API Token
2. 或使用TempMail.lol（不需要Token）
3. 或使用mailtm（免费但可能被识别）

---

## 账号池管理

### OpenAI Pool Orchestrator V6

**功能**：
- 自动化注册
- 多平台同步（Sub2Api/CPA）
- 代理池管理
- 账号维护
- Web管理界面

**启动方法**：
```bash
cd ~/Desktop/GPT账号管理系统/AI-Account-Toolkit/openai_pool_orchestrator-V6
uv run python run.py
# 访问 http://localhost:18421
```

**配置文件**：`config/sync_config.json`

---

## Token提取与使用

### 手动注册后提取Token

1. 在浏览器中登录ChatGPT
2. 打开开发者工具（F12）
3. 在Application → Cookies中找到`oai-client-auth-session`
4. 使用工具提取access_token和refresh_token

### Token存储

注册成功的Token保存到：
- `accounts.json`（openai_register）
- `registered_accounts.txt`（chatgpt_register_duckmail）
- `codex_tokens/`（GPT_register+duckmail+CPA）

---

## 参考资源

- **AI-Account-Toolkit**：https://github.com/adminlove520/AI-Account-Toolkit
- **openai_register**：TempMail.lol版，不需要API Token
- **chatgpt_register_duckmail**：DuckMail版，需要API Token
- **openai_pool_orchestrator-V6**：完整的账号池管理系统

---

## 注意事项

⚠️ **风险提示**：
- 批量注册账号可能违反OpenAI服务条款
- 账号可能被封禁
- 请遵守当地法律法规
- 仅供学习和研究使用

⚠️ **2026年现状**：
- OpenAI加强了注册风控
- 自动化注册成功率下降
- 建议优先考虑手动注册
