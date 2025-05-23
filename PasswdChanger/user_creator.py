import wx


class UserCreator(wx.Frame):
    def __init__(self, parent=None):  # 修复点：正确接收parent参数
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(parent, title="Windows 登录辅助工具", size=(400, 250), style=style)  # 修复点：传递parent给父类
        self.parent = parent  # 保存父窗口引用
        self.init_ui()
        self.Center()

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
        btn_create = wx.Button(panel, label="创建用户")
        btn_return = wx.Button(panel, label="返回")
        btn_sizer.Add(btn_create, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_return)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer, 1, flag=wx.ALL | wx.EXPAND, border=15)
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

            wx.MessageBox("用户创建成功！", "成功", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"创建失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def validate_input(self, user, p1, p2):
        if not user:
            wx.MessageBox("用户名不能为空", "错误", wx.OK | wx.ICON_ERROR)
            return False
        if p1 != p2:
            wx.MessageBox("两次密码输入不一致", "错误", wx.OK | wx.ICON_ERROR)
            return False
        return True

    def on_return(self, event):
        if self.parent:  # 修改点7：直接使用保存的父窗口引用
            self.parent.Show()
        self.Destroy()  # 修改点8：销毁当前窗口
