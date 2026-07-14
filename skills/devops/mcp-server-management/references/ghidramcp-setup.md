# GhidraMCP 安装指南

## 前置依赖
- **Java 21+**：`brew install openjdk@21`
- **Ghidra 12.1.2+**：从GitHub Releases下载（~546MB）

## 安装步骤

### 1. 安装Java 21
```bash
brew install openjdk@21
# 路径: /opt/homebrew/Cellar/openjdk@21/<version>/libexec/openjdk.jdk/Contents/Home
```

### 2. 下载Ghidra
```bash
# 获取最新版本URL
curl -s "https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/latest" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for a in data.get('assets', []):
    if 'PUBLIC' in a['name'] and a['name'].endswith('.zip'):
        print(a['browser_download_url'])
"
# 下载（~546MB，需5-7分钟）
curl -L -o /tmp/ghidra.zip "<url>"
unzip -q /tmp/ghidra.zip -d /Applications/
```

### 3. 配置Java路径
```bash
export JAVA_HOME=/opt/homebrew/Cellar/openjdk@21/<version>/libexec/openjdk.jdk/Contents/Home
sed -i '' "s|JAVA_HOME_OVERRIDE=|JAVA_HOME_OVERRIDE=$JAVA_HOME|" /Applications/ghidra_*/support/launch.properties
```

### 4. 安装GhidraMCP插件
```bash
# 下载预编译版本
curl -L -o /tmp/GhidraMCP.zip "https://github.com/LaurieWired/GhidraMCP/releases/download/1.4/GhidraMCP-release-1-4.zip"
mkdir -p /tmp/GhidraMCP-release
unzip -q /tmp/GhidraMCP.zip -d /tmp/GhidraMCP-release/

# 复制到Ghidra扩展目录
cp /tmp/GhidraMCP-release/*/GhidraMCP-*.zip /Applications/ghidra_*/Ghidra/Extensions/
```

### 5. 配置MCP Bridge
```bash
# 克隆bridge脚本
git clone --depth 1 https://github.com/LaurieWired/GhidraMCP.git /tmp/GhidraMCP
cp /tmp/GhidraMCP/bridge_mcp_ghidra.py ~/.hermes/mcp-servers/

# Python依赖
python3.12 -m pip install --break-system-packages -r /tmp/GhidraMCP/requirements.txt
```

### 6. MCP配置
```json
{
  "command": "python3.12",
  "args": ["/Users/libing/.hermes/mcp-servers/bridge_mcp_ghidra.py"],
  "timeout": 30
}
```

## 使用流程
1. 启动Ghidra → File → Install Extensions → 选GhidraMCP-1-4.zip
2. 重启Ghidra
3. 打开一个二进制文件（exe/so/dll）
4. 启动MCP bridge: `python3.12 ~/.hermes/mcp-servers/bridge_mcp_ghidra.py`

## Pitfalls
- Ghidra 12.1.2需要Java 21+，Java 17不够
- JAVA_HOME路径必须是`.../libexec/openjdk.jdk/Contents/Home`
- 预编译插件版本必须与Ghidra版本匹配
- bridge脚本需要Python 3.10+（mcp包要求）
