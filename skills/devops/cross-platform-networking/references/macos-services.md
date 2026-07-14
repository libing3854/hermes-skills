# macOS Service Management Reference

## Launchctl Commands

```bash
# Start a service (force restart)
sudo launchctl kickstart -k system/com.apple.smbd
sudo launchctl kickstart -k system/com.apple.screensharing

# Alternative: bootstrap (first-time load)
sudo launchctl bootstrap system /System/Library/LaunchDaemons/com.apple.smbd.plist
sudo launchctl bootstrap system /System/Library/LaunchDaemons/com.apple.screensharing.plist

# Check service details
launchctl print system/com.apple.smbd
launchctl print system/com.apple.screensharing

# List all loaded services
launchctl list | grep -E "smbd|screensharing"
```

## Service Socket Configuration

macOS uses launchd socket activation. The sockets are defined in the plist:

- **smbd**: SockServiceName = `microsoft-ds` (port 445), Bonjour = `smb`
- **screensharingd**: SockServiceName = `vnc-server` (port 5900), Bonjour = `rfb`

This means launchd opens the ports and passes file descriptors to the
service process. The service doesn't bind ports itself.

## Share Points

```bash
# List all share points
sharing -l

# Add share point (requires sudo)
sudo sharing -a /path/to/folder -S "DisplayName" -n "ShareName"

# Output shows: name, path, smb config (shared, guest access, read-only, sealed)
```

## Firewall App List

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
# Shows apps with Allow/Block incoming connections rules
# smbd should appear with "Allow incoming connections"
```

## Verification Commands

```bash
# Ports listening (most reliable on macOS)
netstat -an | grep -E "445|5900|139"

# Process check
ps aux | grep -E "smbd|screensharing" | grep -v grep

# Service active count
launchctl print system/com.apple.smbd | head -5
# Should show: active count = 1
```

## Known Gotchas

1. `lsof -c smbd -i` may NOT list smbd's ports (launchd holds the FDs)
2. `sharing -a` fails without sudo
3. `launchctl load -w` may silently fail on macOS Sequoia+; use `kickstart`
4. Screen sharing VNC password may need explicit configuration via ARDAgent
