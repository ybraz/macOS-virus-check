#!/bin/bash
###############################################################################
# Test Fresh Installation
# Simulates a clean install by removing existing files and reinstalling
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Testing Fresh Installation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}⚠${NC}  This will remove existing installation and reinstall"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${YELLOW}→${NC} Step 1: Backing up current config..."
if [ -f "$HOME/.config/vt-scanner/config.json" ]; then
    cp "$HOME/.config/vt-scanner/config.json" "/tmp/vt-scanner-config-backup.json"
    echo -e "${GREEN}✓${NC} Config backed up to /tmp/vt-scanner-config-backup.json"
else
    echo -e "${YELLOW}!${NC} No config to backup"
fi

echo ""
echo -e "${YELLOW}→${NC} Step 2: Removing existing installation..."

# Remove CLI
if [ -f "$HOME/.local/bin/vt-check" ]; then
    rm "$HOME/.local/bin/vt-check"
    echo -e "${GREEN}✓${NC} Removed vt-check"
fi

# Remove Quick Action
if [ -d "$HOME/Library/Services/VirusTotal Scan.workflow" ]; then
    rm -rf "$HOME/Library/Services/VirusTotal Scan.workflow"
    echo -e "${GREEN}✓${NC} Removed Quick Action"
fi

# Remove wrapper
if [ -f "$HOME/.local/bin/vt-scan-file" ]; then
    rm "$HOME/.local/bin/vt-scan-file"
    echo -e "${GREEN}✓${NC} Removed wrapper script"
fi

# Remove virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/venv" ]; then
    rm -rf "$SCRIPT_DIR/venv"
    echo -e "${GREEN}✓${NC} Removed virtual environment"
fi

echo ""
echo -e "${YELLOW}→${NC} Step 3: Running fresh installation..."
echo ""

# Run installer with automatic answers
export INSTALL_TEST_MODE=1

# The install.sh script will be run interactively
echo -e "${BLUE}Running: ./install.sh${NC}"
echo ""
echo "Please answer the prompts:"
echo "  - Create virtual environment? y"
echo "  - Configure API key now? n (we'll restore from backup)"
echo "  - Install Finder Quick Action? y"
echo ""

read -p "Press Enter to continue..."

./install.sh

echo ""
echo -e "${YELLOW}→${NC} Step 4: Restoring config..."
if [ -f "/tmp/vt-scanner-config-backup.json" ]; then
    cp "/tmp/vt-scanner-config-backup.json" "$HOME/.config/vt-scanner/config.json"
    chmod 600 "$HOME/.config/vt-scanner/config.json"
    echo -e "${GREEN}✓${NC} Config restored"
    rm "/tmp/vt-scanner-config-backup.json"
fi

echo ""
echo -e "${YELLOW}→${NC} Step 5: Verifying installation..."

# Test CLI
if command -v vt-check &> /dev/null; then
    echo -e "${GREEN}✓${NC} vt-check command is available"
else
    echo -e "${RED}✗${NC} vt-check command not found"
fi

# Test Quick Action
if [ -d "$HOME/Library/Services/VirusTotal Scan.workflow" ]; then
    echo -e "${GREEN}✓${NC} Quick Action workflow exists"
else
    echo -e "${RED}✗${NC} Quick Action workflow not found"
fi

# Test wrapper
if [ -x "$HOME/.local/bin/vt-scan-file" ]; then
    echo -e "${GREEN}✓${NC} Wrapper script exists and is executable"
else
    echo -e "${RED}✗${NC} Wrapper script not found or not executable"
fi

# Test config
if vt-check config --show | grep -q "Not configured"; then
    echo -e "${YELLOW}⚠${NC}  API key not configured (expected if skipped)"
else
    echo -e "${GREEN}✓${NC} API key is configured"
fi

echo ""
echo -e "${YELLOW}→${NC} Step 6: Restarting Finder..."
killall Finder 2>/dev/null || true
echo -e "${GREEN}✓${NC} Finder restarted"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Fresh Installation Test Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo "Next steps:"
echo -e "  1. Test CLI: ${BLUE}vt-check --help${NC}"
echo -e "  2. Test Quick Action: Right-click a file → Quick Actions → VirusTotal Scan"
echo -e "  3. Configure API if needed: ${BLUE}vt-check config --api-key YOUR_KEY${NC}"
echo ""
