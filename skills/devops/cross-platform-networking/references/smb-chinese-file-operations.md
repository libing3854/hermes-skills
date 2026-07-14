# SMB中文文件名操作

## 问题
smbclient的`cd`命令在处理中文路径时可能失败（NT_STATUS_OBJECT_NAME_NOT_FOUND），
但`-D`参数（设置初始目录）可以正常工作。

## 解决方案：用-D参数代替cd

```bash
# ❌ cd方式会失败
smbclient '//192.168.1.2/共享文件' -U 'user%pass' -c 'cd 电子书/毛泽东集; ls'

# ✅ -D方式正常
smbclient '//192.168.1.2/共享文件' -U 'user%pass' -D '电子书/毛泽东集/转换结果_永乐大典' -c 'ls'
```

## 批量下载中文目录中的文件

```bash
# 列出所有子目录
smbclient '//192.168.1.2/共享文件' -U 'user%pass' -D '电子书/毛泽东集/转换结果_永乐大典' -c 'ls'

# 进入子目录下载文件（-D+ls+prompt off+mget）
smbclient '//192.168.1.2/共享文件' -U 'user%pass' \
  -D '电子书/毛泽东集/转换结果_永乐大典/001_永乐大典 卷之一万三千八百七十八' \
  -c 'lcd /local/path; prompt off; mget *.md; mget *.csv'
```

## 批量脚本模板

```bash
DIRS=(
"001_永乐大典 卷之一万三千八百七十八"
"002_永乐大典 卷之一万三千八百八十"
# ... 更多目录
)

for dir in "${DIRS[@]}"; do
  echo "下载: $dir"
  smbclient '//192.168.1.2/共享文件' -U 'user%pass' \
    -D "远程根目录/$dir" \
    -c "lcd '$PWD'; prompt off; mget *.md" 2>&1 | grep "getting"
done
```

## 注意事项
- smbclient的`-D`参数比`cd`命令更可靠处理中文路径
- Python smbprotocol的`AccessMask`不在`smbprotocol.open`中，用原始int值代替
- smbclient的shell模式在脚本中不好用（heredoc/piping有问题），用`-c`参数更可靠
- 大文件下载用`smbclient -c 'get'`逐个下载，不要用mget大批量
