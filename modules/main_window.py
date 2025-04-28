import datetime
import subprocess
import threading
import wx

from modules.debug_logger import DebugLogger
from modules.config_manager import ConfigManager
from modules.window_manager import WindowManager


class MainWindow(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="Windows 登录辅助工具", size=(250, 400), style=style)
        self.SetIcon(wx.Icon("./Assets/icon.ico"))  # 设置窗口图标

        # 绑定关闭窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.init_ui()
        self._init_timer()
        self.Center()
        DebugLogger.log("[DEBUG] MainWindow 初始化完成")

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 按钮区
        btn_sizer = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=30)
        btn_pass = wx.Button(panel, label="修改用户密码", size=(130, 40))
        btn_user = wx.Button(panel, label="创建用户", size=(130, 40))
        btn_cmd = wx.Button(panel, label="CMD 命令行", size=(130, 40))
        btn_power = wx.Button(panel, label="电源选项", size=(130, 40))
        self.btn_exit = wx.Button(panel, label="退出登录", size=(130, 40))

        btn_sizer.Add(btn_pass, flag=wx.EXPAND)
        btn_sizer.Add(btn_user, flag=wx.EXPAND)
        btn_sizer.Add(btn_cmd, flag=wx.EXPAND)
        btn_sizer.Add(btn_power, flag=wx.EXPAND)
        btn_sizer.Add(self.btn_exit, flag=wx.EXPAND)

        # 设置退出登录按钮样式（程序启动后第3次调用_get_dir_path）
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
        btn_power.Bind(wx.EVT_BUTTON, self.on_power_options)
        self.btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)

    def _init_timer(self):
        # 初始化时间显示定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_time_display, self.timer)
        self.timer.Start(5)
        self._update_time_display(None)  # 立即更新一次
        DebugLogger.log("[DEBUG] 时间显示定时器初始化完成")

    def _update_time_display(self, event):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_display.SetLabel(current_time)

    def on_password(self, event):
        try:
            from PasswdChanger.passwd_changer import PasswordChanger

            DebugLogger.log("[DEBUG] 正在尝试开启修改用户密码窗口")
            if WindowManager().switch_window(PasswordChanger):
                DebugLogger.log("[DEBUG] 成功开启修改用户密码窗口并关闭主窗口")
            else:
                raise RuntimeError("修改用户密码窗口开启失败")

        except (Exception, RuntimeError) as e:
            DebugLogger.log(f"[ERROR] 修改用户密码窗口开启失败: {str(e)}")
            wx.MessageBox(f"[ERROR] 修改用户密码窗口开启失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_user_create(self, event):
        try:
            from PasswdChanger.user_creator import UserCreator

            DebugLogger.log("[DEBUG] 正在尝试开启创建用户窗口")
            if WindowManager().switch_window(UserCreator):
                DebugLogger.log("[DEBUG] 成功开启创建用户窗口并关闭主窗口")
            else:
                raise RuntimeError("创建用户窗口开启失败")

        except (Exception, RuntimeError) as e:
            DebugLogger.log(f"[ERROR] 创建用户窗口开启失败: {str(e)}")
            wx.MessageBox(f"[ERROR] 创建用户窗口开启失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_power_options(self, event):
        try:
            from modules.power_options import PowerOptionsWindow

            DebugLogger.log("[DEBUG] 正在尝试开启电源选项窗口")
            if WindowManager().switch_window(PowerOptionsWindow):
                DebugLogger.log("[DEBUG] 成功开启电源选项窗口并关闭主窗口")
            else:
                raise RuntimeError("电源选项窗口开启失败")

        except (Exception, RuntimeError) as e:
            DebugLogger.log(f"[ERROR] 电源选项窗口开启失败: {str(e)}")
            wx.MessageBox(f"电源选项窗口开启失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_cmd(self, event):
        threading.Thread(target=self.run_cmd_window, daemon=True).start()

    def run_cmd_window(self):
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
            wx.MessageBox(f"[ERROR] CMD进程启动失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def _update_button_state(self):
        """根据认证模式更新按钮状态"""
        try:
            config = ConfigManager.get_config()
            auth_mode = config.get('auth_mode', 0)
            self.btn_exit.Enable(auth_mode != 0)
            DebugLogger.log("[DEBUG] 成功更新按钮状态")
        except (Exception, RuntimeError, NotImplementedError) as e:
            DebugLogger.log(f"[ERROR] 更新按钮状态失败: {str(e)}")
            wx.MessageBox(f"[ERROR] 更新按钮状态失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
            raise RuntimeError(f"[ERROR] 更新按钮状态失败: {str(e)}")

    def on_exit(self, event):
        try:
            from modules.login_window import LoginWindow

            DebugLogger.log("[DEBUG] 正在尝试开启认证窗口")
            if WindowManager().switch_window(LoginWindow):
                DebugLogger.log("[DEBUG] 成功退出至认证窗口并关闭主窗口")
            else:
                raise RuntimeError("认证窗口开启失败")

        except (Exception, RuntimeError) as e:
            DebugLogger.log(f"[ERROR] 认证窗口开启失败: {str(e)}")
            wx.MessageBox(f"认证窗口开启失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_close(self, event):
        """处理关闭窗口事件"""
        DebugLogger.log("[DEBUG] 用户关闭主窗口")
        WindowManager().switch_window(None)


def run():
    app = wx.App()
    MainWindow().Show()
    app.MainLoop()
