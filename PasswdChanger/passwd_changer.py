import ctypes
import os

import wx

from modules.debug_logger import DebugLogger
from modules.window_manager import WindowManager


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
        self.new_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(200, -1))
        grid.Add(self.new_pass, 0, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="确认密码："), 0, wx.ALIGN_CENTER_VERTICAL)
        self.confirm_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(200, -1))
        grid.Add(self.confirm_pass, 0, wx.EXPAND)

        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_change = wx.Button(panel, label="确认修改", size=(80, 30))
        btn_return = wx.Button(panel, label="返回", size=(80, 30))
        btn_change.Bind(wx.EVT_BUTTON, self.on_change)
        btn_return.Bind(wx.EVT_BUTTON, self.on_return)
        self.username.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.new_pass.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.confirm_pass.Bind(wx.EVT_SET_FOCUS, self.on_focus)
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

    def on_focus(self, event):
        """当口令输入框获得焦点时，显示屏幕键盘"""
        DebugLogger.log("[DEBUG] 口令输入框获得焦点，正在尝试显示屏幕键盘")
        self._show_touch_keyboard()
        event.Skip()

    def _show_touch_keyboard(self):
        """显示屏幕键盘"""
        try:
            import subprocess

            # 动态获取屏幕键盘路径
            system_root = os.environ.get("SystemRoot", r"C:\Windows")
            keyboard_path = os.path.join(system_root, "System32", "osk.exe")

            if os.path.exists(keyboard_path):
                ctypes.windll.shell32.ShellExecuteW(None, "open", keyboard_path, None, None, 1)
            else:
                DebugLogger.log("[ERROR] 未找到屏幕键盘程序")
        except Exception as e:
            DebugLogger.log(f"[ERROR] 无法启动屏幕键盘: {str(e)}")

    def on_change(self, event):
        try:
            DebugLogger.log("[DEBUG] 开始执行 修改用户密码 操作")
            from modules.cmd_executor import CommandExecutor
            username = self.username.Value.strip()
            new_pass = self.new_pass.Value
            confirm_pass = self.confirm_pass.Value

            if not self.validate_input(username, new_pass, confirm_pass):
                return

            DebugLogger.log(f"[DEBUG] 被修改密码的用户名: {username}")
            success, msg = CommandExecutor.run_as_admin(["net", "user", username, new_pass])

            # 调试信息已在CommandExecutor中处理
            if success:
                DebugLogger.log("[DEBUG] 修改用户密码操作成功")
                wx.MessageBox("密码修改成功!", "成功", wx.OK | wx.ICON_INFORMATION, parent=self)
            else:
                wx.MessageBox(f"[ERROR] 操作失败: {msg}", "错误", wx.OK | wx.ICON_ERROR, parent=self)
        except (Exception, RuntimeError, NotImplementedError) as e:
            wx.MessageBox(f"[ERROR] 系统错误: {str(e)}", "错误", wx.OK | wx.ICON_ERROR, parent=self)
        finally:
            self.new_pass.Value = ""
            self.confirm_pass.Value = ""
            DebugLogger.log("[DEBUG] 成功安全清除密码记录")

    def validate_input(self, username, p1, p2):
        if not username:
            DebugLogger.log("[ERROR] 用户名为空")
            wx.MessageBox("用户名不能为空!", "错误", wx.OK | wx.ICON_ERROR, parent=self)
            return False
        if p1 != p2:
            DebugLogger.log("[ERROR] 密码输入不一致")
            wx.MessageBox("两次输入的密码不一致!", "错误", wx.OK | wx.ICON_ERROR, parent=self)
            return False
        return True


def run():
    app = wx.App()
    app.MainLoop()
