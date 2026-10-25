#!/bin/bash
set -u

FAILURES=0

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "This uninstaller is intended for macOS."
    exit 1
fi

printf 'Removing Clippy and its local data...\n'

# Ask the app to close normally first so it can save pinned clipboard items.
# Match only the actual process name; pkill -f Clippy also matches this script
# when it is launched from a folder or mounted volume named Clippy.
if /usr/bin/pgrep -x Clippy >/dev/null 2>&1; then
    /usr/bin/osascript -e 'tell application "Clippy" to quit' >/dev/null 2>&1 || true

    for _ in 1 2 3 4 5; do
        if ! /usr/bin/pgrep -x Clippy >/dev/null 2>&1; then
            break
        fi
        /bin/sleep 1
    done

    if /usr/bin/pgrep -x Clippy >/dev/null 2>&1; then
        echo "Clippy did not quit normally; stopping its process."
        /usr/bin/pkill -TERM -x Clippy >/dev/null 2>&1 || true
        /bin/sleep 1
        /usr/bin/pkill -KILL -x Clippy >/dev/null 2>&1 || true
    fi
fi

remove_path() {
    local path="$1"

    if [[ ! -e "$path" && ! -L "$path" ]]; then
        printf 'Not found (skipped): %s\n' "$path"
        return 0
    fi

    if /bin/rm -rf "$path" 2>/dev/null; then
        printf 'Removed: %s\n' "$path"
        return 0
    fi

    # /Applications is normally admin-owned. Ask macOS for authorization only
    # when ordinary removal fails; do not hide a failed or cancelled attempt.
    if [[ "$path" == /Applications/* ]] && /usr/bin/osascript \
        -e "do shell script \"/bin/rm -rf '$path'\" with administrator privileges" \
        >/dev/null 2>&1; then
        printf 'Removed with administrator authorization: %s\n' "$path"
        return 0
    fi

    printf 'Could not remove: %s\n' "$path" >&2
    FAILURES=$((FAILURES + 1))
    return 1
}

# Standard install locations used by the DMG instructions, plus the legacy app.
remove_path "/Applications/Clippy.app" || true
remove_path "$HOME/Applications/Clippy.app" || true
remove_path "/Applications/SmartClipboard.app" || true
remove_path "$HOME/Applications/SmartClipboard.app" || true

# Clippy's pinned clipboard data, Qt settings, and caches.
remove_path "$HOME/Library/Application Support/Clippy" || true
remove_path "$HOME/Library/Application Support/SmartClipboard" || true
remove_path "$HOME/Library/Caches/Clippy" || true
remove_path "$HOME/Library/Caches/SmartClipboard" || true
remove_path "$HOME/Library/Preferences/com.clippyapp.Clippy.plist" || true
# Older releases used this incorrect preferences filename.
remove_path "$HOME/Library/Preferences/com.clippy.app.plist" || true
remove_path "$HOME/Library/Logs/Clippy" || true

# The app uses this exact case-sensitive filename.
remove_path "/tmp/Clippy.lock" || true
remove_path "/tmp/clippy.lock" || true
remove_path "/tmp/smart_clipboard.lock" || true

printf '\n'
if [[ "$FAILURES" -eq 0 ]]; then
    echo "Clippy and its local data have been removed."
else
    echo "Some items could not be removed; review the messages above."
fi
cat <<'EOF'

macOS Accessibility and Input Monitoring permissions are managed by System
Settings and are not changed by this script. Remove Clippy there manually if
needed.
EOF

if [[ -t 0 ]]; then
    read -r -p "Press Return to close this window..." _
fi

[[ "$FAILURES" -eq 0 ]]
