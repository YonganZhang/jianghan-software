# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'uvicorn', 
    'fastapi', 
    'pysr', 
    'julia',
    'sklearn',
    'sklearn.utils._cython_blas', 
    'sklearn.neighbors.typedefs',
    'engineio.async_drivers.threading',
    'socketio',
    'jinja2.ext',  # If templates used
]

# Add 'blueprints' folder and others
# Format: (Source Path, Destination Path)
datas = [
    ('blueprints', 'blueprints'),
    ('models_lib', 'models_lib'),
    ('tools', 'tools'),
    ('表头文件', '表头文件'),
    ('运行前设置', '运行前设置'),
    ('绘图', '绘图'),
    ('config.py', '.'),
    ('exts.py', '.'),
    ('models.py', '.'),
    ('check_and_fix_database.py', '.'),
    ('init_user_directories.py', '.'),
]

# Exclude heavy modules not needed on runtime if possible (optional)
excludes = ['tkinter', 'IPython', 'notebook', 'matplotlib.tests', 'numpy.tests']

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging, False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend',
)
