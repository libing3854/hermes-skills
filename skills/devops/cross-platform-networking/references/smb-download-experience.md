# SMB文件下载经验 (2026-06-26)

## 问题
smbclient的cd命令在处理中文路径+空格时失败：`NT_STATUS_OBJECT_NAME_NOT_FOUND`

## 解决方案
用`-D`参数设置初始目录，绕过cd解析问题。

```bash
# 基本用法
smbclient '//192.168.1.2/共享文件' -U '用户名%密码' \
  -D '电子书/毛泽东集' -c 'ls'

# 批量下载
smbclient '//192.168.1.2/共享文件' -U '用户名%密码' \
  -D '电子书/毛泽东集/子目录' \
  -c 'lcd /本地路径; prompt off; mget *.md'
```

## 实战：下载永乐大典
- 13个子目录，每个1个MD文件+1个CSV索引
- 总计66万字，来自1960年影印本PDF的AI OCR转录
- 目标目录：`/Users/libing/Desktop/临时文件-0001/知识库/永乐大典/`

## Windows共享信息
- IP: 192.168.1.2
- 共享名: 共享文件
- 用户名: [REDACTED]
- 密码: 1472...HARE（见~/bin/winshare脚本）
- 已有winshare命令：`~/bin/winshare ls/cd/get/put/shell`

## 注意
- smbclient shell模式在脚本中不可靠，避免用heredoc
- `-D`是关键参数，解决了中文路径问题
- 下载大文件时注意超时，可能需要分批
