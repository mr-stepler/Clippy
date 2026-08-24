#!/bin/bash

echo "🗑 Removing Clippy and all associated data..."

# 1. Terminate running processes
pkill -f Clippy 2>/dev/null
pkill -f SmartClipboard 2>/dev/null

# 2. Remove application bundles
rm -rf /Applications/Clippy.app 2>/dev/null
rm -rf /Applications/SmartClipboard.app 2>/dev/null

# 3. Clean up temporary files, logs, caches, and user preferences
rm -f /tmp/clippy.lock 2>/dev/null
rm -f /tmp/smart_clipboard.lock 2>/dev/null
rm -rf ~/Library/Application\ Support/Clippy 2>/dev/null
rm -rf ~/Library/Application\ Support/SmartClipboard 2>/dev/null
rm -rf ~/Library/Caches/Clippy 2>/dev/null
rm -rf ~/Library/Preferences/com.clippy.app.plist 2>/dev/null

# 4. Relaunch Finder
killall Finder

echo ""
echo "✅ Clippy and all related files have been successfully removed!"
read -p "Press Enter to close this window..."