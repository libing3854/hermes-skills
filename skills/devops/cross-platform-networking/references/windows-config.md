# Windows Network Configuration Reference

## Network Profile Check/Set

```powershell
# Check current profile
Get-NetConnectionProfile
# NetworkCategory should be "Private" for file sharing/RDP

# Set to Private
Set-NetConnectionProfile -InterfaceAlias "Ethernet" -NetworkCategory Private
```

## Firewall Rules

```powershell
# Check firewall rules by group
Get-NetFirewallRule -DisplayGroup "文件和打印机共享" | Select-Object DisplayName, Enabled
Get-NetFirewallRule -DisplayGroup "网络发现" | Select-Object DisplayName, Enabled
Get-NetFirewallRule -DisplayGroup "远程桌面" | Select-Object DisplayName, Enabled

# Enable all rules in a group (requires admin)
Enable-NetFirewallRule -DisplayGroup "文件和打印机共享"
Enable-NetFirewallRule -DisplayGroup "网络发现"
Enable-NetFirewallRule -DisplayGroup "远程桌面"

# Enable ICMP (ping)
Enable-NetFirewallRule -DisplayName "*ICMPv4-In"
```

## SMB Share

```powershell
# Create share
New-SmbShare -Name 'SharedFolder' -Path 'C:\SharedFolder' -FullAccess 'Everyone'

# List shares
Get-SmbShare | Select-Object Name, Path, Description
```

## RDP Enable

```powershell
# Check RDP status (1 = disabled, 0 = enabled)
Get-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections"

# Enable RDP
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0
```

## Network Services

```powershell
# Check network discovery services
Get-Service -Name "FDResPub" -ErrorAction SilentlyContinue
Get-Service -Name "upnphost" -ErrorAction SilentlyContinue
Get-Service -Name "SSDPSRV" -ErrorAction SilentlyContinue

# Start UPnP if needed
Start-Service upnphost
```

## Admin Elevation Patterns

```powershell
# Method 1: Start-Process (may fail silently for firewall rules)
Start-Process powershell -Verb RunAs -ArgumentList "-Command", "Enable-NetFirewallRule -DisplayGroup '...'"

# Method 2: Run PowerShell as Administrator directly (more reliable)
# Right-click PowerShell → Run as Administrator → then run commands

# Verify elevation
whoami /priv
```

## Known Gotchas

1. **Firewall rules via Start-Process may not apply** - the spawned process
   can fail silently. Verify by checking rule Enabled status after, or
   confirm via Settings UI.
2. **Windows 11 Home cannot be RDP host** - only Pro/Enterprise/Education.
3. **Dual permission system** - SMB shares have both "Share permissions"
   AND "NTFS Security permissions". Both must allow the desired access.
4. **Network must be Private** - Public network blocks most sharing/RDP.
