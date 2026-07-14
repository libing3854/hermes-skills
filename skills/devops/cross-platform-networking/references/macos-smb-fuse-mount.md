# macOS SMB FUSE Mount Guide

Complete recipe for mounting Windows SMB shares on macOS via FUSE when
Apple's native SMB stack (mount_smbfs / Finder) fails.

## Why FUSE?

Apple's SMB kernel stack (`smbfs.kext`) has known incompatibilities with
modern Windows (10/11) SMB configurations:
- SMB signing negotiation failures
- NTLMv2 handshake issues with Microsoft accounts
- `OpenSession failed 80` (EAUTH) even with correct credentials

Third-party SMB libraries (Samba's libsmbclient, Python's smbprotocol)
handle the protocol correctly. FUSE bridges them into a real filesystem.

## Step 1: Install macFUSE

```bash
# Download DMG
curl -LO https://github.com/macfuse/macfuse/releases/download/macfuse-5.2.0/macfuse-5.2.0.dmg
open macfuse-5.2.0.dmg

# OR via Homebrew (may fail on sudo in non-interactive contexts)
brew install --cask macfuse
```

After installation, go to **System Settings → Privacy & Security**,
scroll to bottom, click **Allow** for the macFUSE kernel extension.
Restart if prompted.

**Verify**: `ls /usr/local/include/fuse.h` should exist.

## Step 2: Install pkg-config

```bash
brew install pkg-config
```

## Step 3: Install fuse-python

macFUSE 5.x changed the `getxattr`/`setxattr` function signatures.
fuse-python 1.0.9 needs a CFLAGS override to compile:

```bash
PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
CFLAGS="-Wno-error=incompatible-function-pointer-types" \
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple fuse-python
```

**Error if CFLAGS not used**:
```
fuseparts/_fusemodule.c:1432:2: error: incompatible function pointer types
  assigning to 'int (*)(...)' from 'int (...)'
  [-Wincompatible-function-pointer-types]
  1432 |         DO_ONE_ATTR(getxattr);
```

**Note**: `pyfuse3` is Linux-only — it requires `<linux/fs.h>`. Do not attempt.

## Step 4: Install smb-pyfuse

```bash
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple smb-pyfuse
```

**Fix broken entry point** (the packaged script imports `main` instead of
`smb_pyfuse.__main__`):

```bash
sed -i '' 's/from main import main/from smb_pyfuse.__main__ import main/' \
  ~/Library/Python/3.9/bin/smb-pyfuse
```

## Step 5: Mount

```bash
export PATH="$PATH:$HOME/Library/Python/3.9/bin"
mkdir -p /tmp/smb_mount

# Syntax: smb-pyfuse mount [-u USER] [-p PASS] <mountpoint> <server> <share>
smb-pyfuse mount -u [REDACTED] -p [REDACTED] /tmp/smb_mount 192.168.1.2 共享文件
```

Run in background (blocks otherwise). If mount succeeds, verify with `ls /tmp/smb_mount/`.

**Error "the file system is not available (1)"**: macFUSE kernel extension not approved.
Go to System Settings → Privacy & Security → Allow.

## smbclient Fallback (no FUSE needed)

When FUSE can't be installed (kext approval blocked, admin restrictions), use
`smbclient` from Homebrew Samba. It handles all protocol negotiation correctly:

```bash
brew install samba   # provides smbclient

# List shares (use local-part of Microsoft account email as username)
smbclient -L //192.168.1.2 -U '[REDACTED]%[REDACTED]'

# Browse files interactively
smbclient '//192.168.1.2/共享文件' -U '[REDACTED]%[REDACTED]'

# One-shot commands
smbclient '//server/share' -U 'user%pass' -c 'ls'
smbclient '//server/share' -U 'user%pass' -c 'cd subdir; get file.pdf /local/file.pdf'
smbclient '//server/share' -U 'user%pass' -c 'put /local/file remote_name'
smbclient '//server/share' -U 'user%pass' -c 'recurse; ls'  # recursive listing
```

## Debugging native mount failures

```bash
# Real-time SMB auth log during mount attempt
log show --predicate 'process == "NetAuthSysAgent"' --last 2m --style compact

# Key log lines to look for:
# - "OpenSession failed 80" → EAUTH, credentials rejected by Windows
# - "smb_od_dns_srv_lookup: SRV lookup returned no results" → normal for IP-based
# - "Available MechTypes: SPNEGO<NTLM>" → using SPNEGO-wrapped NTLM
```

## nsmb.conf Quick Reference

User-level config at `~/Library/Preferences/nsmb.conf` (no sudo):

```ini
[default]
signing_required=no

[192.168.1.2]
signing_required=no
protocol_vers_map=4    # 4=SMB3 only, 2=SMB2, 6=SMB2+3
min_auth=ntlmv2
```

Apply changes: `killall NetAuthSysAgent`

## Windows Side Checklist

```powershell
# Disable SMB signing requirement
Set-SmbServerConfiguration -RequireSecuritySignature $false -Force

# Check if SMB1 disabled (normal, fine)
Get-SmbServerConfiguration | Select EnableSMB1Protocol

# Verify share exists
Get-SmbShare
```

## Microsoft Account Username

When Windows uses a Microsoft account (e.g., `user@outlook.com`):
- **smbclient**: try `user` (local part) first — this works on many setups
- **mount_smbfs**: can't handle `@` in username → URL parsing error 64
- If local part fails, create a dedicated local Windows account for SMB

## FUSE was not the first choice

Before installing macFUSE, try these in order:
1. Fix nsmb.conf (`min_auth=ntlmv2`, `signing_required=no`)
2. Disable SMB signing on Windows
3. Use `smbclient` for file operations (no mount needed)
4. FUSE mount as last resort
