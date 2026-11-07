# -*- mode: python ; coding: utf-8 -*-


# These optional Qt bindings are not used by Clippy's QWidget-based UI.
# Excluding them lets PyInstaller omit their associated frameworks when they
# are not required by the remaining Qt modules.
EXCLUDED_PYSIDE6_MODULES = [
    'PySide6.QtDBus',
    'PySide6.QtPdf',
    'PySide6.QtPdfWidgets',
    'PySide6.QtQml',
    'PySide6.QtQmlModels',
    'PySide6.QtQuick',
    'PySide6.QtQuickControls2',
    'PySide6.QtQuickWidgets',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDED_PYSIDE6_MODULES,
    noarchive=False,
    optimize=0,
)

# The application UI is English-only and never installs a QTranslator. PyInstaller's
# Qt hooks otherwise collect every locale's .qm catalogs (about 6.8 MB here).
a.datas = [entry for entry in a.datas if not entry[0].lower().endswith('.qm')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Clippy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Clippy',
)
app = BUNDLE(
    coll,
    name='Clippy.app',
    icon='icon.icns',
    # A stable bundle identifier lets macOS keep TCC permissions attached to
    # the local app across launches, even while it remains ad-hoc/unsigned.
    bundle_identifier='com.mrstepler.clippy',
)
