import os
import sys
import configparser
import ctypes

from modules.debug_window import DebugLogger


class ConfigManager:
    # 动态配置文件路径
    @staticmethod
    def _get_config_path():
        """根据运行模式返回配置文件路径"""
        # 检测是否为打包后的 EXE
        if getattr(sys, 'frozen', False):
            # EXE 模式：配置文件在软件所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # PY 模式：配置文件在系统盘根目录
            base_dir = os.environ.get('SYSTEMDRIVE', 'C:') + '\\'

        return os.path.join(base_dir, 'passwd_changer_config.ini')

    CONFIG_PATH = _get_config_path.__func__()  # 动态获取路径

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
