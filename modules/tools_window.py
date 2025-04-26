import datetime
import subprocess
import threading
import wx

from modules.debug_window import DebugLogger
from modules.window_manager import WindowManager


class ToolsWindow(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="Windows 登录辅助工具", size=(250, 400), style=style)
        self.SetIcon(wx.Icon("./Assets/icon.ico"))  # 设置窗口图标

        # 绑定关闭窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.init_ui()
        self._init_timer()
        self.Center()
        DebugLogger.log("[DEBUG] ToolsWindow 初始化完成")

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 按钮区
        btn_sizer = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=30)
        btn_taskmgr = wx.Button(panel, label="任务管理器", size=(150, 40))
        btn_run = wx.Button(panel, label="“运行”窗口", size=(150, 40))
        btn_clear = wx.Button(panel, label="清除“运行”窗口历史记录", size=(150, 40))
        btn_cmd = wx.Button(panel, label="CMD 命令行", size=(150, 40))
        btn_return = wx.Button(panel, label="返回", size=(150, 40))

        btn_sizer.Add(btn_taskmgr, flag=wx.EXPAND)
        btn_sizer.Add(btn_run, flag=wx.EXPAND)
        btn_sizer.Add(btn_clear, flag=wx.EXPAND)
        btn_sizer.Add(btn_cmd, flag=wx.EXPAND)
        btn_sizer.Add(btn_return, flag=wx.EXPAND)

        tittle = wx.StaticText(panel, label="更多功能", style=wx.ALIGN_CENTER)
        tittle_font = tittle.GetFont()
        tittle_font.SetPointSize(12)  # 设置字体大小为12
        tittle_font.SetWeight(wx.FONTWEIGHT_BOLD)  # 设置字体为粗体
        tittle.SetFont(tittle_font)

        # 时间显示
        self.time_display = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER)

        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tittle, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(2)
        main_sizer.Add(self.time_display, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)

        btn_taskmgr.Bind(wx.EVT_BUTTON, self.on_run)
        btn_run.Bind(wx.EVT_BUTTON, self.on_run)
        btn_clear.Bind(wx.EVT_BUTTON, self.on_run)
        btn_cmd.Bind(wx.EVT_BUTTON, self.on_run)
        btn_return.Bind(wx.EVT_BUTTON, self.on_return)

    def _init_timer(self):
        # 初始化时间显示定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_time_display, self.timer)
        self.timer.Start(5)
        self._update_time_display(None)  # 立即更新一次
        DebugLogger.log("[DEBUG] ToolsWindow 时间显示定时器初始化完成")

    def _update_time_display(self, event):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_display.SetLabel(current_time)

    def on_run(self, event):
        button = event.GetEventObject()
        label = button.GetLabel()

        if label == "任务管理器":
            threading.Thread(target=self.run_taskmgr, daemon=True).start()
        elif label == "“运行”窗口":
            threading.Thread(target=self.run_run, daemon=True).start()
        elif label == "清除“运行”窗口历史记录":
            confirm = wx.MessageBox(f"确定要清除“运行”窗口历史记录吗?", "确认操作", wx.YES_NO | wx.ICON_QUESTION, parent=self)
            if confirm != wx.YES:
                DebugLogger.log(f"[DEBUG] 用户取消了 清除“运行”窗口历史记录 操作")
                return
            threading.Thread(target=self.run_clear_history, daemon=True).start()
        elif label == "CMD 命令行":
            threading.Thread(target=self.run_cmd, daemon=True).start()

    def run_taskmgr(self):
        try:
            DebugLogger.log("[DEBUG] 正在启动任务管理器进程")

            process = subprocess.Popen(
                "start taskmgr",
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            process.wait()
        except (Exception, RuntimeError, NotImplementedError) as e:
            DebugLogger.log(f"[ERROR] 任务管理器进程启动失败: {str(e)}")
            wx.MessageBox(f"[ERROR] 任务管理器进程启动失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR, parent=self)

    def run_run(self):
        try:
            DebugLogger.log("[DEBUG] 正在开启“运行”窗口")

            process = subprocess.Popen(
                "explorer.exe shell:::{2559a1f3-21d7-11d4-bdaf-00c04f60b9f0}",
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            process.wait()
        except (Exception, RuntimeError, NotImplementedError) as e:
            DebugLogger.log(f"[ERROR] “运行”窗口开启失败: {str(e)}")
            wx.MessageBox(f"[ERROR] “运行”窗口开启失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR, parent=self)

    def run_clear_history(self):
        try:
            DebugLogger.log("[DEBUG] 开始执行 清除“运行”窗口历史记录 操作")
            from modules.cmd_executor import CommandExecutor

            command = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Get-ChildItem -Path 'Registry::HKEY_USERS' | Where-Object { $_.Name -match 'S-1-5-21' } | ForEach-Object { $Path = 'Registry::' + $_.Name + '\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU'; if (Test-Path $Path) { Remove-Item -Path $Path -Recurse -Force } }"
            ]

            success, msg = CommandExecutor.run_as_admin(command)

            # 调试信息已在CommandExecutor中处理
            if success:
                DebugLogger.log("[DEBUG] 成功清除“运行”窗口历史记录")
                wx.MessageBox("成功清除“运行”窗口历史记录!", "成功", wx.OK | wx.ICON_INFORMATION, parent=self)
            else:
                wx.MessageBox(f"[ERROR] 操作失败: {msg}", "错误", wx.OK | wx.ICON_ERROR, parent=self)
        except (Exception, RuntimeError, NotImplementedError) as e:
            wx.MessageBox(f"[ERROR] 系统错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR, parent=self)

    def run_cmd(self):
        try:
            DebugLogger.log("[DEBUG] 正在启动CMD进程")

            process = subprocess.Popen(
                "start cmd",
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            process.wait()
        except (Exception, RuntimeError, NotImplementedError) as e:
            DebugLogger.log(f"[ERROR] CMD进程启动失败: {str(e)}")
            wx.MessageBox(f"[ERROR] CMD进程启动失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR, parent=self)

    def on_return(self, event):
        from modules.main_window import MainWindow
        DebugLogger.log("[DEBUG] 正在从更多功能窗口返回主窗口")
        WindowManager().switch_window(MainWindow)

    def on_close(self, event):
        """处理关闭窗口事件"""
        DebugLogger.log("[DEBUG] 用户关闭更多功能窗口")
        WindowManager().switch_window(None)


def run():
    app = wx.App()
    app.MainLoop()
