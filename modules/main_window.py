import datetime
import subprocess
import threading
import wx

from modules.debug_window import DebugLogger
from modules.cmd_executor import CommandExecutor
from modules.config_manager import ConfigManager


class MainWindow(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="Windows 登录辅助工具", size=(250, 400), style=style)
        # 新增实例引用保持
        self._main_window_instance = self
        self.SetIcon(wx.Icon("Assets/icon.ico"))  # 设置窗口图标
        self.init_ui()
        self._init_timer()
        self.Center()
        DebugLogger.log("主窗口初始化完成")

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 按钮区
        btn_sizer = wx.FlexGridSizer(rows=4, cols=1, vgap=15, hgap=30)
        btn_pass = wx.Button(panel, label="修改用户密码", size=(130, 40))
        btn_user = wx.Button(panel, label="创建用户", size=(130, 40))
        btn_cmd = wx.Button(panel, label="CMD 命令行", size=(130, 40))
        self.btn_exit = wx.Button(panel, label="退出登录", size=(130, 40))

        btn_sizer.Add(btn_pass, flag=wx.EXPAND)
        btn_sizer.Add(btn_user, flag=wx.EXPAND)
        btn_sizer.Add(btn_cmd, flag=wx.EXPAND)
        btn_sizer.Add(self.btn_exit, flag=wx.EXPAND)

        self._update_button_state()

        tooltip_text = wx.StaticText(panel, label="请选择功能", style=wx.ALIGN_CENTER)
        text_font = tooltip_text.GetFont()
        text_font.SetPointSize(12)  # 设置字体大小为12
        text_font.SetWeight(wx.FONTWEIGHT_BOLD)  # 设置字体为粗体
        tooltip_text.SetFont(text_font)

        # 时间显示
        self.time_display = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER)

        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tooltip_text, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(2)
        main_sizer.Add(self.time_display, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)

        btn_pass.Bind(wx.EVT_BUTTON, self.on_password)
        btn_user.Bind(wx.EVT_BUTTON, self.on_user_create)
        btn_cmd.Bind(wx.EVT_BUTTON, self.on_cmd)
        self.btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)

    def _init_timer(self):
        # 初始化时间显示定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_time_display, self.timer)
        self.timer.Start(10)
        self._update_time_display(None)  # 立即更新一次

    def _update_time_display(self, event):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_display.SetLabel(current_time)

    def on_password(self, event):
        from PasswdChanger.passwd_changer import PasswordChanger
        PasswordChanger(parent=self).Show()  # 修复点9：传递有效parent
        self.Hide()

    def on_user_create(self, event):
        from PasswdChanger.user_creator import UserCreator
        UserCreator(parent=self).Show()  # 修复点10：传递有效parent
        self.Hide()

    def on_cmd(self, event):
        self.Hide()
        threading.Thread(target=self.run_cmd_window, daemon=True).start()

    def run_cmd_window(self):
        try:
            if CommandExecutor.DEBUG_MODE:
                DebugLogger.log("[DEBUG] 正在启动CMD进程")  # 修改这里

            process = subprocess.Popen(
                "start cmd",
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            process.wait()
        except Exception as e:
            DebugLogger.log(f"CMD进程启动失败: {str(e)}")
        finally:
            wx.CallAfter(self.restore_main_window)

    def restore_main_window(self):
        if not self.IsShown():
            self.Show()
            self.Raise()

    def _update_button_state(self):
        """根据认证模式更新按钮状态"""
        config = ConfigManager.get_config()
        auth_mode = config.get('auth_mode', 0)
        self.btn_exit.Enable(auth_mode != 0)

    def on_exit(self, event):
        """安全退出到认证窗口"""

        def safe_exit():
            from modules.login_window import LoginWindow
            login_win = LoginWindow()
            login_win.Show()
            self.Hide()  # 修复点7：销毁而不是关闭

        wx.CallAfter(safe_exit)  # 修复点8：确保在主线程执行


def run():
    app = wx.App()
    MainWindow().Show()
    app.MainLoop()
