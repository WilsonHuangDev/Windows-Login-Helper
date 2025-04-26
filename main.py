import ctypes
import sys
import traceback
import time

import wx

from modules.config_manager import ConfigManager
from modules.debug_window import DebugLogger
from modules.window_manager import WindowManager


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
                print(f"[ERROR] 提权失败: {ret}")
                return False

            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] 权限请求失败: {str(e)}")
            print("程序将在 10 秒后自动退出...")
            time.sleep(10)
            sys.exit(1)

    @staticmethod
    def main_loop():
        try:
            # 确保单例App实例
            if not wx.GetApp():
                app = wx.App()
            else:
                app = wx.GetApp()

            app.SetExitOnFrameDelete(False)  # 防止最后一个窗口关闭时退出

            logger = DebugLogger()  # 实例化（此时才会创建进程）

            # 读取配置并选择初始窗口类
            config = ConfigManager.get_config()
            auth_mode = config.get('auth_mode', 0)

            if auth_mode == 0:
                DebugLogger.log("[DEBUG] 模式0: 跳过密码验证")
                from modules.main_window import MainWindow
                initial_window_class = MainWindow
            else:
                from modules.login_window import LoginWindow
                initial_window_class = LoginWindow

            # 首次窗口显示
            if not WindowManager().current_window:
                WindowManager().switch_window(initial_window_class)  #动态加载窗口类

            app.MainLoop()

        except Exception as e:
            traceback.print_exc()
            print("程序将在 10 秒后自动退出...")
            time.sleep(10)
            sys.exit(1)


if __name__ == "__main__":
    DebugLogger.log("[DEBUG] 启动运行程序")
    if not ProcessManager.require_admin():
        sys.exit(1)
    ProcessManager.main_loop()
