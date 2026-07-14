# Windows SMB文件访问

## 连接信息
- Windows IP: 192.168.1.2
- 共享名: 共享文件
- 用户名: [REDACTED]
- 密码: [REDACTED]

## winshare命令（已安装）
```bash
~/bin/winshare ls              # 列出根目录
~/bin/winshare cd 电子书        # 列出子目录
~/bin/winshare get 远程/文件 本地路径  # 下载
~/bin/winshare put 本地文件 远程路径  # 上传
~/bin/winshare shell           # 交互模式
```

## 已知内容
电子书/目录下有：
- 毛泽东集（1-10卷PDF + 选集 + 转换结果）
- 永乐大典（1960年影印本PDF → OCR转录MD，13卷）
- 各类PDF电子书

## 批量下载（smbclient -D模式）
```bash
smbclient '//192.168.1.2/共享文件' -U '[REDACTED]%[REDACTED]' \
  -D '电子书/毛泽东集/转换结果_永乐大典/子目录名' \
  -c 'lcd /本地目录; prompt off; mget *.md; mget *.csv'
```

## 注意
- smbclient的`cd`命令对中文路径不可靠，用`-D`代替
- 批量下载用`prompt off; mget`模式
