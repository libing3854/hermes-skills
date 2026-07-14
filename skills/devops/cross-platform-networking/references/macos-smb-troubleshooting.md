# macOS SMB Troubleshooting: Native Mount vs smbclient

When `mount_smbfs` / Finder fails but `smbclient` succeeds, the issue is
Apple's SMB stack, not credentials or network.

## Diagnostic Workflow (in order)

```bash
# 1. Network
ping -c 3 <ip>
nc -zv <ip> 445

# 2. Enumerate shares (smbclient from Homebrew: brew install samba)
smbclient -L //<ip> -U 'user%password'

# 3. Try native mount
/sbin/mount_smbfs -N '//user:password@<ip>/ShareName' /tmp/mountpoint

# 4. Check system auth logs (error 80 = EAUTH)
log show --predicate 'process == "NetAuthSysAgent"' --last 2m --style compact | grep -E 'OpenSession|MechType'

# 5. If smbclient works but mount_smbfs doesn't → Apple SMB stack incompatibility
```

## nsmb.conf — macOS SMB Client Configuration

Two locations (both read, server-specific in user file overrides system):

| File | Scope | Needs sudo |
|------|-------|------------|
| `/etc/nsmb.conf` | System-wide | Yes |
| `~/Library/Preferences/nsmb.conf` | Per-user | No |

### Key Options

```
[default]
signing_required=no       # Disable SMB signing requirement
min_auth=ntlmv2           # Minimum auth level: ntlm | ntlmv2 | kerberos
port445=direct            # Direct TCP (skip NetBIOS)

[192.168.1.2]             # Server-specific overrides
protocol_vers_map=4       # 1=SMB1, 2=SMB2, 4=SMB3, 6=SMB2+3
signing_required=no
min_auth=ntlmv2
```

### Critical Setting: min_auth

- `min_auth=ntlm` — Allows NTLMv1. **DO NOT USE**: modern Windows 10/11
  disable NTLMv1 by default. This setting causes `EAUTH (error 80)` with
  Windows because Apple's stack tries NTLMv1 first and fails.
- `min_auth=ntlmv2` — Correct setting. Forces NTLMv2 which Windows accepts.
- `min_auth=kerberos` — Only useful in AD domain environments.

### protocol_vers_map

If mount fails with auth error despite correct credentials, try forcing
SMB protocol version:

- `protocol_vers_map=2` — SMB2 only (more compatible with older Windows)
- `protocol_vers_map=4` — SMB3 only (required for some Win11 configs)

### Apply Changes

```bash
killall NetAuthSysAgent   # Force reload of nsmb.conf
```

## Microsoft Account SMB Authentication

When Windows is signed in with a Microsoft account (e.g., `user@outlook.com`):

- **Try the local part first** (everything before `@`): `smbclient` and
  `mount_smbfs` often work with just `user` instead of `user@outlook.com`.
- The full email may work in `smbclient` but NOT in `mount_smbfs` due to
  URL parsing issues (two `@` signs in the URL).
- If nothing works, create a local Windows account specifically for SMB.

## Windows Side: SMB Signing

```powershell
# Check current setting
Get-SmbServerConfiguration | Select RequireSecuritySignature

# Disable (if macOS mount fails)
Set-SmbServerConfiguration -RequireSecuritySignature $false -Force
```

SMB signing is a common blocker: `smbclient` (Samba) supports it,
but Apple's `mount_smbfs` / Finder may fail the negotiation.

## Fallback: smbclient for File Operations

When native mount fails but smbclient works:

```bash
# List files recursively
smbclient '//<ip>/ShareName' -U 'user%password' -c 'recurse;ls'

# Download a file
smbclient '//<ip>/ShareName' -U 'user%password' -c 'cd subdir; get filename.pdf'

# Upload a file
smbclient '//<ip>/ShareName' -U 'user%password' -c 'cd subdir; put localfile.pdf'
```

## Chinese / Unicode Share Name Issue

`mount_smbfs` URL parser rejects Chinese characters in the share name
(e.g., `共享文件` → error 64: "URL parsing failed"). English share names
like `SharedFolder` parse correctly. Workarounds:

- Use `smbclient` instead (handles Unicode share names natively)
- Rename the Windows share to ASCII-only
- Use FUSE-based mount (see below) which bypasses `mount_smbfs` entirely

## FUSE Mount Alternatives

When Apple's native SMB stack is hopeless, mount via userspace FUSE:

### fuse-t (kext-less, recommended)

```bash
# Download and install
curl -LO https://github.com/macos-fuse-t/fuse-t/releases/download/1.2.6/fuse-t-macos-installer-1.2.6.pkg
sudo installer -pkg fuse-t-macos-installer-1.2.6.pkg -target /
```

### smb-pyfuse (Python, uses smbprotocol under the hood)

```bash
# Prerequisite: FUSE libraries (macFUSE with headers, or fuse-t + manual header setup)
# Install from GitHub (Pypi may have SSL issues from China — use mirror)
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple smb-pyfuse

# Known issue: fuse-python dependency needs fuse.h headers.
# fuse-t .pkg only ships .dylib/.a, not headers.
# Workaround: install macFUSE from https://osxfuse.github.io (includes headers)
# then `pip3 install fuse-python` will compile.
```

### smb2fuse (Go, macOS-native)

https://github.com/GabrielePintus/smb2fuse — pure Go SMB2 mount, no FUSE
dependency issues. Requires Go toolchain to build from source.

## Error Codes Reference

| Code | Meaning | Likely Cause |
|------|---------|-------------|
| 64 | EINVAL (URL parse) | Chinese chars in share name, double `@` in username, `mount_smbfs` URL parsing bug |
| 77 | EAUTH | Credentials rejected OR SMB protocol/auth mismatch |
| 80 | EAUTH (in logs) | Apple's SMB stack auth failure — check nsmb.conf `min_auth` |
| NT_STATUS_LOGON_FAILURE | Bad credentials | Wrong user/password format or local account doesn't exist |
