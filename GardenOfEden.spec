# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['MainMenuPage.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Audio', 'Audio'),
        ('font', 'font'),
        ('Sprites', 'Sprites'),
        ('StoryImages', 'StoryImages'),
        ('*.png', '.'),
        ('*.jpg', '.'),
        ('*.tmx', '.'),
    ],
    hiddenimports=[
        'pygame',
        'pytmx',
        'display_scaler',
        'resource_path',
        'Start',
        'Prologue',
        'CharactersPage',
        'TheNaga',
        'TheTwins',
        'TheGuardian',
        'TheStatues',
        'TheGarden',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GardenOfEden',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add 'icon.ico' here if you have an icon file
)
