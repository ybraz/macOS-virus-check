# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-15

### Added
- Initial release of VirusTotal Scanner for macOS
- CLI interface with rich formatting and progress indicators
- Finder Quick Action integration for context menu scanning
- Smart hash-based file checking to avoid unnecessary uploads
- Local caching system for scan results (7-day default)
- Batch scanning support for multiple files
- Recursive directory scanning
- macOS native notifications for scan results
- Secure API key storage with proper file permissions
- Environment variable support for API key (`VT_API_KEY`)
- Detailed scan reports with clickable links to VirusTotal
- Color-coded threat levels (green/yellow/red)
- JSON output option for programmatic use
- Configuration management commands
- Automated installation script
- Comprehensive documentation and examples

### Features
- `vt-check scan` - Scan files for malware
- `vt-check hash` - Check file hash without uploading
- `vt-check config` - Manage configuration and API key
- Support for glob patterns and wildcards
- Cache management and clearing
- Browser integration for detailed reports

### Security
- Hash-first approach minimizes unnecessary uploads
- API key stored with 600 permissions (owner only)
- No hardcoded secrets or credentials
- Privacy-focused design

## [Unreleased]

### Planned
- Menu bar application for quick access
- Scheduled directory monitoring
- Custom notification sounds
- Export scan reports (PDF, CSV)
- Batch processing queue
- Integration with macOS Security framework
- Watch folders for automatic scanning
- Advanced filtering and search in scan history
- Multi-language support
- Dark mode UI enhancements

---

For more details, see the [README](README.md).
