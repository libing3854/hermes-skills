# SMB Helper Script (winshare)

When dealing with Chinese/Unicode share names that `mount_smbfs` can't handle,
create a shell wrapper script for `smbclient`.

## The winshare Script

```bash
#!/bin/bash
SERVER="//192.168.1.2/共享文件"
AUTH='-U [REDACTED]%[REDACTED]'

case "${1:-ls}" in
    ls)    smbclient "$SERVER" $AUTH -c "ls" ;;
    cd)    smbclient "$SERVER" $AUTH -c "cd ${2:-.}; ls" ;;
    get)   smbclient "$SERVER" $AUTH -c "get \"$2\" \"${3:-.}\"" ;;
    put)   smbclient "$SERVER" $AUTH -c "put \"$2\" \"${3:-.}\"" ;;
    shell) smbclient "$SERVER" $AUTH ;;
    *)     echo "用法: winshare {ls|cd|get|put|shell}" ;;
esac
```

Install to `~/bin/winshare` and add to PATH.

## -D Flag for Subdirectory Navigation

`smbclient` `cd` command fails with Chinese directory names in interactive mode.
Use `-D` flag to set initial directory:

```bash
# Works with Chinese path
smbclient '//192.168.1.2/共享文件' -U 'user%pass' \
  -D '电子书/毛泽东集/转换结果_永乐大典/001_永乐大典 卷之一万三千八百七十八' \
  -c 'ls'
```

## Programmatic Access with Python smbprotocol

For batch downloads, use `smbprotocol` (pip3 install smbprotocol).

Key imports:
```python
from smbprotocol.open import Open, CreateDisposition, ImpersonationLevel, ShareAccess, FileDirectoryInformation
```

Key constants:
```python
FILE_LIST_DIRECTORY = 0x00120089
FILE_READ_DATA = 0x00120089
FILE_ATTRIBUTE_DIRECTORY = 0x10
```

Open.create() signature:
```python
f.create(ImpersonationLevel.Impersonation, desired_access, file_attributes,
         ShareAccess.READ, CreateDisposition.FILE_OPEN, 0)
```
