---
name: cross-platform-networking
description: |
  Configure Mac ↔ Windows LAN file sharing (SMB), remote desktop (RDP/VNC),
  and network diagnostics. Covers macOS launchctl service management,
  sharing command, Windows PowerShell firewall/share config, and
  cross-platform port testing. Trigger when user asks to: set up file sharing
  between Mac and Windows, enable remote desktop, configure VNC, troubleshoot
  LAN connectivity, or make two machines see each other on the same network.
version: 1.2.0
platforms: [macos, windows]
metadata:
  hermes:
    tags: [networking, smb, vnc, rdp, lan, file-sharing, remote-desktop, mac, windows]
    category: devops
    related_skills: [macos-computer-use]
---

# Cross-Platform LAN Networking

Configure Mac ↔ Windows file sharing and remote control on the same LAN.

## Quick Reference

See `references/smb-chinese-file-operations.md` for Chinese filename handling in smbclient.

| Need | Mac side | Windows side |
|------|----------|-------------|
| Win accesses Mac files | Enable SMB via `sharing` + start smbd | `\\MacIP\ShareName` |
| Mac accesses Win files | `smb://WinIP\ShareName` in Finder | Enable folder sharing + firewall |
| Mac controls Win | Install Windows App / MS Remote Desktop | Enable RDP (Pro+ only) |
| Win controls Mac | — | Install VNC Viewer, connect to MacIP |

## macOS Service Management

### Start/stop SMB and Screen Sharing

```bash
# Start SMB
sudo launchctl kickstart -k system/com.apple.smbd

# Start Screen Sharing (VNC)
sudo launchctl kickstart -k system/com.apple.screensharing

# Check service status
launchctl print system/com.apple.smbd
launchctl print system/com.apple.screensharing
```

### Manage Share Points

```bash
# List shares
sharing -l

# Add a share (requires sudo)
sudo sharing -a /path/to/folder -S "ShareName" -n "ShareName"

# Remove a share
sudo sharing -r "ShareName"
```

### Verify Ports Are Listening

```bash
# Check SMB (445) and VNC (5900)
netstat -an | grep -E "445|5900"

# Also check SMB netbios (139)
netstat -an | grep 139
```

**Pitfall**: `lsof -c smbd -i` may NOT show smbd's ports even when the
service is running. This is because macOS uses launchd socket activation —
launchd holds the socket and passes it to the service. Use `netstat -an`
instead of `lsof` to verify ports.

### smbclient cd Command Fails on Chinese/Spaced Directories
**Symptom**: `smbclient -c 'cd 目录名'` 报 `NT_STATUS_OBJECT_NAME_NOT_FOUND`。
**Cause**: smbclient的`cd`命令对中文+空格的目录名支持不好。
**Fix**: 用`-D`参数直接设置初始目录，不用cd：
```bash
# ❌ 错误
smbclient //server/share -U user -c 'cd 电子书/目录名; ls'

# ✅ 正确
smbclient //server/share -U user -D '电子书/目录名' -c 'ls'
```
**批量下载**: `mget *.md` 配合 `-D`：
```bash
smbclient //server/share -U 'user%pass' -D '远程/路径' -c "lcd '$PWD'; prompt off; mget *.md; mget *.csv"
```

### macOS Firewall

```bash
# Check if firewall is on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# List apps with firewall rules
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
```

smbd typically appears in the app list. If not, the firewall may block
SMB connections.

## Windows Configuration (via PowerShell)

### Check/Set Network to Private

```powershell
Get-NetConnectionProfile
# If not Private:
Set-NetConnectionProfile -InterfaceAlias "Ethernet" -NetworkCategory Private
```

### Enable File Sharing Firewall Rules

```powershell
# Requires admin elevation
Enable-NetFirewallRule -DisplayGroup "文件和打印机共享"
Enable-NetFirewallRule -DisplayGroup "网络发现"
Enable-NetFirewallRule -DisplayGroup "远程桌面"
```

**Pitfall**: `Start-Process powershell -Verb RunAs -ArgumentList "-Command", "..."` spawns
a new elevated process that may fail silently or not apply rules properly.
Better to run PowerShell as Administrator directly, or verify via UI:
Settings → System → Remote Desktop → confirm toggle is ON.

