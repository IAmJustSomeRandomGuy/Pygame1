# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['game.py'],
             pathex=['C:\\Users\\Adan Mez\\PycharmProjects\\rythm'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['pygame', 'pkg_resources'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += Tree("C:/Users/Adan Mez/AppData/Roaming/Python/Python38/site-packages/pygame", prefix= "pygame")
a.datas += Tree("C:/Users/Adan Mez/AppData/Local/Programs/Python/Python38/Lib/site-packages/pkg_resources", prefix= "pkg_resources")
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
