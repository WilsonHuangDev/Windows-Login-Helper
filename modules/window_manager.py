import wx

from modules.debug_window import DebugLogger


class WindowManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.current_window = None
        return cls._instance

    def switch_window(self, window_class, *args, **kwargs):
        """安全的窗口切换方法"""
        try:
            DebugLogger.log(f"[WINDOW] 正在切换到 {window_class.__name__}")

            # 先创建新窗口
            new_window = window_class(*args, **kwargs)
            new_window.Show()

            # 再销毁旧窗口
            if self.current_window:
                DebugLogger.log(f"[WINDOW] 正在销毁 {self.current_window.__class__.__name__}")
                self.current_window.Destroy()

            self.current_window = new_window
            DebugLogger.log(f"[WINDOW] 成功切换到 {window_class.__name__}")
            return new_window

        except Exception as e:
            DebugLogger.log(f"[WINDOW] 窗口切换失败: {str(e)}")
            raise
