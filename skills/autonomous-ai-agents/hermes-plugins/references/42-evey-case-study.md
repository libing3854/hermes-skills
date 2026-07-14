# 真实审查案例：42-evey/hermes-plugins

审查日期：2026-05-26

## 项目概况
- 仓库：https://github.com/42-evey/hermes-plugins
- 类型：23 个 Hermes Agent 自定义插件合集
- 作者：42-evey (evey@evey.cc)，单人项目
- 代码量：35 个 Python 文件，7,529 行代码，单个 commit
- 许可：README 写 MIT，LICENSE 文件为 AGPL-3.0

## 五维度审查

### 来源 🟡
- 单人开发者，无社区 review
- 列入 Hermes Atlas 社区目录
- 作者运行完整的 "Evey" 自主 AI Agent 栈

### 代码 🟡
- 零 eval()/exec()/os.system() — 全代码零动态执行
- 零数据外发 — telemetry 仅写本地 JSONL 文件
- evey-sandbox 名不副实：描述说 Docker 沙箱，实际是文件读取器
- evey-wallet 硬编码加密货币捐款地址（不影响安全，但代码风格不佳）

### 依赖 🟢
- 零强制外部依赖，全部使用 Python 标准库
- 可选依赖：PyYAML（配置解析），paho-mqtt（MQTT 连接）
- 无 pip install 即可运行，供应链风险极低

### 许可 🔴
- README 写 MIT，LICENSE 文件为 AGPL-3.0
- AGPL-3.0：网络服务也触发开源义务
- 个人使用 OK，商业闭源有障碍

### 权限 🟡
- 各插件权限有限：文件读写 ~/.hermes/ 下本地文件
- 部分插件需环境变量（API Key）
- 无 sudo/root 权限
- evey-commands 唯一使用 subprocess（仅执行 docker ps）

## 结论：🟡 谨慎安装
代码干净无恶意，但 AGPL 许可冲突和单人维护是主要关注点。
