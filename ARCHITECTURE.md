# Architecture Guide

This document describes the architecture and design decisions of the VirusTotal Scanner for macOS.

## Overview

The scanner is designed with modularity, security, and user experience in mind. It provides two main interfaces (CLI and Finder integration) backed by a common core.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User Interfaces                    │
├──────────────────────┬──────────────────────────────┤
│   CLI (cli.py)       │  Quick Action (Automator)    │
│   - Click framework  │  - vt_quick_action.py        │
│   - Rich formatting  │  - macOS notifications       │
└──────────────────────┴──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Core Components                        │
├─────────────────────────────────────────────────────┤
│  vt_scanner.py    │  config.py    │  utils.py      │
│  - API client     │  - Config mgmt│  - Helpers     │
│  - Hash checking  │  - Cache mgmt │  - Formatting  │
│  - File scanning  │  - API key    │  - Notify      │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              External Services                      │
├─────────────────────────────────────────────────────┤
│         VirusTotal API v3                           │
│         - File analysis                             │
│         - Hash lookup                               │
│         - Report generation                         │
└─────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. vt_scanner.py - VirusTotal API Client

**Purpose**: Core integration with VirusTotal API v3

**Key Classes**:
- `VirusTotalScanner`: Main API client class

**Key Methods**:
```python
calculate_file_hash(file_path)  # Calculate SHA-256
check_hash(file_hash)            # Check if hash exists in VT
upload_file(file_path)           # Upload file for analysis
get_analysis(analysis_id)        # Get analysis results
scan_file(file_path)             # Complete scan workflow
parse_results(analysis_data)     # Parse and summarize results
```

**Design Decisions**:
- Hash-first approach: Always check hash before uploading
- Automatic polling: Waits for analysis to complete
- Error handling: Comprehensive exception handling for API errors
- Large file support: Uses upload URL for files >32MB

### 2. config.py - Configuration Management

**Purpose**: Manage API keys, settings, and caching

**Key Classes**:
- `Config`: Configuration and cache manager

**Key Methods**:
```python
get_api_key()                   # Get API key from env or file
set_api_key(api_key)           # Save API key securely
get_cached_result(file_hash)   # Retrieve cached scan
cache_result(file_hash, result) # Store scan result
clear_cache()                   # Clear all cached results
```

**Design Decisions**:
- Priority: Environment variable > Config file
- Security: Config file with 600 permissions (owner only)
- Cache TTL: 7 days default (configurable)
- Storage location: `~/.config/vt-scanner/`

### 3. utils.py - Utility Functions

**Purpose**: Helper functions for common tasks

**Key Functions**:
```python
format_file_size(bytes)         # Human-readable file sizes
format_timestamp(unix_time)     # Human-readable dates
send_notification(title, msg)   # macOS notifications
validate_file_path(path)        # Path validation
get_threat_emoji(level)         # Threat level icons
expand_paths(paths, recursive)  # Expand globs and dirs
```

**Design Decisions**:
- Pure functions: No side effects where possible
- Graceful degradation: Fall back if services unavailable
- macOS integration: Native notification support

### 4. cli.py - Command Line Interface

**Purpose**: Rich, interactive CLI for end users

**Key Commands**:
```python
scan [FILES]                    # Scan one or more files
hash HASH_VALUE                 # Check hash without upload
config [OPTIONS]                # Manage configuration
```

**Design Decisions**:
- Click framework: Modern, declarative CLI
- Rich library: Beautiful terminal output
- Progress indicators: Real-time feedback
- Multiple output formats: Human-readable and JSON

### 5. Quick Action Integration

**Purpose**: Finder context menu integration

**Components**:
- `vt_quick_action.py`: Python script called by Automator
- `create_quick_action.sh`: Installer for workflow
- Automator workflow: macOS service definition

**Workflow**:
1. User right-clicks file in Finder
2. Selects "Quick Actions" → "VirusTotal Scan"
3. Automator runs shell script
4. Shell script calls `vt_quick_action.py` with file path
5. Script scans file and shows notification
6. User clicks notification to view full report

## Data Flow

### Scan Workflow

```
User Request
    │
    ▼
1. Calculate file hash (SHA-256)
    │
    ▼
2. Check local cache
    ├─ Found ──→ Return cached result
    │
    └─ Not found
         │
         ▼
3. Check VirusTotal by hash
    ├─ Found ──→ Parse and cache result
    │
    └─ Not found
         │
         ▼
4. Upload file to VirusTotal
    │
    ▼
5. Poll for analysis completion
    │
    ▼
6. Parse results and cache
    │
    ▼
7. Display to user
```

### Configuration Priority

