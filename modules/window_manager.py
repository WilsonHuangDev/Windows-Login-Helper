import wx

from modules.debug_window import DebugLogger


class WindowManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.current_window = None
            cls._instance.pending_window = None  # 新增待处理窗口状态
        return cls._instance

    def switch_window(self, window_class, *args, **kwargs):
        """安全的窗口切换方法（带状态保护）"""
        try:
            DebugLogger.log(f"[WINDOW] 正在切换窗口到 {window_class.__name__}")

            # 创建新窗口但不立即显示
            self.pending_window = window_class(*args, **kwargs)
            DebugLogger.log(f"[WINDOW] {window_class.__name__} 实例创建成功")

            # 先显示新窗口
            self.pending_window.Show()
            self.pending_window.Raise()
            DebugLogger.log(f"[WINDOW] {window_class.__name__} 已成功显示")

            # 延迟销毁旧窗口（关键修复）
            if self.current_window:
                DebugLogger.log(f"[WINDOW] 计划销毁 {self.current_window.__class__.__name__}")
                wx.CallLater(100, self._safe_destroy_window, self.current_window)

            # 更新当前窗口引用
            self.current_window = self.pending_window
            self.pending_window = None

            DebugLogger.log(f"[DEBUG] 成功开启 {window_class.__name__} 窗口")
            return True

        except Exception as e:
            DebugLogger.log(f"[WINDOW] 窗口切换失败: {str(e)}")
            if self.pending_window:
                self.pending_window.Destroy()
            if self.current_window:
                self.current_window.Raise()
            return False

    def _safe_destroy_window(self, window):
        """安全销毁窗口方法"""
        try:
            if window and window.IsShown():
                DebugLogger.log(f"[WINDOW] 正在销毁 {window.__class__.__name__}")
                window.Destroy()
        except Exception as e:
            DebugLogger.log(f"[WINDOW] 窗口销毁失败: {str(e)}")
