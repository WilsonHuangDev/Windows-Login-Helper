import ctypes
import sys
import traceback

import wx

from modules import ConfigManager
from modules.debug_window import DebugLogger


class ProcessManager:
    @staticmethod
    def require_admin():
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                return True

            params = ' '.join([f'"{arg}"' for arg in sys.argv])
            ret = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1
            )

            if ret <= 32:
                print(f"提权失败，错误代码: {ret}")
                return False

            sys.exit(0)
        except Exception as e:
            print(f"权限请求失败: {str(e)}")
            input("按回车退出...")
            sys.exit(1)

    @staticmethod
    def main_loop():
        try:
            # 确保只创建一个 wx.App 实例
            app = wx.App() if not wx.GetApp() else wx.GetApp()

            # 加载配置
            config = ConfigManager.get_config()
            debug_mode = config.get('debug_mode', 0) == 1

            # 设置调试模式（关键修复点）
            DebugLogger.set_debug_mode(debug_mode)  # 使用正确的类方法
            logger = DebugLogger()  # 实例化（此时才会创建进程）

            # 创建主窗口或登录窗口
            if config.get('auth_mode', 0) == 0:
                from modules.main_window import MainWindow
                frame = MainWindow()
            else:
                from modules.login_window import LoginWindow
                frame = LoginWindow()

            frame.Show()
            app.MainLoop()

        except Exception as e:
            traceback.print_exc()
            input("发生错误，按回车退出...")


if __name__ == "__main__":
    if not ProcessManager.require_admin():
        sys.exit(1)
    ProcessManager.main_loop()
