#!/bin/bash
###############################################################################
# VirusTotal Scanner for macOS - Installation Script
#
# This script installs the VirusTotal scanner with both CLI and Finder
# integration capabilities.
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation paths
INSTALL_DIR="$HOME/.local/bin"
SYMLINK_NAME="vt-check"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  VirusTotal Scanner for macOS - Installation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}→${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 is not installed!"
    echo "  Please install Python 3 from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Check pip
echo -e "${YELLOW}→${NC} Checking pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}✗${NC} pip is not installed!"
    echo "  Installing pip..."
    python3 -m ensurepip --upgrade
fi
echo -e "${GREEN}✓${NC} pip is available"

# Create virtual environment (optional but recommended)
read -p "$(echo -e ${YELLOW}?${NC} Create virtual environment? [recommended] \(y/n\): )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    VENV_DIR="$SCRIPT_DIR/venv"

    if [ -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}→${NC} Virtual environment already exists, using it..."
    else
        echo -e "${YELLOW}→${NC} Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✓${NC} Virtual environment created"
    fi

    source "$VENV_DIR/bin/activate"
    PYTHON_BIN="$VENV_DIR/bin/python3"
    PIP_BIN="$VENV_DIR/bin/pip"
else
    PYTHON_BIN="python3"
    PIP_BIN="python3 -m pip"
fi

# Install Python dependencies
echo -e "${YELLOW}→${NC} Installing Python dependencies..."
$PIP_BIN install -q --upgrade pip
$PIP_BIN install -q -r "$SCRIPT_DIR/requirements.txt"
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create install directory
echo -e "${YELLOW}→${NC} Setting up CLI command..."
mkdir -p "$INSTALL_DIR"

# Create wrapper script
WRAPPER_SCRIPT="$INSTALL_DIR/$SYMLINK_NAME"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# VirusTotal Scanner CLI wrapper

SCRIPT_DIR="$SCRIPT_DIR"

# Use virtual environment if it exists
if [ -d "\$SCRIPT_DIR/venv" ]; then
    source "\$SCRIPT_DIR/venv/bin/activate"
fi

# Add src directory to Python path
export PYTHONPATH="\$SCRIPT_DIR/src:\$PYTHONPATH"

# Run the CLI
python3 "\$SCRIPT_DIR/src/cli.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✓${NC} CLI command created: $SYMLINK_NAME"

# Check if install directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo -e "${YELLOW}⚠${NC}  Warning: $INSTALL_DIR is not in your PATH"
    echo ""
    echo "  Add this to your shell configuration file (~/.zshrc or ~/.bashrc):"
    echo -e "  ${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "  Then run: source ~/.zshrc (or ~/.bashrc)"
    echo ""
fi

# Configure API key
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  API Key Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check if API key is already configured
EXISTING_KEY=$("$WRAPPER_SCRIPT" config --show 2>/dev/null | grep "API Key" | grep -v "Not configured" || echo "")

if [ -n "$EXISTING_KEY" ]; then
    echo -e "${GREEN}✓${NC} API key already configured"
    echo ""
else
    echo "You need a VirusTotal API key to use this tool."
    echo "Get your free API key at: https://www.virustotal.com/gui/my-apikey"
    echo ""

    read -p "$(echo -e ${YELLOW}?${NC} Do you want to configure your API key now? \(y/n\): )" -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your VirusTotal API key: " API_KEY
        "$WRAPPER_SCRIPT" config --api-key "$API_KEY"
        echo ""
    else
        echo ""
        echo "You can configure it later by running:"
        echo -e "  ${BLUE}$SYMLINK_NAME config --api-key YOUR_KEY${NC}"
        echo ""
    fi
fi

# Install Quick Action
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Finder Quick Action (Optional)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "This adds a 'VirusTotal Scan' option to the Finder context menu"
echo "(right-click on files)."
echo ""

read -p "$(echo -e ${YELLOW}?${NC} Install Finder Quick Action? \(y/n\): )" -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}→${NC} Creating Quick Action..."
    bash "$SCRIPT_DIR/automator/create_quick_action_v2.sh"
    echo -e "${GREEN}✓${NC} Quick Action installed"
    echo ""
    echo -e "${YELLOW}⚠${NC}  Important: Restart Finder for Quick Action to appear"
    echo "  Run: killall Finder"
fi

# Installation complete
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Usage examples:"
echo -e "  ${BLUE}$SYMLINK_NAME scan file.dmg${NC}           # Scan a file"
echo -e "  ${BLUE}$SYMLINK_NAME scan *.exe${NC}             # Scan multiple files"
echo -e "  ${BLUE}$SYMLINK_NAME scan -r ~/Downloads${NC}    # Scan directory recursively"
echo -e "  ${BLUE}$SYMLINK_NAME hash <sha256>${NC}          # Check hash without upload"
echo -e "  ${BLUE}$SYMLINK_NAME config --show${NC}          # Show configuration"
echo ""
echo "For help:"
echo -e "  ${BLUE}$SYMLINK_NAME --help${NC}"
echo ""
echo -e "${GREEN}Happy scanning!${NC}"
echo ""
