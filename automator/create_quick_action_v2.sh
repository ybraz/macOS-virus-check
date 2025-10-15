#!/bin/bash
###############################################################################
# Create VirusTotal Quick Action for macOS Finder (Version 2 - Fixed)
#
# This version creates a more robust Quick Action that doesn't depend
# on hardcoded paths
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKFLOW_DIR="$HOME/Library/Services"
WORKFLOW_NAME="VirusTotal Scan.workflow"
WORKFLOW_PATH="$WORKFLOW_DIR/$WORKFLOW_NAME"

echo "Creating VirusTotal Quick Action (v2)..."
echo "Project root: $PROJECT_ROOT"

# Remove old workflow if exists
if [ -d "$WORKFLOW_PATH" ]; then
    echo "Removing old workflow..."
    rm -rf "$WORKFLOW_PATH"
fi

# Create Services directory if it doesn't exist
mkdir -p "$WORKFLOW_DIR"

# Create wrapper script that will be called by the Quick Action
WRAPPER_SCRIPT="$HOME/.local/bin/vt-scan-file"
mkdir -p "$HOME/.local/bin"

cat > "$WRAPPER_SCRIPT" << 'WRAPPER_EOF'
#!/bin/bash
# VirusTotal Quick Action Wrapper Script

# Find the vt-check command
if command -v vt-check &> /dev/null; then
    VT_CHECK="vt-check"
elif [ -x "$HOME/.local/bin/vt-check" ]; then
    VT_CHECK="$HOME/.local/bin/vt-check"
else
    # Try to find project location
    PROJECT_DIRS=(
        "$HOME/macos-virus-check"
        "$HOME/projects/macos-virus-check"
        "$HOME/Documents/macos-virus-check"
        "$HOME/Downloads/macos-virus-check"
    )

    for dir in "${PROJECT_DIRS[@]}"; do
        if [ -f "$dir/src/cli.py" ]; then
            export PYTHONPATH="$dir/src:$PYTHONPATH"
            VT_CHECK="python3 $dir/src/cli.py"
            break
        fi
    done
fi

# If still not found, show error
if [ -z "$VT_CHECK" ]; then
    osascript -e 'display notification "vt-check not found. Please install first." with title "❌ VirusTotal Scanner" sound name "Basso"'
    exit 1
fi

# Scan the file
for file in "$@"; do
    (
        # Show scanning notification
        osascript -e "display notification \"Scanning $(basename "$file")...\" with title \"🔍 VirusTotal Scanner\""

        # Run scan with notification
        $VT_CHECK scan --notify "$file" 2>&1 | logger -t virustotal-scan
    ) &
done
WRAPPER_EOF

chmod +x "$WRAPPER_SCRIPT"

# Create the workflow using Automator CLI (if available) or manual structure
echo "Creating workflow structure..."

# Create the workflow directory structure
mkdir -p "$WORKFLOW_PATH/Contents"

# Create Info.plist
cat > "$WORKFLOW_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>VirusTotal Scan</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <dict>
                <key>NSApplicationIdentifier</key>
                <string>com.apple.finder</string>
            </dict>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.item</string>
            </array>
        </dict>
    </array>
    <key>CFBundleIdentifier</key>
    <string>com.virustotal.quickaction</string>
    <key>CFBundleName</key>
    <string>VirusTotal Scan</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
EOF

# Create document.wflow with the wrapper script path
cat > "$WORKFLOW_PATH/Contents/document.wflow" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>521.1</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.3</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <dict/>
                    <key>CheckedForUserDefaultShell</key>
                    <dict/>
                    <key>inputMethod</key>
                    <dict/>
                    <key>shell</key>
                    <dict/>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>$HOME/.local/bin/vt-scan-file "$@"</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>2.0.3</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>A1B2C3D4-E5F6-G7H8-I9J0-K1L2M3N4O5P6</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                    <string>Run</string>
                    <string>Unix</string>
                </array>
                <key>OutputUUID</key>
                <string>B2C3D4E5-F6G7-H8I9-J0K1-L2M3N4O5P6Q7</string>
                <key>UUID</key>
                <string>C3D4E5F6-G7H8-I9J0-K1L2-M3N4O5P6Q7R8</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <integer>0</integer>
                        <key>name</key>
                        <string>inputMethod</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                    <key>1</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>source</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>1</string>
                    </dict>
                    <key>2</key>
                    <dict>
                        <key>default value</key>
                        <false/>
                        <key>name</key>
                        <string>CheckedForUserDefaultShell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>2</string>
                    </dict>
                    <key>3</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>COMMAND_STRING</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>3</string>
                    </dict>
                    <key>4</key>
                    <dict>
                        <key>default value</key>
                        <string>/bin/sh</string>
                        <key>name</key>
                        <string>shell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>4</string>
                    </dict>
                </dict>
                <key>conversionLabel</key>
                <integer>0</integer>
                <key>isViewVisible</key>
                <true/>
                <key>location</key>
                <string>449.000000:316.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <true/>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>serviceInputTypeIdentifier</key>
        <string>com.apple.Automator.fileSystemObject</string>
        <key>serviceOutputTypeIdentifier</key>
        <string>com.apple.Automator.nothing</string>
        <key>serviceProcessesInput</key>
        <integer>0</integer>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.servicesMenu</string>
    </dict>
</dict>
</plist>
EOF

echo ""
echo "✅ Quick Action created successfully!"
echo ""
echo "Files created:"
echo "  • Workflow: $WORKFLOW_PATH"
echo "  • Wrapper: $WRAPPER_SCRIPT"
echo ""
echo "The 'VirusTotal Scan' option will appear in:"
echo "  • Finder → Right-click on any file → Quick Actions → VirusTotal Scan"
echo "  • Or: Right-click → Services → VirusTotal Scan"
echo ""
echo "⚠️  Important next steps:"
echo "  1. Restart Finder: killall Finder"
echo "  2. Or log out and log back in"
echo "  3. First time you run it, macOS may ask for Automator permissions"
echo ""
echo "To remove: rm -rf '$WORKFLOW_PATH' '$WRAPPER_SCRIPT'"
echo ""
