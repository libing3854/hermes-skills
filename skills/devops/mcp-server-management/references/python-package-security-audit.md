# Python包安全审查清单

安装任何新的Python包前，按此清单检查：

## 1. setup.py / pyproject.toml
- 检查install_requires是否有可疑依赖
- 检查是否有自定义的install命令（cmdclass）
- 检查entry_points是否有隐藏的命令

## 2. 网络调用
```bash
# 检查是否有外部网络调用
grep -rn "requests\.\|urllib\.\|httpx\.\|aiohttp\.\|socket\." <package>/ --include="*.py"

# 检查硬编码的URL
grep -rn "https\?://" <package>/ --include="*.py" | grep -v "github.com\|docs\|readme"
```

## 3. 数据收集/遥测
```bash
# 检查是否有telemetry
grep -rn "telemetry\|analytics\|tracking\|phone_home\|posthog\|umami" <package>/ --include="*.py"

# 检查是否有opt-out机制
grep -rn "opt.out\|disable\|CLAUDE_TELEMETRY\|DO_NOT_TRACK" <package>/ --include="*.py"
```

## 4. 代码执行
```bash
# 检查是否有subprocess调用
grep -rn "subprocess\.\|os\.system\|os\.popen\|eval\|exec" <package>/ --include="*.py"

# 检查是否读取敏感文件
grep -rn "open.*\.env\|open.*credentials\|open.*token" <package>/ --include="*.py"
```

## 5. 依赖链
```bash
# 检查依赖树
pip show <package>
pipdeptree -p <package>  # 如果安装了pipdeptree
```

## 6. 社区信任
- GitHub stars (>1000相对可信)
- 最近提交时间（活跃维护）
- Issue数量和响应速度
- 是否有已知CVE

## 7. 安装建议
```bash
# 关闭遥测安装
CLI_HUB_ANALYTICS=off pip install <package>
DO_NOT_TRACK=1 pip install <package>

# 或用环境变量
export DO_NOT_TRACK=1
```
