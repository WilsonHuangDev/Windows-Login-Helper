import wx

from modules.debug_logger import DebugLogger


class WindowManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.current_window = None
            cls._instance.pending_window = None
            cls._instance.main_window = None  # 主窗口引用
        return cls._instance

    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window

    def switch_window(self, window_class, *args, **kwargs):
        """支持传入 None 表示退出程序"""
        if window_class is None:
            wx.CallAfter(self._exit_application)  # 通过事件队列安全退出
            return True

        """安全的窗口切换方法（带状态保护）"""
        try:
            DebugLogger.log(f"[WINDOW] 正在切换窗口到 {window_class.__name__}")

            # 如果是主窗口且已存在，则直接显示
            if window_class.__name__ == "MainWindow" and self.main_window:
                DebugLogger.log("[WINDOW] 主窗口已存在")
                self.restore_main_window()
                return True

            # 创建新窗口但不立即显示
            self.pending_window = window_class(*args, **kwargs)
            DebugLogger.log(f"[WINDOW] {window_class.__name__} 实例创建成功")

            # 显示新窗口
            self.pending_window.Show()
            self.pending_window.Raise()
            DebugLogger.log(f"[WINDOW] 已成功显示 {window_class.__name__}")

            # 如果是主窗口，设置主窗口引用
            if window_class.__name__ == "MainWindow":
                self.set_main_window(self.pending_window)

            # 隐藏或销毁旧窗口
            if self.current_window:
                if self.current_window == self.main_window:
                    DebugLogger.log(f"[WINDOW] 正在隐藏主窗口 {self.current_window.__class__.__name__}")
                    self.current_window.Hide()
                else:
                    self._safe_destroy_window(self.current_window)

            # 更新当前窗口引用
            self.current_window = self.pending_window
            self.pending_window = None

            DebugLogger.log(f"[DEBUG] 成功切换至 {window_class.__name__} 窗口")
            return True

        except Exception as e:
            DebugLogger.log(f"[WINDOW] 窗口切换失败: {str(e)}")
            # 确保销毁未显示的待处理窗口
            if self.pending_window:
                self._safe_destroy_window(self.pending_window)
            # 恢复当前窗口
            if self.current_window:
                self.current_window.Raise()
            return False

    def restore_main_window(self):
        """重新显示主窗口并销毁当前窗口"""
        if self.current_window and self.current_window != self.main_window:
            self._safe_destroy_window(self.current_window)

        if self.main_window and not self.main_window.IsShown():
            self.main_window.Show()
            self.main_window.Raise()
            DebugLogger.log("[WINDOW] 主窗口 MainWindow 已重新显示")

        # 更新当前窗口引用为主窗口
        self.current_window = self.main_window

    def _safe_destroy_window(self, window):
        """安全销毁窗口方法"""
        try:
            if window and window.IsShown():
                DebugLogger.log(f"[WINDOW] 正在销毁 {window.__class__.__name__}")
                window.Destroy()
        except Exception as e:
            DebugLogger.log(f"[WINDOW] 窗口销毁失败: {str(e)}")

    def _exit_application(self):
        """安全退出应用程序"""
        if self.current_window:
            self.current_window.Destroy()
        DebugLogger.log("[DEBUG] 结束运行程序")
        wx.GetApp().ExitMainLoop()
