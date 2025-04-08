import os
import sys
import configparser
import ctypes

from modules.debug_window import DebugLogger


class ConfigManager:
    @staticmethod
    def _get_dir_path():
        """根据运行模式返回配置文件所在目录"""
        # 检测是否为打包后的 EXE
        if getattr(sys, 'frozen', False):
            # EXE模式：配置文件在软件所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # PY模式：配置文件在系统盘的Windows\WindowsLoginHelper目录
            system_root = os.environ.get('SYSTEMROOT', 'C:\\Windows')
            base_dir = os.path.join(system_root, 'WindowsLoginHelper')
            DebugLogger.log("[DEBUG] 使用内核对象创建目录")
            if not ctypes.windll.kernel32.CreateDirectoryW(base_dir, None):
                error_code = ctypes.windll.kernel32.GetLastError()
                if error_code != 183:  # 忽略已存在错误
                    DebugLogger.log(f"目录创建失败: {str(error_code)}")
                    ctypes.windll.user32.MessageBoxW(0, f"目录创建失败!\n错误代码: {error_code}", "错误", 0x10)
                    sys.exit(1)

        return base_dir

    @staticmethod
    def _get_config_path():
        # 通过_get_dir_path获取基础目录
        config_dir = ConfigManager._get_dir_path()

        # 拼接配置文件名
        config_name = 'passwd_changer_config.ini'
        config_path = os.path.join(config_dir, config_name)  # 合成完整路径
        DebugLogger.log(f"[DEBUG] 配置文件路径: {config_path}")
        return config_path

    DEFAULT_CONFIG = {
        'Auth': {
            'auth_mode': '0',
            'static_password': ''
        },
        'Debug': {
            'debug_mode': '0'
        }
    }

    @classmethod
    def get_config(cls):
        """获取配置信息"""
        config = configparser.ConfigParser()
        if not os.path.exists(cls._get_config_path()):
            DebugLogger.log("[DEBUG] 配置文件不存在")
            cls._create_default_config()

        try:
            config.read(cls._get_config_path())
            config_data = {
                'auth_mode': int(config.get('Auth', 'auth_mode', fallback='0')),
                'static_password': config.get('Auth', 'static_password', fallback=''),
                'debug_mode': int(config.get('Debug', 'debug_mode', fallback='0'))
            }
            DebugLogger.log(f"[DEBUG] 读取的配置信息: {config_data}")
            return config_data
        except Exception as e:
            cls._show_error(f"配置加载失败: {str(e)}")
            return cls._get_default_config()

    @classmethod
    def _create_default_config(cls):
        """创建默认配置文件"""
        try:
            config = configparser.ConfigParser()
            config.read_dict(cls.DEFAULT_CONFIG)
            with open(cls._get_config_path(), 'w') as f:
                config.write(f)
            DebugLogger.log("[DEBUG] 已自动创建默认配置文件")
        except PermissionError:
            cls._show_error("需要管理员权限创建配置文件!")
        except Exception as e:
            cls._show_error(f"创建配置文件失败: {str(e)}")

    @classmethod
    def _get_default_config(cls):
        return {
            'auth_mode': 0,
            'static_password': '',
            'debug_mode': 0
        }

    @classmethod
    def _show_error(cls, message):
        DebugLogger.log(message)
        ctypes.windll.user32.MessageBoxW(0, message, "错误", 0x10)
