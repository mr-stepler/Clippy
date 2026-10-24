# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
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
    codesign_identity='-',  # Ad-hoc signature keeps macOS bundle identity stable.
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
    bundle_identifier='com.mrstepler.clippy',
    codesign_identity='-',
    info_plist={
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '13.0',
    },
)