### Create SMB Share

```powershell
New-SmbShare -Name 'SharedFolder' -Path 'C:\SharedFolder' -FullAccess 'Everyone'
```

### Enable RDP

```powershell
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0
```

**Critical**: Windows 11 Home cannot act as RDP host. Must be Pro/Enterprise/Education.

## Cross-Platform Port Diagnostics

Test in this order:

```bash
# 1. Basic connectivity
ping -c 3 <target_ip>

# 2. Specific port (SMB, RDP, VNC)
nc -zv <target_ip> 445    # SMB
nc -zv <target_ip> 3389   # RDP
nc -zv <target_ip> 5900   # VNC

# 3. All listening ports on local machine
netstat -an | grep LISTEN
```

## Programmatic SMB Testing (Python)

macOS doesn't ship `smbclient`. Use Python's `smbprotocol` library to
test SMB connections programmatically — useful for diagnosing auth issues.

```python
# Install: pip3 install smbprotocol
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
import uuid

conn = Connection(uuid.uuid4(), "192.168.1.2", 445)
conn.connect()  # TCP test
session = Session(conn, username="user", password="pass")
session.connect()  # Auth test
tree = TreeConnect(session, "\\\\192.168.1.2\\SharedFolder")
tree.connect()  # Share access test
```

**Diagnostic value:**
- `Connection refused` → port closed or firewall blocking
- `STATUS_LOGON_FAILURE (0xc000006d)` → wrong username/password
- `STATUS_ACCESS_DENIED (0xc0000022)` → share permissions issue
- `STATUS_BAD_NETWORK_NAME (0xc00000cc)` → share name doesn't exist

**Pitfall**: `mount_smbfs` on macOS may fail with "Authentication error"
even when credentials are correct. Use this Python approach or `smbclient` to
isolate whether the issue is network, auth, or share-level. If Python/
smbclient succeed but `mount_smbfs` doesn't, the issue is Apple's SMB
stack — see `references/macos-smb-troubleshooting.md`.

## 批量下载中文目录中的文件（smbclient -D 方案）

**问题：** smbclient的`cd`命令在处理中文目录名+空格时会失败（NT_STATUS_OBJECT_NAME_NOT_FOUND）。

**解决：** 用`-D`参数设置初始目录，绕过cd的路径解析问题：

```bash
# ❌ 这样会失败
smbclient '//server/share' -U 'user%pass' -c 'cd 电子书/毛泽东集/子目录; ls'

# ✅ 用-D设置初始目录
smbclient '//server/share' -U 'user%pass' -D '电子书/毛泽东集/子目录' -c 'ls'
smbclient '//server/share' -U 'user%pass' -D '电子书/毛泽东集/子目录' -c 'prompt off; mget *.md'
```

**批量下载脚本模式：**
```bash
DIRS=("目录1" "目录2" "目录3")
for dir in "${DIRS[@]}"; do
  smbclient '//server/share' -U 'user%pass' \
    -D "父目录/$dir" \
    -c "lcd '$PWD'; prompt off; mget *.md" 2>&1 | grep "getting"
done
```

**关键参数：**
- `-D path`：设置初始目录（绕过cd的中文路径问题）
- `prompt off`：关闭确认提示（批量下载必须）
- `mget *.md`：批量下载匹配的文件
- `lcd localdir`：设置本地下载目录

**⚠️ 注意：** smbclient shell模式（heredoc/pipe）在脚本中不稳定，用`-c`参数传命令更可靠。

## Common Failure Patterns

1. **SMB share visible but can't write**: Check both "Share permissions"
   AND "NTFS Security permissions" on Windows. Both must allow write.

2. **RDP port timeout**: Windows firewall rules enabled via PowerShell
   may not actually apply. Confirm via Settings → System → Remote Desktop
   toggle in the UI. Network must be "Private".

3. **lsof shows no ports but netstat does**: Normal on macOS with launchd
   socket activation. Use netstat to verify.

4. **VNC connection refused**: Ensure screensharingd is running AND the
   VNC password is set (via Screen Sharing settings or ARDAgent kickstart).

5. **Different subnets**: Machines must be in the same /24 (e.g., both
   192.168.1.x). Check with `ifconfig` (Mac) or `ipconfig` (Windows).