```
1. Environment Variable (VT_API_KEY)
    ├─ Found ──→ Use this
    │
    └─ Not found
         │
         ▼
2. Config File (~/.config/vt-scanner/config.json)
    ├─ Found ──→ Use this
    │
    └─ Not found ──→ Error: Not configured
```

## Security Model

### API Key Storage

1. **Environment Variable** (highest priority)
   - Temporary, session-specific
   - Good for CI/CD pipelines
   - Not persistent

2. **Config File** (fallback)
   - Stored at `~/.config/vt-scanner/config.json`
   - File permissions: 600 (owner read/write only)
   - Not accessible by other users

### Privacy Protection

1. **Hash-First Approach**
   - Always check hash before uploading
   - Avoids uploading files already in VT database
   - Reduces unnecessary data transfer

2. **Local Caching**
   - Stores results locally for 7 days
   - Reduces API calls
   - Improves response time

3. **No Telemetry**
   - No usage tracking
   - No data sent to third parties
   - Only communicates with VirusTotal API

## Error Handling

### Levels of Error Handling

1. **API Errors**
   ```python
   try:
       response = requests.get(url)
       response.raise_for_status()
   except requests.exceptions.RequestException as e:
       # Handle API errors gracefully
   ```

2. **File Errors**
   ```python
   if not file_path.exists():
       raise FileNotFoundError(f"File not found: {file_path}")
   ```

3. **Configuration Errors**
   ```python
   if not api_key:
       # Provide helpful error message with solutions
   ```

### Error Messages

- **User-friendly**: Clear, actionable messages
- **Contextual**: Include relevant information
- **Helpful**: Suggest solutions

Example:
```
❌ VirusTotal API key not configured!

To configure, run one of the following:
  1. vt-check config --api-key YOUR_KEY
  2. export VT_API_KEY=YOUR_KEY

Get your API key at: https://www.virustotal.com/gui/my-apikey
```

## Performance Optimizations

### 1. Caching Strategy

- **Cache location**: `~/.config/vt-scanner/cache/`
- **Cache key**: SHA-256 hash of file
- **Cache TTL**: 7 days (configurable)
- **Benefits**:
  - Reduces API calls
  - Faster responses for known files
  - Respects rate limits

### 2. Batch Processing

- **Parallel potential**: Could scan multiple files concurrently
- **Rate limiting**: Respect VT API limits (4 req/min free tier)
- **Progress feedback**: Real-time updates during batch scans

### 3. Hash-First Approach

- **Speed**: Hash check is faster than upload
- **Bandwidth**: Avoids uploading known files
- **API quota**: Saves API requests

## Extension Points

### Adding New Commands

```python
# In cli.py
@cli.command()
@click.argument("arg")
def new_command(arg):
    """Command description"""
    # Implementation
    pass
```

### Custom Notification Handlers

```python
# In utils.py
def send_custom_notification(title, message):
    # Custom implementation
    pass
```

### Additional File Formats

```python
# In vt_scanner.py
def scan_special_format(file_path):
    # Special handling for specific formats
    pass
```

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies (API calls)
- Verify error handling

### Integration Tests
- Test complete workflows
- Use test API key
- Verify end-to-end functionality

### Manual Testing
- Test on real macOS systems
- Verify Finder integration
- Test with various file types

## Future Enhancements

### Planned Features

1. **Menu Bar Application**
   - Always-accessible from menu bar
   - Drag-and-drop interface
   - Quick access to recent scans

2. **Folder Monitoring**
   - Watch specific directories
   - Automatic scanning of new files
   - Scheduled scans

3. **Advanced Reporting**
   - Export reports (PDF, CSV)
   - Scan history
   - Statistics and trends

4. **Enhanced Caching**
   - SQLite database for cache
   - Better query capabilities
   - Scan history search

## Dependencies

### Core Dependencies

```
requests       # HTTP client for API calls
click          # CLI framework
rich           # Terminal formatting
pync           # macOS notifications
python-magic   # File type detection (optional)
```

### Why These Choices?

- **requests**: Industry standard, reliable HTTP client
- **click**: Modern, declarative CLI with excellent documentation
- **rich**: Beautiful terminal output with minimal effort
- **pync**: Native macOS notification support

## Compatibility

### macOS Versions
- Tested on: macOS 10.15+
- Should work on: macOS 10.14+

### Python Versions
- Required: Python 3.8+
- Recommended: Python 3.10+

### VirusTotal API
- API Version: v3
- Tier: Free tier compatible
- Premium features: Large file upload URL

---

For questions about architecture, please open an issue or see [CONTRIBUTING.md](CONTRIBUTING.md).
