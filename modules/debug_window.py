import os
import datetime
import multiprocessing
import wx


class DebugLogger:
    _instance = None
    debug_mode = False  # 类属性存储调试模式状态
    log_file_path = None  # 日志文件路径

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 设置日志文件路径
            cls._set_log_file_path()
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

    @staticmethod
    def _set_log_file_path():
        # 延迟导入 ConfigManager
        from modules.config_manager import ConfigManager

        # 通过_get_dir_path获取基础目录
        log_dir = ConfigManager._get_dir_path()

        # 拼接日志文件夹路径
        log_folder = os.path.join(log_dir, 'Logs')

        # 动态生成日志文件名
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        log_name = f'debug_{current_date}.log'
        log_path = os.path.join(log_folder, log_name)  # 合并完整路径

        DebugLogger.log_file_path = log_path  # 更新类属性
        DebugLogger.log(f"[DEBUG] 日志文件输出路径: {log_path}")
        return log_path

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
        cls._write_to_file(message)

    @classmethod
    def _write_to_file(cls, message):
        """将日志写入文件"""
        if cls.log_file_path:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(cls.log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"[{timestamp}] {message}\n")


class DebugWindow(wx.Frame):
    def __init__(self, queue):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="调试信息输出", size=(600, 400), style=style)
        self.queue = queue
        self.SetIcon(wx.Icon("Assets/icon.ico"))  # 设置窗口图标
        self.init_ui()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_logs, self.timer)
        self.timer.Start(5)
        self.Show()
        DebugLogger.log("[DEBUG] 调试信息输出窗口初始化完成")

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
