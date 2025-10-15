# Troubleshooting Guide

Common issues and solutions for VirusTotal Scanner for macOS.

## Quick Action Issues

### "The document 'VirusTotal Scan.workflow' could not be opened"

**Problem**: The Quick Action workflow file is corrupted or incomplete.

**Solution**:
1. Remove the broken workflow:
   ```bash
   rm -rf ~/Library/Services/VirusTotal\ Scan.workflow
   ```

2. Reinstall using the fixed script:
   ```bash
   cd macos-virus-check
   ./automator/create_quick_action_v2.sh
   ```

3. Restart Finder:
   ```bash
   killall Finder
   ```

4. Test with a simple file on your Desktop

### Quick Action Not Appearing in Context Menu

**Possible causes and solutions**:

1. **Finder needs restart**
   ```bash
   killall Finder
   ```

2. **Log out and log back in**
   - Sometimes macOS needs a full logout to register new services

3. **Check if workflow exists**
   ```bash
   ls ~/Library/Services/
   ```
   You should see `VirusTotal Scan.workflow`

4. **Check System Preferences**
   - Go to: **System Settings** → **Privacy & Security** → **Extensions** → **Finder**
   - Make sure "VirusTotal Scan" is enabled

### Quick Action Shows But Doesn't Work

**Possible causes**:

1. **vt-check not installed**
   - Make sure you ran `./install.sh` first
   - Test: `vt-check --help`

2. **API key not configured**
   ```bash
   vt-check config --show
   ```
   If not configured:
   ```bash
   vt-check config --api-key YOUR_KEY
   ```

3. **Check wrapper script**
   ```bash
   cat ~/.local/bin/vt-scan-file
   ```
   Should exist and be executable

4. **Test wrapper manually**
   ```bash
   ~/.local/bin/vt-scan-file ~/Desktop/test-file.txt
   ```

5. **Check logs**
   ```bash
   log show --predicate 'subsystem == "com.apple.automator"' --last 5m
   # Or
   tail -f /var/log/system.log | grep virustotal
   ```

## CLI Issues

### "Command not found: vt-check"

**Solution**:
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent (zsh)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Make permanent (bash)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "API key not configured"

**Solution**:
```bash
# Method 1: Config file
vt-check config --api-key YOUR_KEY

# Method 2: Environment variable
export VT_API_KEY="your-key-here"
echo 'export VT_API_KEY="your-key"' >> ~/.zshrc
```

### "ModuleNotFoundError" or Import Errors

**Solution**:
```bash
# Reinstall dependencies
cd macos-virus-check
pip install -r requirements.txt

# Or with virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Rate Limit Errors

**Problem**: "Too many requests" or API quota exceeded

**Solution**:
- Free API: 4 requests/minute, 500/day
- Wait 60 seconds between scans
- Use cache (enabled by default)
- Consider upgrading to premium API

## Notification Issues

### Notifications Not Showing

**Possible causes**:

1. **Notifications disabled for Terminal/Automator**
   - Go to: **System Settings** → **Notifications**
   - Enable notifications for "Terminal" and "Script Editor"

2. **pync not installed**
   ```bash
   pip install pync
   ```

3. **Fallback to osascript**
   - Should work automatically if pync fails

### Notifications Show But Can't Click

**Note**: This is normal behavior for some notification types. The permalink is still available in the CLI output.

## Permission Issues

### "Permission denied" Errors

**Solution**:
```bash
# Fix permissions on config directory
chmod 700 ~/.config/vt-scanner
chmod 600 ~/.config/vt-scanner/config.json

# Fix script permissions
chmod +x ~/.local/bin/vt-check
chmod +x ~/.local/bin/vt-scan-file
```

### Automator Asks for Permissions

**This is normal!** First time running:
1. macOS will ask if Automator can access files
2. Click "Allow" or "OK"
3. May need to run twice (once to grant permission, once to scan)

## Cache Issues

### Old Results Being Shown

**Solution**:
```bash
# Clear cache
vt-check config --clear-cache

# Or scan without cache
vt-check scan --no-cache file.pdf
```

### Cache Directory Not Found

**Solution**:
```bash
# Recreate cache directory
mkdir -p ~/.config/vt-scanner/cache
chmod 700 ~/.config/vt-scanner
```

## Network Issues

### "Connection timeout" or "Network error"

**Possible causes**:

1. **No internet connection**
   - Check your network

2. **Firewall blocking**
   - Allow Python/Terminal through firewall
   - Check if HTTPS (443) is blocked

3. **VPN issues**
   - Try disconnecting VPN temporarily

4. **Proxy settings**
   - Configure proxy in requests library if needed

## Installation Issues

### Installation Script Fails

**Solution**:
```bash
# Manual installation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create symlink manually
ln -s "$(pwd)/install.sh" ~/.local/bin/vt-check
```

### Python Version Too Old

**Requirement**: Python 3.8+

**Solution**:
```bash
# Check version
python3 --version

# Install latest Python from python.org
# Or use Homebrew
brew install python@3.11
```

## macOS Version Issues

### Quick Action Not Supported

**Requirement**: macOS 10.15 (Catalina) or later

**Alternative**: Use CLI only
```bash
vt-check scan file.pdf
```

## Debugging

### Enable Verbose Logging

```bash
# Set environment variable
export VT_DEBUG=1

# Then run command
vt-check scan file.pdf
```

### Check System Logs

```bash
# Automator logs
log show --predicate 'process == "Automator"' --last 10m

# Python errors
log show --predicate 'process == "Python"' --last 10m

# Custom tag
log show --predicate 'subsystem == "virustotal-scan"' --last 10m
```

### Test Components Individually

```bash
# Test API client
python3 -c "from src.vt_scanner import VirusTotalScanner; print('OK')"

# Test config
python3 -c "from src.config import Config; c=Config(); print(c.get_api_key())"

# Test CLI
python3 src/cli.py --help
```

## Getting Help

If you're still having issues:

1. **Check existing issues**: [GitHub Issues](https://github.com/ybraz/macOS-virus-check/issues)
2. **Create new issue** with:
   - macOS version: `sw_vers`
   - Python version: `python3 --version`
   - Error message (full output)
   - Steps to reproduce

## Quick Fix Checklist

Run these commands to fix common issues:

```bash
# 1. Reinstall Quick Action
rm -rf ~/Library/Services/VirusTotal\ Scan.workflow
cd macos-virus-check
./automator/create_quick_action_v2.sh
killall Finder

# 2. Fix permissions
chmod +x ~/.local/bin/vt-check
chmod +x ~/.local/bin/vt-scan-file
chmod 700 ~/.config/vt-scanner
chmod 600 ~/.config/vt-scanner/config.json 2>/dev/null || true

# 3. Update PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 4. Reinstall dependencies
cd macos-virus-check
pip install -r requirements.txt

# 5. Test installation
./test_installation.sh
```

## Known Issues

### Issue: Quick Action slow on first run
**Cause**: macOS caching
**Workaround**: Normal after first use

### Issue: Notifications don't show file icon
**Cause**: pync limitation
**Workaround**: Not fixable, doesn't affect functionality

### Issue: Can't scan files over 32MB (free API)
**Cause**: VirusTotal API limit
**Solution**: Upgrade to premium API

---

Still having problems? Open an issue on [GitHub](https://github.com/ybraz/macOS-virus-check/issues) with detailed information.