6. **SMB auth error even with correct password**: Windows "Password
   protected sharing" must be OFF (Control Panel → Network and Sharing
   Center → Advanced sharing settings → All networks → turn off password
   protection). Also ensure Guest account is enabled if using anonymous
   access.

7. **Finder stuck on old SMB connection**: macOS Finder may cache stale
   SMB connections. If `open smb://...` fails but Python smbprotocol
   succeeds, reset Finder:
   ```bash
   killall -9 Finder  # Force restart Finder
   # Then re-open the connection
   open smb://192.168.1.2/SharedFolder
   ```
   **Root cause**: Finder's SMB client may hold onto a cached session
   that has gone stale, while the underlying network is fine.

8. **Microsoft account username format**: When Windows uses a Microsoft
   account (e.g., `user@outlook.com`), SMB authentication often works with
   just the **local part** (`user`) instead of the full email. Try the
   local part first — `mount_smbfs` can't handle `@` in the username field
   (URL parsing error 64). Verify with `smbclient` before assuming wrong
   password. If neither works, create a local Windows account for SMB.

9. **Apple SMB stack vs smbclient divergence**: When `smbclient` (from
   Homebrew Samba) authenticates successfully but `mount_smbfs`/Finder
   fails with "Authentication error" (exit 77), the problem is Apple's
   **Pitfall**: Apple's SMB stack incompatibility — NOT wrong credentials. Do not keep retrying
   different username formats. Instead:
   - Check `/etc/nsmb.conf` for `min_auth=ntlm` (blocks NTLMv2 with
     modern Windows — change to `ntlmv2`)
   - Debug with: `log show --predicate 'process == "NetAuthSysAgent"' --last 2m`
   - Use `smbclient` as a working fallback for file operations
   - As last resort: install MacFUSE with a third-party SMB mount tool

10. **SMB signing blocks macOS native mount**: Windows SMB signing
    (`RequireSecuritySignature`) may be enabled by default. smbclient
    handles it, but `mount_smbfs`/Finder often fail the negotiation.
    Disable on Windows: `Set-SmbServerConfiguration -RequireSecuritySignature $false -Force`

### macOS SMB Debugging

```bash
# Real-time auth log — shows actual error codes during mount attempts
log show --predicate 'process == "NetAuthSysAgent"' --last 2m --style compact

# Force nsmb.conf reload after config changes
killall NetAuthSysAgent
```

### smbclient Shell Mode Pitfalls (2026-06-26)

**Problem:** `smbclient` interactive shell mode (`-c 'cd dir; ls'`) fails with Chinese character paths and spaces. The `cd` command returns `NT_STATUS_OBJECT_NAME_NOT_FOUND` even when the directory exists.

**Root Cause:** smbclient's path handling breaks with mixed encoding (Chinese + ASCII + spaces).

**Solution:** Use `-D` flag to set initial directory instead of `cd`:
```bash
# ❌ BROKEN — cd fails with Chinese paths
smbclient '//server/share' -U 'user%pass' -c 'cd 电子书/毛泽东集; ls'

# ✅ WORKS — use -D to set initial directory
smbclient '//server/share' -U 'user%pass' -D '电子书/毛泽东集' -c 'ls'

# ✅ WORKS — download files from specific directory
smbclient '//server/share' -U 'user%pass' -D '电子书/毛泽东集/子目录' \
  -c 'lcd /local/dir; prompt off; mget *.md'
```

**For recursive downloads:** Use `winshare` script pattern (~/bin/winshare) or Python smbprotocol library. The `recurse on; mget` pattern works but requires correct initial directory via `-D`.

**Known working credentials format:** `//IP/共享文件` with `username%password`

User-level nsmb.conf at `~/Library/Preferences/nsmb.conf` (no sudo needed)
overrides system-wide `/etc/nsmb.conf`. Server-specific sections like
`[192.168.1.2]` take precedence over `[default]`.

## FUSE-based SMB Mount (when native mount_smbfs fails)

When Apple's SMB stack (mount_smbfs / Finder) is incompatible with the Windows server, use FUSE to mount via third-party SMB libraries that handle the protocol correctly.

### MacFUSE Installation

