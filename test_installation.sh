#!/bin/bash
###############################################################################
# Test installation script
# Verify that the VirusTotal scanner is properly installed and configured
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  VirusTotal Scanner - Installation Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: Check if command exists
echo -e "${YELLOW}→${NC} Testing CLI command availability..."
if command -v vt-check &> /dev/null; then
    echo -e "${GREEN}✓${NC} vt-check command is available"
else
    echo -e "${RED}✗${NC} vt-check command not found in PATH"
    echo "  Try running the installation script: ./install.sh"
    exit 1
fi

# Test 2: Check Python modules
echo -e "${YELLOW}→${NC} Testing Python module imports..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 << EOF
import sys
sys.path.insert(0, '$SCRIPT_DIR/src')

try:
    import vt_scanner
    import config
    import utils
    import cli
    print("${GREEN}✓${NC} All Python modules import successfully")
except ImportError as e:
    print("${RED}✗${NC} Import error: " + str(e))
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Module import test failed"
    exit 1
fi

# Test 3: Check dependencies
echo -e "${YELLOW}→${NC} Testing dependencies..."
python3 << EOF
import sys

required_modules = ['requests', 'click', 'rich']
missing = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print("${RED}✗${NC} Missing dependencies: " + ", ".join(missing))
    print("  Run: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("${GREEN}✓${NC} All dependencies installed")
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

# Test 4: Check configuration
echo -e "${YELLOW}→${NC} Testing configuration..."
vt-check config --show > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Configuration accessible"
else
    echo -e "${RED}✗${NC} Configuration test failed"
    exit 1
fi

# Test 5: Check API key
echo -e "${YELLOW}→${NC} Checking API key configuration..."
if vt-check config --show 2>&1 | grep -q "Not configured"; then
    echo -e "${YELLOW}⚠${NC}  API key not configured"
    echo "  Configure with: vt-check config --api-key YOUR_KEY"
else
    echo -e "${GREEN}✓${NC} API key is configured"
fi

# Test 6: Check Quick Action (optional)
echo -e "${YELLOW}→${NC} Checking Quick Action installation..."
WORKFLOW_PATH="$HOME/Library/Services/VirusTotal Scan.workflow"
if [ -d "$WORKFLOW_PATH" ]; then
    echo -e "${GREEN}✓${NC} Quick Action installed"
else
    echo -e "${YELLOW}⚠${NC}  Quick Action not installed (optional)"
    echo "  Install with: ./automator/create_quick_action.sh"
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation Test Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo -e "  1. Configure API key: ${BLUE}vt-check config --api-key YOUR_KEY${NC}"
echo -e "  2. Test a scan: ${BLUE}vt-check scan /path/to/file${NC}"
echo -e "  3. View help: ${BLUE}vt-check --help${NC}"
echo ""
