# Quick Start Guide

Get started with VirusTotal Scanner for macOS in 5 minutes.

## 1. Installation

```bash
# Clone or download the repository
cd macos-virus-check

# Run the installer
./install.sh
```

Follow the prompts to:
- Install Python dependencies
- Set up the `vt-check` command
- Configure your API key
- Optionally install Finder integration

**Important**: If you install the Finder Quick Action, restart Finder:
```bash
killall Finder
```

## 2. Get Your API Key

1. Visit [VirusTotal API Key page](https://www.virustotal.com/gui/my-apikey)
2. Sign in or create a free account
3. Copy your API key

## 3. Configure API Key

```bash
vt-check config --api-key YOUR_API_KEY_HERE
```

Or use environment variable:
```bash
export VT_API_KEY="your-api-key-here"
```

## 4. Scan Your First File

```bash
# Scan a single file
vt-check scan /path/to/file.dmg

# Scan with notification
vt-check scan --notify suspicious.pdf

# Scan multiple files
vt-check scan *.exe
```

## 5. Use Finder Integration (Optional)

If you installed the Quick Action:

1. Find any file in Finder
2. Right-click the file
3. Select **Quick Actions** → **VirusTotal Scan**
4. Wait for the notification with results

## Common Commands

```bash
# Scan a directory recursively
vt-check scan -r ~/Downloads

# Check a hash without uploading
vt-check hash a3f2b1c4d5e6...

# View configuration
vt-check config --show

# Clear cache
vt-check config --clear-cache

# Get help
vt-check --help
```

## Understanding Results

### Clean (Green ✅)
- 0 detections from all antivirus engines
- File appears safe

### Suspicious (Yellow ⚠️)
- 1+ engines marked as suspicious
- May be a false positive
- Review the detailed report

### Malicious (Red 🚨)
- 1+ engines detected malware
- Do not open or execute the file
- Delete or quarantine immediately

## Rate Limits (Free API)

- **4 requests per minute**
- **500 requests per day**
- Files up to **32 MB**

Wait between scans or upgrade to premium for higher limits.

## Troubleshooting

### Command not found
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.zshrc for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### API Key Error
```bash
# Re-configure
vt-check config --api-key YOUR_KEY

# Or use environment variable
export VT_API_KEY="your-key"
```

### Quick Action Not Showing
1. Log out and log back in
2. Or restart Finder: `killall Finder`
3. Check `~/Library/Services/` for the workflow

## Next Steps

- Read the full [README](README.md) for advanced features
- Check [CHANGELOG](CHANGELOG.md) for updates
- Report issues on GitHub

---

Happy scanning! 🔍
