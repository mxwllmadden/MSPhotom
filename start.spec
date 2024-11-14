from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os

hidden_imports = [
    'PIL',
    'tkinter',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'concurrent.futures',
    'numpy',
    'asyncio',
    'nest_asyncio',
    'h5py',
    'cv2'
]

a = Analysis(
    ['start.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,X
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MSPhotomApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='MSPhotomApp'
)
