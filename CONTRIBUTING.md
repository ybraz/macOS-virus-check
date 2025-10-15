# Contributing to VirusTotal Scanner for macOS

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title** - Describe the issue concisely
2. **Steps to reproduce** - Detailed steps to recreate the bug
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - macOS version, Python version, etc.
6. **Logs/Screenshots** - If applicable

### Suggesting Features

Feature requests are welcome! Please include:

1. **Use case** - Why this feature would be useful
2. **Proposed solution** - How it might work
3. **Alternatives** - Other approaches you've considered
4. **Examples** - Similar features in other tools

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/macos-virus-check.git
   cd macos-virus-check
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding style (PEP 8 for Python)
   - Add tests if applicable
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Run the installation test
   ./test_installation.sh

   # Test your specific changes
   python3 src/cli.py scan test-file.txt
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Include screenshots/examples if applicable

## Development Setup

### Prerequisites

- macOS 10.15 or later
- Python 3.8+
- pip
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/macos-virus-check.git
cd macos-virus-check

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional)
pip install pytest black flake8 mypy

# Run from source
python3 src/cli.py --help
```

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

Example:
```python
def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file

    Args:
        file_path: Path to the file

    Returns:
        SHA256 hash as hexadecimal string

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    # Implementation here
    pass
```

### Code Formatting

```bash
# Format code with black
black src/

# Check style with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

### Testing

- Add tests for new features
- Ensure existing tests pass
- Test on actual macOS systems
- Verify both CLI and Quick Action work

### Documentation

- Update README.md for new features
- Add examples to QUICKSTART.md
- Update CHANGELOG.md
- Include docstrings in code

## Project Structure

```
macos-virus-check/
├── src/                    # Source code
│   ├── vt_scanner.py      # VirusTotal API client
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration management
│   └── utils.py           # Utility functions
├── automator/             # Finder integration
│   ├── vt_quick_action.py
│   └── create_quick_action.sh
├── examples/              # Usage examples
├── install.sh            # Installation script
├── test_installation.sh  # Testing script
└── README.md            # Documentation
```

## Areas for Contribution

### High Priority
- [ ] Unit tests and test coverage
- [ ] Error handling improvements
- [ ] Performance optimizations
- [ ] Support for more file types
- [ ] Better error messages

### Medium Priority
- [ ] Menu bar application
- [ ] Folder monitoring/watching
- [ ] Scan history viewer
- [ ] Custom notification sounds
- [ ] Export reports (PDF/CSV)

### Low Priority
- [ ] Multi-language support
- [ ] Custom themes
- [ ] Integration with other security tools
- [ ] Scheduled scans
- [ ] Advanced filtering

## Security Considerations

When contributing, please:

- **Never commit API keys** or secrets
- **Respect user privacy** - minimize data collection
- **Handle errors securely** - don't leak sensitive info
- **Follow security best practices**
- **Test with malicious files carefully** - use VMs or sandboxes

## API Key for Testing

For testing:
1. Get a free API key from [VirusTotal](https://www.virustotal.com/gui/my-apikey)
2. Use environment variable: `export VT_API_KEY="your-key"`
3. Never commit the key to Git

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Read the full [README](README.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
