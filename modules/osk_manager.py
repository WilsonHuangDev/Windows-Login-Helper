import ctypes
import os

from modules.debug_logger import DebugLogger


class OSKManager:
    def has_physical_keyboard(self):
        # 定义常量
        RIM_TYPEKEYBOARD = 1

        user32 = ctypes.windll.user32
        GetRawInputDeviceList = user32.GetRawInputDeviceList
        GetRawInputDeviceList.restype = ctypes.c_uint

        class RAWINPUTDEVICELIST(ctypes.Structure):
            _fields_ = [
                ("hDevice", ctypes.c_void_p),
                ("dwType", ctypes.c_uint)
            ]

        DebugLogger.log("[DEBUG] 正在检测物理键盘")

        # 获取设备数量
        nDevices = ctypes.c_uint(0)
        if GetRawInputDeviceList(None, ctypes.byref(nDevices), ctypes.sizeof(RAWINPUTDEVICELIST)) != 0:
            return False

        if nDevices.value == 0:
            return False

        # 获取设备列表
        dev_list = (RAWINPUTDEVICELIST * nDevices.value)()
        if GetRawInputDeviceList(dev_list, ctypes.byref(nDevices), ctypes.sizeof(RAWINPUTDEVICELIST)) == -1:
            return False

        # 检查是否有键盘
        for dev in dev_list:
            if dev.dwType == RIM_TYPEKEYBOARD:
                return True
        return False

    def show_keyboard_if_needed(self):
        if not self.has_physical_keyboard():
            DebugLogger.log("[DEBUG] 未检测到物理键盘, 正在尝试打开屏幕键盘")
            self._show_touch_keyboard()
        else:
            DebugLogger.log("[DEBUG] 已检测到物理键盘, 无需打开屏幕键盘")

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