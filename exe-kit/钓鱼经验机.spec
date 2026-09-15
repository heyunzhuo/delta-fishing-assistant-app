# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：把钓鱼经验机打成单文件 exe。

用法（在仓库根目录、已装好 PyInstaller 的环境里）：
    pyinstaller --noconfirm --clean 钓鱼经验机.spec

产出：dist/钓鱼经验机.exe
"""

import os
import sys

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# 源码包目录：正常在仓库根目录下执行，脚本所在处即为 fishing_assistant 的父目录。
PACKAGE_DIR = os.path.abspath(os.path.join(SPECPATH, "fishing_assistant"))
if not os.path.isdir(PACKAGE_DIR):
    raise SystemExit(f"找不到源码包目录：{PACKAGE_DIR}（请在仓库根目录执行 pyinstaller）")

# 鱼饵数字模板（0~5.png）是运行时读取的只读资源，必须显式收进包内。
# 打包后由 config.BUNDLE_DIR（sys._MEIPASS）定位，不再依赖 __file__。
datas = collect_data_files("fishing_assistant", includes=["assets/digits/*.png"])
if not datas:
    raise SystemExit("未能收集 assets/digits/*.png，请确认源码完整")

hiddenimports = [
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "PIL.Image",
    "mss.windows",
]

a = Analysis(
    [os.path.join(PACKAGE_DIR, "__main__.py")],
    pathex=[SPECPATH],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "pytest",
        "unittest",
        "pydoc_data",
        "test",
    ],
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
    name="钓鱼经验机",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # 无黑框窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 嵌入 UAC 清单：游戏多以管理员运行，助手必须同级才能发送鼠标输入。
    # 效果是双击直接弹出「是否允许此应用更改…」，不需要右键"以管理员身份运行"。
    # 注意：这两个路径是相对当前工作目录解析的，必须显式拼成绝对路径。
    manifest=os.path.join(SPECPATH, "app.manifest"),
    version=os.path.join(SPECPATH, "version_info.txt"),
    icon=None,
)
