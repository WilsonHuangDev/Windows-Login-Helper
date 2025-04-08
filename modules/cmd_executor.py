import subprocess

from modules.debug_window import DebugLogger


class CommandExecutor:
    @classmethod
    def run_as_admin(cls, command: list, encoding: str = "gbk"):
        try:
            DebugLogger.log(f"[DEBUG] 执行命令: {' '.join(command)}")

            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True,
                encoding=encoding
            )

            if result.stdout.strip():
                DebugLogger.log(f"[DEBUG] 命令输出: {result.stdout.strip()}")
            if result.stderr.strip():
                DebugLogger.log(f"命令错误: {result.stderr.strip()}")

            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() or "Unknown error"
            DebugLogger.log(f"命令失败: {error_msg}")
            return False, error_msg
        except Exception as e:
            DebugLogger.log(f"系统错误: {str(e)}")
            return False, str(e)
