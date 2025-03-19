import datetime
import subprocess
import threading
import wx

from modules.debug_window import DebugLogger
from .cmd import CommandExecutor


class MainWindow(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU
        super().__init__(None, title="系统工具集", size=(500, 250), style=style)
        self.init_ui()
        self._init_timer()
        self.Center()

        # 确保窗口关闭时完全退出
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # 时间显示相关
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_time_display)
        self.timer.Start(10)

        DebugLogger.log("主窗口初始化完成")

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 按钮区
        btn_sizer = wx.FlexGridSizer(rows=1, cols=3, vgap=15, hgap=30)
        btn_pass = wx.Button(panel, label="修改用户密码", size=(130, 40))
        btn_user = wx.Button(panel, label="创建新用户", size=(130, 40))
        btn_cmd = wx.Button(panel, label="命令行工具", size=(130, 40))

        btn_sizer.Add(btn_pass, flag=wx.EXPAND)
        btn_sizer.Add(btn_user, flag=wx.EXPAND)
        btn_sizer.Add(btn_cmd, flag=wx.EXPAND)

        # 时间显示
        self.time_display = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER)

        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.time_display, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)

        btn_pass.Bind(wx.EVT_BUTTON, self.on_password)
        btn_user.Bind(wx.EVT_BUTTON, self.on_user_create)
        btn_cmd.Bind(wx.EVT_BUTTON, self.on_cmd)

    def _init_timer(self):
        # 初始化时间显示定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_time_display, self.timer)
        self.timer.Start(10)
        self._update_time_display(None)  # 立即更新一次

    def _update_time_display(self, event):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_display.SetLabel(current_time)

    def on_close(self, event):
        # 完全销毁窗口
        self.Destroy()
        # 如果这是最后一个窗口，退出主循环
        if wx.GetApp().GetTopWindow() is None:
            print("MainWindow closing.")
            wx.GetApp().Exit()

    def on_password(self, event):
        from PasswdChanger.passwd import PasswordChanger
        PasswordChanger().Show()
        self.Close()

    def on_user_create(self, event):
        from PasswdChanger.user_creator import UserCreator
        UserCreator().Show()
        self.Close()

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


def run():
    app = wx.App()
    MainWindow().Show()
    app.MainLoop()
