import os
import configparser
import ctypes
from modules.debug_window import DebugLogger


class ConfigManager:
    CONFIG_PATH = os.path.join(os.environ['WINDIR'], 'passwd_changer_config.ini')
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
        if not os.path.exists(cls.CONFIG_PATH):
            cls._create_default_config()

        try:
            config.read(cls.CONFIG_PATH)
            return {
                'auth_mode': int(config.get('Auth', 'auth_mode', fallback='0')),
                'static_password': config.get('Auth', 'static_password', fallback=''),
                'debug_mode': int(config.get('Debug', 'debug_mode', fallback='0'))
            }
        except Exception as e:
            cls._show_error(f"配置加载失败: {str(e)}")
            return cls._get_default_config()

    @classmethod
    def _create_default_config(cls):
        """创建默认配置文件"""
        try:
            config = configparser.ConfigParser()
            config.read_dict(cls.DEFAULT_CONFIG)
            with open(cls.CONFIG_PATH, 'w') as f:
                config.write(f)
        except PermissionError:
            cls._show_error("需要管理员权限创建配置文件")
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
        ctypes.windll.user32.MessageBoxW(0, message, "配置错误", 0x10)