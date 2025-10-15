# VirusTotal Scanner for macOS

A comprehensive, user-friendly VirusTotal integration for macOS featuring both CLI and Finder context menu scanning capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)

## Features

### 🚀 Dual Interface
- **CLI Tool**: Powerful command-line interface with rich formatting
- **Finder Integration**: Right-click context menu for quick scans

### 🔍 Smart Scanning
- **Hash-based checks**: Verify files without uploading when possible
- **Intelligent caching**: Store recent results to avoid redundant scans
- **Batch scanning**: Process multiple files or entire directories
- **Recursive scanning**: Scan all files in a directory tree

### 🎨 Rich Output
- **Color-coded results**: Green (clean), yellow (suspicious), red (malicious)
- **Detailed reports**: File info, detection stats, and direct links to VT
- **macOS notifications**: Get notified when scans complete
- **Progress indicators**: Visual feedback for long-running operations

### 🔒 Secure Configuration
- **Safe API key storage**: Stored with restricted permissions (600)
- **Environment variable support**: Use `VT_API_KEY` for CI/CD
- **No hardcoded secrets**: API keys never stored in code

## Installation

### Prerequisites
- macOS 10.15 or later
- Python 3.8 or higher
- VirusTotal API key ([get one free](https://www.virustotal.com/gui/my-apikey))

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/macos-virus-check.git
cd macos-virus-check

# Run the installation script
./install.sh
```

The installer will:
1. Check Python and pip installation
2. Optionally create a virtual environment
3. Install required dependencies
4. Create the `vt-check` command
5. Configure your API key
6. Optionally install the Finder Quick Action (using the fixed v2 script)

**After installation with Quick Action**: Restart Finder by running `killall Finder`

### Manual Installation

If you prefer manual installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
export VT_API_KEY="your-api-key-here"

# Or save it to config
python3 src/cli.py config --api-key YOUR_KEY

# Run from source
python3 src/cli.py scan file.dmg
```

## Usage

### Command Line Interface

#### Basic Scanning

```bash
# Scan a single file
vt-check scan suspicious.dmg

# Scan multiple files
vt-check scan file1.exe file2.pdf file3.zip

# Scan all files in current directory
vt-check scan *

# Recursively scan a directory
vt-check scan -r ~/Downloads
```

#### Advanced Options

```bash
# Force upload even if file exists in VT database
vt-check scan --force-upload malware.exe

# Send macOS notification when complete
vt-check scan --notify suspicious.pdf

# Open detailed report in browser
vt-check scan --open-report file.dmg

# Disable cache for fresh results
vt-check scan --no-cache file.exe

# Output results as JSON
vt-check scan --json file.pdf
```

#### Hash Checking

Check a file hash without uploading:

```bash
vt-check hash a3f2b1c4d5e6f7890abcdef1234567890abcdef1234567890abcdef12345678
```

#### Configuration

```bash
# Set API key
vt-check config --api-key YOUR_KEY

# Show current configuration
vt-check config --show

# Clear cached results
vt-check config --clear-cache
```

### Finder Quick Action

After installation with Quick Action enabled:

1. **Right-click** any file in Finder
2. Select **Quick Actions** → **VirusTotal Scan**
3. A notification will appear with the scan progress
4. Click the result notification to view the full report online

### Example Output

```
📁 Scanning: suspicious.dmg
🔍 SHA256: a3f2b1c4d5e6...
⏳ Checking VirusTotal...

╭─────────── ✅ Scan Result ────────────╮
│ File        suspicious.dmg            │
│ Size        15.3 MB                   │
│ Type        Apple Disk Image          │
│ SHA-256     a3f2b1c4d5e6f7...         │
│ Result      ✅ CLEAN                  │
│ Detections  0/70 detections           │
│ Last        2025-10-14 15:30:22       │
│ Report      https://virustotal.com... │
│ Status      Retrieved from VT database│
╰───────────────────────────────────────╯
```

## Project Structure

```
macos-virus-check/
├── src/
│   ├── vt_scanner.py      # Core VirusTotal API client
│   ├── cli.py             # CLI interface with Click
│   ├── config.py          # Configuration management
│   └── utils.py           # Utility functions
├── automator/
│   ├── vt_quick_action.py # Quick Action script
│   └── create_quick_action.sh
├── install.sh             # Installation script
├── requirements.txt       # Python dependencies
└── README.md
```

## Configuration

### API Key Priority

The scanner looks for your API key in this order:

1. **Environment variable**: `VT_API_KEY`
2. **Config file**: `~/.config/vt-scanner/config.json`

### Configuration File Location

- **Config**: `~/.config/vt-scanner/config.json`
- **Cache**: `~/.config/vt-scanner/cache/`

### Cache Management

Scan results are cached for 7 days by default. To manage cache:

```bash
# Clear all cached results
vt-check config --clear-cache

# Disable cache for a specific scan
vt-check scan --no-cache file.dmg
```

## Security Considerations

### Privacy
- **Hash-first approach**: Files are checked by hash before uploading
- **No automatic uploads**: You control what gets uploaded
- **Local cache**: Results cached locally for faster repeated scans

### API Key Security
- Stored with 600 permissions (owner read/write only)
- Never logged or exposed in error messages
- Can be stored as environment variable for additional security

### What Gets Uploaded?
- When you scan a file, the scanner first calculates its SHA-256 hash
- If the hash exists in VT database, no upload occurs
- Files are only uploaded if they're new to VirusTotal
- Use `vt-check hash <sha256>` to check without any upload risk

## Limitations

### Free API Tier
The free VirusTotal API has these limits:
- **4 requests per minute**
- **500 requests per day**
- **32 MB max file size**

For larger files or higher volume, consider a [premium API key](https://www.virustotal.com/gui/my-apikey).

### Detection Accuracy
- VirusTotal aggregates results from 70+ antivirus engines
- False positives can occur
- 0 detections doesn't guarantee absolute safety
- Use as one tool in a comprehensive security strategy

## Troubleshooting

### "API key not configured"

```bash
# Set your API key
vt-check config --api-key YOUR_KEY

# Or use environment variable
export VT_API_KEY="your-key-here"
```

### "Command not found: vt-check"

```bash
# Add to PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# Then reload your shell
source ~/.zshrc
```

### Quick Action not appearing

1. Log out and log back in (or restart Finder)
2. Check `~/Library/Services/` for the workflow
3. Re-run: `./automator/create_quick_action.sh`

### Rate limit errors

The free API allows 4 requests/minute:
- Wait a minute between scans
- Consider upgrading to premium API
- Use `--no-cache` sparingly

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [VirusTotal](https://www.virustotal.com/) for providing the API
- [Click](https://click.palletsprojects.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/macos-virus-check/issues)
- **API Docs**: [VirusTotal API v3](https://developers.virustotal.com/reference/overview)

## Disclaimer

This tool is provided as-is for educational and security research purposes. Always follow responsible disclosure practices and respect VirusTotal's terms of service. The authors are not responsible for misuse of this tool.

---

**Made with ❤️ for macOS security**
