# Cron 终端环境完全无响应故障排查

> 陷阱 #19 (v2.9.4+, 2026-06-26)

## 现象

在 cron 任务运行期间，所有 `terminal` 工具调用（包括最简的 `date`、`/bin/echo`、`true`）均 30s 超时返回，无任何输出。

与此形成对比的是，文件类工具（`read_file`、`write_file`、`search_files`、`patch`）正常工作，因为它们绕过 shell 进程，直接操作文件系统。

## 根因

Hermes 的 `terminal` 工具底层依赖 shell（bash）环境执行命令。终端 session 因以下原因可能进入"僵死"状态：

1. **后台进程僵尸**：之前的 cron 任务留下未退出的后台进程，占用 shell session
2. **pty 分配失败**：cron 系统中伪终端资源耗尽
3. **Shell 启动延迟**：cron 环境中 bash 启动脚本（`.bashrc`/`.profile`）耗时过长或挂起
4. **进程泄漏**：Hermes 自身的 shell 子进程在任务完成后未正确回收

## 诊断步骤

### Step 1: 确认故障范围

```
terminal("date", timeout=5)  → TIMEOUT → 终端故障（非脚本问题）
terminal("echo test", timeout=5)  → TIMEOUT → 确认
write_file("/tmp/test.txt", "hello")  → SUCCESS → 文件工具正常
```

如果 Step 1 确认所有终端命令超时但文件工具正常 → 进入应对策略

### Step 2: 检查现有资源

```
write_file("/tmp/check.sh", """
import os
# 检查缓存文件状态
cache = '/Users/libing/Desktop/美股总结/.finance_cache.json'
if os.path.exists(cache):
    print(f'Cache: EXISTS, mtime={os.path.getmtime(cache)}')
else:
    print('Cache: NOT FOUND')

# 检查最近的HTML
out = '/Users/libing/Desktop/美股总结'
htmls = [f for f in os.listdir(out) if f.startswith('金融看板_v5_')]
htmls.sort(reverse=True)
if htmls:
    print(f'Latest HTML: {htmls[0]}')
""")
terminal("python3 /tmp/check.sh") → may TIMEOUT but worth trying
```

### Step 3: 验证脚本未挂起

```
# 通过 file tools 读取 gen_v5.py 确认 fetch_data 状态
read_file(".../gen_v5.py", offset=229, limit=5)
# 如果 fetch_data = True 且未注释 → 可能已死循环
```

### Step 4: 安全清理僵死进程（Hermes 内置工具）

```
process(action='list')
# 如果找到 gen_v5.py 进程:
process(action='kill', session_id='...')
```

## 应对策略

### A. 终端故障时的降级执行流

```
# 1. 写入修改脚本
write_file("/tmp/patch_fetch.py", patch_code)

# 2. 写入执行脚本
write_file("/tmp/run_gen.py", """
import subprocess, sys
result = subprocess.run(
    [sys.executable, "/path/to/gen_v5.py"],
    cwd="/Users/libing/.hermes/skills/productivity/financial-dashboard/scripts",
    capture_output=True, text=True, timeout=300
)
print(result.stdout)
print(result.stderr)
""")

# 3. 尝试 terminal 执行
terminal("python3 /tmp/run_gen.py")
# 如果依然超时 → 放弃，报告缓存兜底
```

### B. 完全放弃终端时的报告策略

```
📊 金融看板生成报告
━━━━━━━━━━━━━━━━━━━
❌ 今日生成失败：终端环境故障（非脚本问题）

| 可用文件 | 日期 | 大小 |
|---------|------|------|
| 金融看板_v5_20260625_0604.html | 6/25 | 640KB |

建议：待终端恢复后手动执行 `gen_v5.py`
```

## 区分故障类型

| 现象 | 类型 | 处理 |
|-----|------|-----|
| 脚本卡在某个 ticker，有输出后超时 | 进程运行中 | `process kill` |
| 所有命令均无输出，30s 超时 | 终端环境故障 | 切换文件工具 |
| 仅 gen_v5.py 超时，其他命令正常 | yfinance 限速 | 走缓存兜底 |

## 何时建议重试 cron

终端故障通常在 cron 重新调度后自动恢复（新的 session 分配）。如果：

-  Yesterday 的 cron 运行正常
- Today 的 cron 70%+ 终端调用超时
- 文件工具确认缓存数据完整

→ 大概率是临时性的 session/pty 泄漏，下次 cron 运行会恢复正常。

## 与陷阱 #16 的区分

陷阱 #16（yfinance 限速）：
- 脚本在**运行**中，只是慢
- 终端正常响应
- 解决：fetch_data = False 快速兜底

陷阱 #19（终端故障）：
- 脚本**无法运行**，shell 无响应
- 终端层完全卡住
- 解决：报告缓存可用，不尝试重跑
