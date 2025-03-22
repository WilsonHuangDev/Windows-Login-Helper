import sys
import os
from cx_Freeze import setup, Executable


# 动态路径处理（确保配置文件生成在程序目录）
def get_target_path(filename):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.getcwd()
    return os.path.join(base_dir, filename)


# 配置排除模块（减少体积）
build_exe_options = {
    "excludes": ["tkinter", "unittest", "pydoc"],  # 排除无用模块
    "include_files": [
        ("PasswdChanger/", "PasswdChanger"),  # 包含子包
        ("modules/", "modules"),  # 包含模块
        # ("icon.ico", "icon.ico")  # 程序图标
    ],
    "bin_includes": ["python3.dll"],  # 显式包含关键 DLL
    "optimize": 2  # 编译优化级别
}

# 主程序配置
base = "Win32GUI" if sys.platform == "win32" else None  # 隐藏终端
executables = [
    Executable(
        "main.py",
        base=base,
        target_name="WinLoginHelper.exe",  # 输出名称
        # icon="icon.ico"  # 图标文件
    )
]

# 打包设置
setup(
    name="Windows-Login-Helper",
    description="Windows 登录辅助工具",
    options={"build_exe": build_exe_options},
    executables=executables
)
