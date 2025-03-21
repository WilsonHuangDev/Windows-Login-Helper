# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 不打包系统目录文件，只包含代码
added_files = [
    ("PasswdChanger/", "PasswdChanger"),  # 子包目录
    ("modules/", "modules")               # 模块目录
]

a = Analysis(
    ['main.py'],
    pathex=[],                            # 保持为空避免路径干扰
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'wx.lib.pubsub',                  # wxPython 常缺的模块
        'multiprocessing.util',            # 多进程支持
        'PasswdChanger.passwd_changer',
        'PasswdChanger.user_creator'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],                           # 不要排除任何模块
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
    name='Windows-Login-Helper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                             # 压缩可执行文件
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                        # 关键！隐藏终端
    icon='icon.ico'                       # 可选图标
)

# 多文件模式核心配置
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Windows-Login-Helper'
)