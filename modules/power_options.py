import wx
import ctypes
import platform
from ctypes import wintypes

class PowerOptionsWindow(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(parent, title="电源选项", size=(250, 300))
        self.parent = parent
        self.init_ui()
        self.Center()
        
    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        buttons = [
            ("关机", self.on_shutdown),
            ("重启", self.on_reboot),
            ("睡眠", self.on_sleep),
            ("休眠", self.on_hibernate),
            ("返回", self.on_back)
        ]

        for label, handler in buttons:
            btn = wx.Button(panel, label=label, size=(150, 40))
            btn.Bind(wx.EVT_BUTTON, handler)
            sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)

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
        self.Hide()
        if self.parent:
            self.parent.restore_main_window()
