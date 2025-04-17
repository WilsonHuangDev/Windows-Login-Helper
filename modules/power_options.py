import wx
import ctypes
import platform

from ctypes import wintypes
from modules.debug_window import DebugLogger


# 定义 LUID 结构体
class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG),
    ]

# 定义 SYSTEM_POWER_CAPABILITIES 结构体
class SYSTEM_POWER_CAPABILITIES(ctypes.Structure):
    _fields_ = [
        ("PowerButtonPresent", wintypes.BOOLEAN),
        ("SleepButtonPresent", wintypes.BOOLEAN),
        ("LidPresent", wintypes.BOOLEAN),
        ("SystemS1", wintypes.BOOLEAN),
        ("SystemS2", wintypes.BOOLEAN),
        ("SystemS3", wintypes.BOOLEAN),  # 睡眠支持
        ("SystemS4", wintypes.BOOLEAN),  # 休眠支持
        ("SystemS5", wintypes.BOOLEAN),
        ("HiberFilePresent", wintypes.BOOLEAN),
        ("FullWake", wintypes.BOOLEAN),
        ("VideoDimPresent", wintypes.BOOLEAN),
        ("ApmPresent", wintypes.BOOLEAN),
        ("UpsPresent", wintypes.BOOLEAN),
        ("ThermalControl", wintypes.BOOLEAN),
        ("ProcessorThrottle", wintypes.BOOLEAN),
        ("ProcessorMinThrottle", ctypes.c_ubyte),
        ("ProcessorMaxThrottle", ctypes.c_ubyte),
        ("FastSystemS4", wintypes.BOOLEAN),
        ("Hiberboot", wintypes.BOOLEAN),
        ("WakeAlarmPresent", wintypes.BOOLEAN),
        ("AoAc", wintypes.BOOLEAN),  # S0待机支持
        ("DiskSpinDown", wintypes.BOOLEAN),
    ]
    _pack_ = 1  # 确保1字节对齐

class PowerOptionsWindow(wx.Frame):
    def __init__(self, parent=None):
        style = wx.CAPTION | wx.STAY_ON_TOP | wx.CLOSE_BOX
        super().__init__(parent, title="Windows 登录辅助工具", size=(250, 360), style=style)
        self.parent = parent  # 保存父窗口引用
        self.SetIcon(wx.Icon("Assets/icon.ico"))  # 设置窗口图标
        self.init_ui()
        self.Center()
        DebugLogger.log("[DEBUG] PowerOptionsWindow 初始化完成")
        
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
        btn_back.Bind(wx.EVT_BUTTON, self.on_return)

    # Windows API相关操作
    def _execute_power_action(self, action):
        try:
            if platform.system() != "Windows":
                DebugLogger.log("[ERROR] 操作失败: 仅支持Windows系统")
                wx.MessageBox("[ERROR] 仅支持 Windows 系统!", "错误", wx.OK | wx.ICON_ERROR)
                raise NotImplementedError("[ERROR] 仅支持Windows系统")

            # 获取必要函数
            advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
            user32 = ctypes.WinDLL('user32', use_last_error=True)

            # 提权处理
            class TOKEN_PRIVILEGES(ctypes.Structure):
                _fields_ = [
                    ("PrivilegeCount", wintypes.DWORD),
                    ("Luid", LUID),
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

            luid = LUID()
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
                DebugLogger.log("[DEBUG] 即将执行关机操作")
                ctypes.windll.user32.ExitWindowsEx(0x00000008, 0x00000000)
            elif action == "reboot":
                DebugLogger.log("[DEBUG] 即将执行重启操作")
                ctypes.windll.user32.ExitWindowsEx(0x00000002 | 0x00000004, 0)
            elif action == "sleep":
                DebugLogger.log("[DEBUG] 即将执行睡眠操作")
                ctypes.windll.powrprof.SetSuspendState(False, False, False)
            elif action == "hibernate":
                DebugLogger.log("[DEBUG] 即将执行休眠操作")
                ctypes.windll.powrprof.SetSuspendState(True, False, False)

        except Exception as e:
            DebugLogger.log(f"[ERROR] 操作失败: {str(e)}")
            wx.MessageBox(f"[ERROR] 操作失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
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

    def on_return(self, event):
        if self.parent:
            self.parent.restore_main_window()

        self.Hide()

    def _update_button_state(self):
        try:
            powrprof = ctypes.WinDLL("PowrProf.dll")
            # 设置正确的函数原型
            powrprof.GetPwrCapabilities.argtypes = [ctypes.POINTER(SYSTEM_POWER_CAPABILITIES)]
            powrprof.GetPwrCapabilities.restype = wintypes.BOOL

            power_caps = SYSTEM_POWER_CAPABILITIES()
            # 正确检查返回值
            if not powrprof.GetPwrCapabilities(ctypes.byref(power_caps)):
                raise ctypes.WinError()

            # 检测现代待机(S0)
            powrprof.PowerDeterminePlatformRoleEx.restype = ctypes.c_uint
            platform_role = powrprof.PowerDeterminePlatformRoleEx(0)
            s0_supported = (platform_role == 3) or (power_caps.AoAc == 1)

            # 更新按钮状态
            can_sleep = power_caps.SystemS3 or s0_supported
            can_hibernate = power_caps.SystemS4 and power_caps.HiberFilePresent

            DebugLogger.log(f"[POWER] 电源能力检测结果: S3={can_sleep}, S4={can_hibernate}, S0={s0_supported}")

            self.btn_sleep.Enable(can_sleep)
            self.btn_hibernate.Enable(can_hibernate)

            DebugLogger.log("[DEBUG] 成功更新电源按钮状态")

        except Exception as e:
            DebugLogger.log(f"[ERROR] 更新电源按钮状态失败: {str(e)}")
            # 安全回退：启用按钮并提供提示
            self.btn_sleep.Enable(True)
            self.btn_hibernate.Enable(True)
            wx.MessageBox(f"[ERROR] 更新电源按钮状态失败: {str(e)}\n已启用全部按钮", "警告", wx.OK | wx.ICON_WARNING)
