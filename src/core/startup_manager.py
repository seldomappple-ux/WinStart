import os


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_APPROVED_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"


def ensure_startup_option_in_task_manager(executable_path: str, app_name: str = "WinStart") -> bool:
    if os.name != "nt" or not executable_path:
        return False
    try:
        import winreg

        command = f"\"{executable_path}\""
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as run_key:
            try:
                current_command, _ = winreg.QueryValueEx(run_key, app_name)
            except FileNotFoundError:
                current_command = None
            if current_command != command:
                winreg.SetValueEx(run_key, app_name, 0, winreg.REG_SZ, command)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, STARTUP_APPROVED_RUN_KEY) as approved_key:
            try:
                status_data, _ = winreg.QueryValueEx(approved_key, app_name)
            except FileNotFoundError:
                status_data = None
            if status_data is None:
                disabled_data = bytes([3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                winreg.SetValueEx(approved_key, app_name, 0, winreg.REG_BINARY, disabled_data)
        return True
    except OSError:
        return False
