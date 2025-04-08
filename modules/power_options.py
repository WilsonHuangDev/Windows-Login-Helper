import wx
import ctypes
import platform
from ctypes import wintypes

class PowerOptionsWindow(wx.Frame):
    def __init__(self, parent=None):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(parent, title="电源选项", size=(250, 360), style=style)
        self.parent = parent  # 保存父窗口引用
        self.SetIcon(wx.Icon("Assets/icon.ico"))  # 设置窗口图标
        self.init_ui()
        self.Center()
        
    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 按钮区
        btn_sizer = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=30)
        btn_shutdown = wx.Button(panel, label="关机", size=(130, 40))
        btn_reboot = wx.Button(panel, label="重启", size=(130, 40))
        self.btn_sleep = wx.Button(panel, label="睡眠", size=(130, 40))
        self.btn_hibernate = wx.Button(panel, label="休眠", size=(130, 40))
        btn_back = wx.Button(panel, label="返回", size=(130, 40))

        btn_sizer.Add(btn_shutdown, flag=wx.EXPAND)
        btn_sizer.Add(btn_reboot, flag=wx.EXPAND)
        btn_sizer.Add(self.btn_sleep, flag=wx.EXPAND)
        btn_sizer.Add(self.btn_hibernate, flag=wx.EXPAND)
        btn_sizer.Add(btn_back, flag=wx.EXPAND)

        self._update_button_state()

        tooltip_text = wx.StaticText(panel, label="电源选项", style=wx.ALIGN_CENTER)
        text_font = tooltip_text.GetFont()
        text_font.SetPointSize(12)  # 设置字体大小为12
        text_font.SetWeight(wx.FONTWEIGHT_BOLD)  # 设置字体为粗体
        tooltip_text.SetFont(text_font)

        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tooltip_text, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(2)

        panel.SetSizer(main_sizer)

        btn_shutdown.Bind(wx.EVT_BUTTON, self.on_shutdown)
        btn_reboot.Bind(wx.EVT_BUTTON, self.on_reboot)
        self.btn_sleep.Bind(wx.EVT_BUTTON, self.on_sleep)
        self.btn_hibernate.Bind(wx.EVT_BUTTON, self.on_hibernate)
        btn_back.Bind(wx.EVT_BUTTON, self.on_back)

    # Windows API相关操作
    def _execute_power_action(self, action):
        try:
            if platform.system() != "Windows":
                raise NotImplementedError("仅支持Windows系统")

            # 获取必要函数
            advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
            user32 = ctypes.WinDLL('user32', use_last_error=True)

            # 提权处理
            class TOKEN_PRIVILEGES(ctypes.Structure):
                _fields_ = [
                    ("PrivilegeCount", wintypes.DWORD),
                    ("Luid", wintypes.LUID),
                    ("Attributes", wintypes.DWORD)
                ]

            SE_SHUTDOWN_NAME = "SeShutdownPrivilege"
            TOKEN_ADJUST_PRIVILEGES = 0x0020
            TOKEN_QUERY = 0x0008

            hToken = wintypes.HANDLE()
            advapi32.OpenProcessToken(
                ctypes.windll.kernel32.GetCurrentProcess(),
                TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY,
                ctypes.byref(hToken)
            )

            luid = wintypes.LUID()
            advapi32.LookupPrivilegeValueW(None, SE_SHUTDOWN_NAME, ctypes.byref(luid))

            tp = TOKEN_PRIVILEGES()
            tp.PrivilegeCount = 1
            tp.Luid = luid
            tp.Attributes = 0x00000002  # SE_PRIVILEGE_ENABLED

            advapi32.AdjustTokenPrivileges(
                hToken,
                False,
                ctypes.byref(tp),
                0,
                None,
                None
            )

            # 执行电源操作
            if action == "shutdown":
                ctypes.windll.user32.ExitWindowsEx(0x00000008, 0x00000000)
            elif action == "reboot":
                ctypes.windll.user32.ExitWindowsEx(0x00000002 | 0x00000004, 0)
            elif action == "sleep":
                ctypes.windll.powrprof.SetSuspendState(False, False, False)
            elif action == "hibernate":
                ctypes.windll.powrprof.SetSuspendState(True, False, False)

        except Exception as e:
            wx.MessageBox(f"操作失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
        finally:
            ctypes.windll.kernel32.CloseHandle(hToken)

    def on_shutdown(self, event):
        self._execute_power_action("shutdown")

    def on_reboot(self, event):
        self._execute_power_action("reboot")

    def on_sleep(self, event):
        self._execute_power_action("sleep")

    def on_hibernate(self, event):
        self._execute_power_action("hibernate")

    def on_back(self, event):
        if self.parent:
            self.parent.restore_main_window()

        self.Hide()

    def _update_button_state(self):
        """根据系统电源选项状态更新按钮状态"""
        self.btn_hibernate.Enable()