1. Download from https://github.com/macfuse/macfuse/releases
2. Install the .pkg
3. Approve the kernel extension in System Settings → Privacy & Security
4. Install the Python bindings:
   ```bash
   pip3 install fuse-python
   ```

### FUSE Mount

```bash
# Create mount point
mkdir -p /Volumes/WindowsShare

# Mount using Python FUSE
python3 -c "
import fuse, smbclient
fuse.FUSE(smbclient.SMBFS('//user:pass@192.168.1.2/ShareName'), '/Volumes/WindowsShare', foreground=True)
"
```

### ⚠️ MiMo Code协议族注意
MiMo Code基于OpenCode开发，创建Multica自定义runtime profile时协议族必须选`opencode`而非`claude`。

## SMB文件下载（smbclient -D模式）

当smbclient的cd命令因中文路径失败时，用`-D`参数设置初始目录：

```bash
# ❌ cd会失败（中文路径+空格）
smbclient '//server/share' -U 'user%pass' -c 'cd 电子书/毛泽东集; ls'

# ✅ 用-D设置初始目录
smbclient '//server/share' -U 'user%pass' \
  -D '电子书/毛泽东集' -c 'ls'

# ✅ 批量下载MD文件
smbclient '//server/share' -U 'user%pass' \
  -D '电子书/毛泽东集/子目录' \
  -c 'lcd /本地路径; prompt off; mget *.md'
```

**原理：** `-D`在连接时就切换到目标目录，绕过了cd命令对中文路径的解析问题。
Windows server, use FUSE to mount via third-party SMB libraries that
handle the protocol correctly.

### Prerequisites

```bash
# 1. Install macFUSE (kernel extension + headers)
# Download DMG from: https://github.com/macfuse/macfuse/releases
# Or: curl -LO https://github.com/macfuse/macfuse/releases/download/macfuse-5.2.0/macfuse-5.2.0.dmg
# Double-click .pkg, then approve kext in System Settings → Privacy & Security

# 2. Install pkg-config (needed by fuse-python)
brew install pkg-config

# 3. Install fuse-python (with CFLAGS workaround for macFUSE 5.x API changes)
PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
CFLAGS="-Wno-error=incompatible-function-pointer-types" \
pip3 install fuse-python

# 4. Install smb-pyfuse (uses smbprotocol, already verified working)
pip3 install smb-pyfuse
```

### Mount

```bash
export PATH="$PATH:$HOME/Library/Python/3.9/bin"
mkdir -p /tmp/smb_mount
smb-pyfuse mount -u USERNAME -p PASSWORD /tmp/smb_mount SERVER_IP SHARE_NAME
```

**Pitfall**: `smb-pyfuse` entry script may be broken — fix with:
```bash
sed -i '' 's/from main import main/from smb_pyfuse.__main__ import main/' \
  ~/Library/Python/3.9/bin/smb-pyfuse
```

**Pitfall**: `fuse-python` 1.0.9 fails to compile with macFUSE ≥5.0 due to
incompatible function pointer types in `getxattr`/`setxattr`. The CFLAGS
workaround above suppresses the error. `pyfuse3` is Linux-only (requires
`<linux/fs.h>`).

**Pitfall**: Pip may fail with SSL errors on Pypi CDN from mainland China.
Use Tsinghua mirror: `pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple <pkg>`

### smbclient command-line fallback

If FUSE mounting is blocked (kernel extension not approved), use
`smbclient` (Homebrew Samba) for file operations — it handles all SMB
protocol versions correctly and doesn't need FUSE:

```bash
# Install: brew install samba
# List shares
smbclient -L //server -U 'user%password'
# List files
smbclient '//server/share' -U 'user%password' -c 'ls'
# Download
smbclient '//server/share' -U 'user%password' -c 'get remote_file /local/path'
# Upload
smbclient '//server/share' -U 'user%password' -c 'put /local/file remote_name'
```

## References

See `references/macos-services.md` for detailed macOS launchctl commands.
See `references/macos-smb-troubleshooting.md` for nsmb.conf configuration,
diagnostic workflow, and error code reference.
See `references/macos-smb-fuse-mount.md` for complete FUSE setup recipe,
error transcripts, and smbclient file operation examples.
