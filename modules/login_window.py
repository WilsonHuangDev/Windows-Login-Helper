import wx
import datetime
from modules import ConfigManager, PasswordGenerator, CommandExecutor
from modules.debug_window import DebugLogger


class LoginWindow(wx.Frame):
    def __init__(self):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(None, title="系统登录", size=(380, 220), style=style)
        self._load_config()
        self.init_ui()
        self._init_timer()
        self.Center()

        if self.debug_mode == 1 and self.auth_mode in (2, 3):
            wx.CallAfter(self._log_initial_password)

    def _load_config(self):
        self.config = ConfigManager.get_config()
        self.auth_mode = self.config.get('auth_mode', 0)
        self.static_password = self.config.get('static_password', '')
        self.debug_mode = self.config.get('debug_mode', 0)

    def init_ui(self):
        if self.auth_mode == 0:
            self.bypass_login()
            return

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 密码输入区
        input_sizer = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=10)
        input_sizer.Add(wx.StaticText(panel, label="请输入口令密码："),
                        flag=wx.ALIGN_CENTER_VERTICAL)
        self.password_entry = wx.TextCtrl(panel,
                                          style=wx.TE_PROCESS_ENTER,
                                          size=(200, -1))
        input_sizer.Add(self.password_entry, flag=wx.EXPAND)

        # 按钮区（仅保留验证按钮）
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, label="验证", size=(80, 30))
        btn_sizer.Add(btn_ok, flag=wx.ALIGN_CENTER)

        # 时间显示
        self.time_display = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER)

        main_sizer.Add(input_sizer, 0, wx.ALL | wx.EXPAND, 15)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        main_sizer.Add(self.time_display, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)

        # 绑定事件（已修复）
        btn_ok.Bind(wx.EVT_BUTTON, self.on_login)
        self.password_entry.Bind(wx.EVT_TEXT_ENTER, self.on_login)

    def _init_timer(self):
        """初始化时间显示定时器"""
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_time_display, self.timer)
        self.timer.Start(10)
        self._update_time_display(None)

    def _update_time_display(self, event):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_display.SetLabel(current_time)

    def _debug_print(self, message):
        """修复缺失的调试输出方法"""
        if self.debug_mode == 1:
            DebugLogger.log(message)

    def _log_initial_password(self):
        """安全记录初始口令"""
        try:
            dynamic_pass = PasswordGenerator.generate_dynamic_password()
            self._debug_print(f"初始动态口令: {dynamic_pass}")
        except Exception as e:
            self._debug_print(f"动态口令生成失败: {str(e)}")

    def validate_password(self, input_pass):
        """根据配置验证密码"""
        try:
            input_pass = input_pass.strip()

            # 模式0：无需验证
            if self.auth_mode == 0:
                self._debug_print("模式0：跳过密码验证")
                return True

            # 模式1：仅静态密码
            elif self.auth_mode == 1:
                self._debug_print(f"模式1验证 - 输入密码：{input_pass}")
                if not self.static_password:
                    self._debug_print("静态密码未配置")
                    wx.MessageBox("静态密码未配置！", "配置错误", wx.OK | wx.ICON_ERROR)
                    return False
                return input_pass == self.static_password

            # 模式2：仅动态口令
            elif self.auth_mode == 2:
                current_dynamic = PasswordGenerator.generate_dynamic_password()
                self._debug_print(f"模式2验证 - 输入：{input_pass} 正确口令：{current_dynamic}")
                return input_pass == current_dynamic

            # 模式3：两者均可
            elif self.auth_mode == 3:
                current_dynamic = PasswordGenerator.generate_dynamic_password()
                valid_static = (input_pass == self.static_password) if self.static_password else False
                valid_dynamic = (input_pass == current_dynamic)

                self._debug_print(f"模式3验证 - 输入：{input_pass} 静态验证：{valid_static} 动态验证：{valid_dynamic}")
                return valid_static or valid_dynamic

            # 无效模式
            else:
                self._debug_print(f"无效认证模式：{self.auth_mode}")
                wx.MessageBox("无效的认证模式配置！", "配置错误", wx.OK | wx.ICON_ERROR)
                return False

        except Exception as e:
            error_msg = f"验证失败：{str(e)}"
            self._debug_print(error_msg)
            if self.debug_mode == 1:
                import traceback
                traceback.print_exc()
            wx.MessageBox(error_msg, "错误", wx.OK | wx.ICON_ERROR)
            return False

    def on_login(self, event):
        try:
            input_pass = self.password_entry.GetValue()
            self._debug_print(f"开始验证输入：{input_pass}")

            if self.validate_password(input_pass):
                self._debug_print("验证成功")
                # 创建主窗口但不立即销毁登录窗口
                from modules.main_window import MainWindow
                main_win = MainWindow()
                main_win.Show()
                self.Hide()  # 隐藏登录窗口
            else:
                self._debug_print("验证失败")
                wx.MessageBox("认证失败，请检查输入！", "错误", wx.OK | wx.ICON_ERROR)
                self.password_entry.SetValue("")
        except Exception as e:
            self._debug_print(f"登录异常：{str(e)}")
            wx.MessageBox("发生未知错误！", "错误", wx.OK | wx.ICON_ERROR)

    def bypass_login(self):
        """直接跳过登录"""
        self._debug_print("跳过登录流程")
        from modules.main_window import MainWindow
        main_win = MainWindow()
        main_win.Show()
        self.Hide()
