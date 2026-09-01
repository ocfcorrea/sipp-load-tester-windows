# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Coleta arquivos de assets do customtkinter
ctk_datas = collect_data_files('customtkinter')

# Arquivos adicionais de dados do projeto a embutir no .exe
datas = [
    ('pcap', 'pcap'),
    ('scenarios', 'scenarios'),
    ('bin/sipp', 'bin/sipp'),
    ('docs', 'docs'),
    ('.env.example', '.')
]
if os.path.exists('version.json'):
    datas.append(('version.json', '.'))
datas += ctk_datas

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'packaging',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'dotenv',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog'
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
    name='SIPp_Load_Tester_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Janela limpa sem terminal preto de fundo
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
