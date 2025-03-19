import datetime
import multiprocessing

import wx


class DebugLogger:
    _instance = None
    debug_mode = False  # 类属性存储调试模式状态

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 仅在调试模式启用时初始化队列和进程
            if cls.debug_mode:
                cls.queue = multiprocessing.Queue()
                cls.process = multiprocessing.Process(
                    target=cls._run_debug_window,
                    args=(cls.queue,),
                    daemon=True
                )
                cls.process.start()
        return cls._instance

    @classmethod
    def set_debug_mode(cls, debug_mode: bool):
        """设置调试模式的类方法"""
        cls.debug_mode = debug_mode

    @classmethod
    def _run_debug_window(cls, queue):
        """调试窗口进程入口"""
        app = wx.App()
        frame = DebugWindow(queue)
        app.MainLoop()

    @classmethod
    def log(cls, message):
        """线程安全的日志记录方法"""
        if cls.debug_mode and hasattr(cls, 'queue'):
            cls.queue.put(message)


class DebugWindow(wx.Frame):
    def __init__(self, queue):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="调试信息", size=(600, 400), style=style)
        self.queue = queue
        self.init_ui()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_logs, self.timer)
        self.timer.Start(100)
        self.Show()

    def init_ui(self):
        panel = wx.Panel(self)
        self.log_text = wx.TextCtrl(panel,
                                    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
                                    size=(580, 380))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)

    def update_logs(self, event):
        """定时更新日志内容"""
        while not self.queue.empty():
            try:
                msg = self.queue.get_nowait()
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                self.log_text.AppendText(f"[{timestamp}] {msg}\n")
            except:
                break


def run_debug_window(queue):
    app = wx.App()
    DebugWindow(queue)
    app.MainLoop()
