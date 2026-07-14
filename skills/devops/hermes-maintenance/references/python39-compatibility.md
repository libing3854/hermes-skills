# Python 3.9 兼容性陷阱

**发现时间：** 2026-06-28

## 问题

macOS自带的Python 3.9（`/usr/bin/python3`）不支持现代Python语法：
- `X | None` 类型注解（需3.10+）
- `match/case` 语句（需3.10+）
- 部分`typing`模块新特性

多个现代包已要求Python 3.10+：
- crawl4ai（网页抓取）
- mem0ai（记忆层）
- sentence-transformers（embedding）
- cli-anything-hub（CLI工具管理）
- mcp（Model Context Protocol SDK）

## 诊断

```bash
python3 --version  # 如果是3.9.x就需要换
python3.12 --version  # 确认3.12可用
```

## 解决

用Python 3.12安装和运行：
```bash
# 安装包
python3.12 -m pip install --break-system-packages <package>

# 运行脚本
python3.12 script.py

# 运行模块
python3.12 -m <module>
```

## Python 3.12路径

```
/opt/homebrew/bin/python3.12
```

## 注意

- `--break-system-packages` 是必需的（PEP 668保护）
- 如果用venv可以跳过这个flag
- Python 3.14也已安装但部分包可能不兼容
- pip安装的包在 `/opt/homebrew/lib/python3.12/site-packages/`
