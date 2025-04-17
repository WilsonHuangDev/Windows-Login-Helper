import wx


class WindowManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.current_window = None
        return cls._instance

    def switch_window(self, window_class, *args, **kwargs):
        """切换窗口并自动销毁前一个窗口"""
        if self.current_window:
            self.current_window.Destroy()

        self.current_window = window_class(*args, **kwargs)
        self.current_window.Show()
        return self.current_window

    def get_current(self):
        """获取当前活动窗口"""
        return self.current_window
