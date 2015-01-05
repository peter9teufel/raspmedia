# -*- mode: python -*-
a = Analysis(['RaspMediaCopyTool.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas + Tree('img', 'img'),
          name='RaspMedia Copy Tool' + ('.exe' if sys.platform == 'win32' else ''),
          debug=False,
          strip=None,
          upx=True,
          console=(True if sys.platform == 'win32' else False),
          icon='img/ic_main.ico')
if sys.platform == 'darwin':
    app = BUNDLE(exe,
             name='RaspMedia Copy Tool.app',
             icon='img/ic_main.icns')
