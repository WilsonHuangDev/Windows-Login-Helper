import wx

from modules.debug_logger import DebugLogger
from modules.window_manager import WindowManager


class UserCreator(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="Windows 登录辅助工具", size=(320, 280), style=style)
        self.SetIcon(wx.Icon("./Assets/icon.ico"))  # 设置窗口图标

        # 绑定关闭窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.init_ui()
        self.Center()
        DebugLogger.log("[DEBUG] UserCreator 初始化完成")

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # 用户名
        sizer.Add(wx.StaticText(panel, label="用户名："),
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.username = wx.TextCtrl(panel, size=(200, -1))
        sizer.Add(self.username, flag=wx.EXPAND)

        # 密码
        sizer.Add(wx.StaticText(panel, label="密码："),
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(200, -1))
        sizer.Add(self.password, flag=wx.EXPAND)

        # 确认密码
        sizer.Add(wx.StaticText(panel, label="确认密码："),
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.confirm_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(200, -1))
        sizer.Add(self.confirm_pass, flag=wx.EXPAND)

        # 用户组选择
        sizer.Add(wx.StaticText(panel, label="用户组："),
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.group_choice = wx.Choice(panel, choices=["标准用户", "管理员"])
        self.group_choice.SetSelection(0)
        sizer.Add(self.group_choice, flag=wx.EXPAND)

        # 按钮布局
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_create = wx.Button(panel, label="创建用户", size=(80, 30))
        btn_return = wx.Button(panel, label="返回", size=(80, 30))
        btn_sizer.Add(btn_create, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_return)

        tittle = wx.StaticText(panel, label="创建用户", style=wx.ALIGN_CENTER)
        tittle_font = tittle.GetFont()
        tittle_font.SetPointSize(12)  # 设置字体大小为12
        tittle_font.SetWeight(wx.FONTWEIGHT_BOLD)  # 设置字体为粗体
        tittle.SetFont(tittle_font)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tittle, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(sizer, 1, flag=wx.ALL | wx.EXPAND, border=15)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=15)

        panel.SetSizer(main_sizer)

        btn_create.Bind(wx.EVT_BUTTON, self.on_create)
        btn_return.Bind(wx.EVT_BUTTON, self.on_return)

    def on_create(self, event):
        try:
            from modules.cmd_executor import CommandExecutor
            username = self.username.Value.strip()
            password = self.password.Value
            confirm = self.confirm_pass.Value

            if not self.validate_input(username, password, confirm):
                return

            # 获取用户组选择
            group = self.group_choice.GetStringSelection()
            is_admin = (group == "管理员")

            # 创建用户命令
            success, msg = CommandExecutor.run_as_admin(["net", "user", username, password, "/add"])
            if not success:
                raise Exception(msg)

            # 设置管理员权限命令
            if is_admin:
                success, msg = CommandExecutor.run_as_admin(
                    ["net", "localgroup", "Users", username, "/delete"]
                )
                success, msg = CommandExecutor.run_as_admin(
                    ["net", "localgroup", "Administrators", username, "/add"]
                )
                if not success:
                    raise Exception(msg)

            wx.MessageBox("用户创建成功!", "成功", wx.OK | wx.ICON_INFORMATION)
        except (Exception, RuntimeError, NotImplementedError) as e:
            wx.MessageBox(f"[ERROR] 创建失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def validate_input(self, user, p1, p2):
        if not user:
            wx.MessageBox("用户名不能为空!", "错误", wx.OK | wx.ICON_ERROR)
            return False
        if p1 != p2:
            wx.MessageBox("两次密码输入不一致!", "错误", wx.OK | wx.ICON_ERROR)
            return False
        return True

    def on_return(self, event):
        from modules.main_window import MainWindow
        DebugLogger.log("[DEBUG] 正在从创建用户窗口返回主窗口")
        WindowManager().switch_window(MainWindow)

    def on_close(self, event):
        """处理关闭窗口事件"""
        DebugLogger.log("[DEBUG] 用户关闭创建用户窗口")
        WindowManager().switch_window(None)
