import configparser
import datetime
import os
import sys

from modules.config_manager import ConfigManager
from modules.debug_window import DebugLogger


class PasswordGenerator:
    # 动态密钥文件路径
    @staticmethod
    def _get_key_path():
        """根据运行模式返回密钥文件路径"""
        if getattr(sys, 'frozen', False):
            # EXE 模式：密钥文件在软件所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # PY 模式：密钥文件在系统盘根目录
            base_dir = os.environ.get('SYSTEMDRIVE', 'C:') + '\\'

        return os.path.join(base_dir, 'passwd_key_map.ini')

    KEY_FILE = _get_key_path.__func__()  # 动态获取路径

    @classmethod
    def _load_key_map(cls):
        """加载密钥对照表"""
        key_map = {}
        try:
            if not os.path.exists(cls.KEY_FILE):
                cls._create_default_key_file()

            config = configparser.ConfigParser()
            config.read(cls.KEY_FILE)

            if 'Keys' in config:
                for key in config['Keys']:
                    key_map[key] = config['Keys'][key]
            return key_map
        except Exception as e:
            DebugLogger.log(f"密钥表加载失败: {str(e)}")
            ConfigManager._show_error(f"密钥表加载失败: {str(e)}")
            return {}

    @classmethod
    def _create_default_key_file(cls):
        """创建默认密钥表"""
        default_keys = {
            "01": "B1", "02": "D1", "03": "F1", "04": "H1", "05": "J1",
            "06": "L1", "07": "N1", "08": "P1", "09": "R1", "10": "T1",
            "11": "V1", "12": "X1", "13": "Z1", "14": "A1", "15": "C1",
            "16": "E1", "17": "G1", "18": "I1", "19": "K1", "20": "M1",
            "21": "O1", "22": "Q1", "23": "S1", "24": "U1", "25": "W1",
            "26": "Y1", "27": "B2", "28": "D2", "29": "F2", "30": "H2",
            "31": "J2", "32": "L2", "33": "N2", "34": "P2", "35": "R2",
            "36": "T2", "37": "V2", "38": "X2", "39": "Z2", "40": "A2",
            "41": "C2", "42": "E2", "43": "G2", "44": "I2", "45": "K2",
            "46": "M2", "47": "O2", "48": "Q2", "49": "S2", "50": "U2",
            "51": "W2", "52": "Y2", "53": "B3", "54": "D3", "55": "F3",
            "56": "H3", "57": "J3", "58": "L3", "59": "N3", "60": "P3",
            "61": "R3", "62": "T3", "63": "V3", "64": "X3", "65": "Z3",
            "66": "A3", "67": "C3", "68": "E3", "69": "G3", "70": "I3",
            "71": "K3", "72": "M3", "73": "O3", "74": "Q3", "75": "S3",
            "76": "U3", "77": "W3", "78": "Y3", "79": "B4", "80": "D4",
            "81": "F4", "82": "H4", "83": "J4", "84": "L4", "85": "N4",
            "86": "P4", "87": "R4", "88": "T4", "89": "V4", "90": "X4",
            "91": "Z4", "92": "A4", "93": "C4", "94": "E4", "95": "G4",
            "96": "I4", "97": "K4", "98": "M4", "99": "O4", "00": "S4"
        }
        try:
            config = configparser.ConfigParser()
            config['Keys'] = default_keys
            with open(cls.KEY_FILE, 'w') as f:
                config.write(f)
        except Exception as e:
            DebugLogger.log(f"创建密钥表失败: {str(e)}")
            ConfigManager._show_error(f"创建密钥表失败: {str(e)}")

    @classmethod
    def generate_dynamic_password(cls):
        """生成动态口令"""
        # 加载密钥映射表并保存为类属性
        cls.key_map = cls._load_key_map()  # 修复关键行
        try:
            now = datetime.datetime.now()
            time_str = now.strftime("%d%m%Y%H%M")
            offset = 2 if now.time() < datetime.time(12, 30) else 4

            encrypted = []
            for char in time_str:
                original_num = int(char)
                shifted_num = (original_num + offset) % 10
                encrypted.append(f"{shifted_num}")

            encrypted_str = "".join(encrypted)
            password_parts = []
            for i in range(0, len(encrypted_str), 2):
                pair = encrypted_str[i:i + 2].ljust(2, "0")
                password_part = cls.key_map.get(pair, None)  # 使用 cls.key_map
                if not password_part:
                    raise ValueError(f"无效的密钥对: {pair}")
                password_parts.append(password_part)

            raw_password = "".join(password_parts)

            # 分离字母和数字并重新排列
            letters = []
            numbers = []
            for char in raw_password:
                if char.isalpha():
                    letters.append(char)
                elif char.isdigit():
                    numbers.append(char)

            return "".join(letters + numbers)
        except Exception as e:
            raise ValueError(f"生成动态口令失败: {str(e)}")
