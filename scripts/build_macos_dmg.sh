#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "This build script must run on macOS." >&2
    exit 1
fi

for tool in sips iconutil hdiutil; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Required macOS tool not found: $tool" >&2
        exit 1
    fi
done

TEMP_DIR="$(mktemp -d)"
ICON_FILE="$ROOT_DIR/icon.icns"
HAD_ORIGINAL_ICON=0
if [[ -f "$ICON_FILE" ]]; then
    cp "$ICON_FILE" "$TEMP_DIR/original-icon.icns"
    HAD_ORIGINAL_ICON=1
fi
cleanup() {
    if (( HAD_ORIGINAL_ICON )); then
        cp "$TEMP_DIR/original-icon.icns" "$ICON_FILE"
    else
        rm -f "$ICON_FILE"
    fi
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT
ICONSET_DIR="$TEMP_DIR/Clippy.iconset"
STAGING_DIR="$TEMP_DIR/Clippy-dmg"
OUTPUT_DMG="$ROOT_DIR/dist/Clippy.dmg"
mkdir -p "$ICONSET_DIR" "$STAGING_DIR" "$ROOT_DIR/dist"

# Clippy.spec expects icon.icns. Generate the standard macOS iconset from the
# checked-in source image so builds do not depend on an ignored local file.
for size in 16 32 128 256 512; do
    sips -s format png -z "$size" "$size" "$ROOT_DIR/icon.JPG" \
        --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
    if (( size < 512 )); then
        double_size=$((size * 2))
        sips -s format png -z "$double_size" "$double_size" "$ROOT_DIR/icon.JPG" \
            --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
    fi
done
iconutil -c icns "$ICONSET_DIR" -o "$ROOT_DIR/icon.icns"

python3 -m PyInstaller --noconfirm --clean Clippy.spec
APP_BUNDLE="$ROOT_DIR/dist/Clippy.app"
if [[ ! -d "$APP_BUNDLE" ]]; then
    echo "PyInstaller did not produce $APP_BUNDLE" >&2
    exit 1
fi

cp -R "$APP_BUNDLE" "$STAGING_DIR/Clippy.app"
cp "$ROOT_DIR/uninstall.command" "$STAGING_DIR/uninstall.command"
chmod +x "$STAGING_DIR/uninstall.command"
ln -s /Applications "$STAGING_DIR/Applications"
rm -f "$OUTPUT_DMG"
hdiutil create \
    -volname "Clippy" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    "$OUTPUT_DMG"

echo "Created $OUTPUT_DMG"
