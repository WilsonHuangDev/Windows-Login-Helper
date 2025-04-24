import wx

from modules.debug_window import DebugLogger
from modules.window_manager import WindowManager


class SecurePasswordTextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER,
            size=(200, -1))
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def on_key_down(self, event):
        if event.ControlDown() and event.GetKeyCode() in (ord('C'), ord('V')):
            return
        event.Skip()


class PasswordChanger(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="Windows 登录辅助工具", size=(320, 250), style=style)
        self.SetIcon(wx.Icon("./Assets/icon.ico"))  # 设置窗口图标

        # 绑定关闭窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.init_ui()
        self.Center()
        DebugLogger.log("[DEBUG] PasswordChanger 初始化完成")

    def init_ui(self):
        panel = wx.Panel(self)
        grid = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)

        grid.Add(wx.StaticText(panel, label="用户名："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.username = wx.TextCtrl(panel, size=(200, -1))
        grid.Add(self.username, 0, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="新密码："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.new_pass = SecurePasswordTextCtrl(panel)
        grid.Add(self.new_pass, 0, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="确认密码："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.confirm_pass = SecurePasswordTextCtrl(panel)
        grid.Add(self.confirm_pass, 0, wx.EXPAND)

        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_change = wx.Button(panel, label="确认修改", size=(80, 30))
        btn_return = wx.Button(panel, label="返回", size=(80, 30))
        btn_change.Bind(wx.EVT_BUTTON, self.on_change)
        btn_return.Bind(wx.EVT_BUTTON, self.on_return)
        btn_box.Add(btn_change, 0, wx.RIGHT, 10)
        btn_box.Add(btn_return)

        tittle = wx.StaticText(panel, label="修改用户密码", style=wx.ALIGN_CENTER)
        tittle_font = tittle.GetFont()
        tittle_font.SetPointSize(12)  # 设置字体大小为12
        tittle_font.SetWeight(wx.FONTWEIGHT_BOLD)  # 设置字体为粗体
        tittle.SetFont(tittle_font)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tittle, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 15)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_box, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        panel.SetSizer(main_sizer)

    def on_return(self, event):
        from modules.main_window import MainWindow
        DebugLogger.log("[DEBUG] 正在从修改用户密码窗口返回主窗口")
        WindowManager().switch_window(MainWindow)

    def on_close(self, event):
        """处理关闭窗口事件"""
        DebugLogger.log("[DEBUG] 用户关闭修改用户密码窗口")
        WindowManager().switch_window(None)

    def on_change(self, event):
        try:
            from modules.cmd_executor import CommandExecutor
            username = self.username.Value.strip()
            new_pass = self.new_pass.Value
            confirm_pass = self.confirm_pass.Value

            if not self.validate_input(username, new_pass, confirm_pass):
                return

            success, msg = CommandExecutor.run_as_admin(["net", "user", username, new_pass])

            # 调试信息已在CommandExecutor中处理
            if success:
                wx.MessageBox("密码修改成功!", "成功", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox(f"[ERROR] 操作失败: {msg}", "错误", wx.OK | wx.ICON_ERROR)
        except (Exception, RuntimeError, NotImplementedError) as e:
            wx.MessageBox(f"[ERROR] 系统错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        finally:
            self.new_pass.Value = ""
            self.confirm_pass.Value = ""

    def validate_input(self, username, p1, p2):
        if not username:
            wx.MessageBox("用户名不能为空!", "错误", wx.OK | wx.ICON_ERROR)
            return False
        if p1 != p2:
            wx.MessageBox("两次输入的密码不一致!", "错误", wx.OK | wx.ICON_ERROR)
            return False
        return True


def run():
    app = wx.App()
    app.MainLoop()
