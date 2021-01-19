# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

excluded_binaries = [
        'opengl32sw.dll',
        'Qt5Quick.dll',
        'd3dcompiler_47.dll',
        'Qt5Qml.dll',
        'libcrypto-1_1.dll',
        'libGLESv2.dll',
        'tcl86t.dll',
        'tk86t.dll',
        'Qt5Network.dll',
        'ucrtbase.dll']

data_list = [('.\\src\\pomodoro', '.\\pomodoro'), 
             ('.\\LICENSE', '.'),
             ('.\\AUTHOR', '.'),
             ('.\\README.md', '.')]

project_path = ['.']

a = Analysis(['.\\src\\main.py'],
             pathex=project_path,
             binaries=[],
             datas=data_list,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='pomodoro',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='.\\src\\pomodoro\\data\\icons\\tomato.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pomodoro')
