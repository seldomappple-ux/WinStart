import os
import shutil
import sys
import time


STALE_RUNTIME_SECONDS = 7 * 24 * 60 * 60


def cleanup_stale_pyinstaller_runtime_dirs() -> None:
    """清理 PyInstaller onefile 异常退出后遗留的旧 _MEI 目录."""
    if not (getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")):
        return

    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        return

    runtime_root = os.path.join(local_appdata, "WinStart", "_runtime")
    current_meipass = os.path.abspath(sys._MEIPASS)

    if not os.path.isdir(runtime_root):
        return

    for name in os.listdir(runtime_root):
        if not name.startswith("_MEI"):
            continue

        path = os.path.abspath(os.path.join(runtime_root, name))
        if path == current_meipass or not os.path.isdir(path):
            continue
        try:
            if time.time() - os.path.getmtime(path) < STALE_RUNTIME_SECONDS:
                continue
        except OSError:
            continue

        try:
            shutil.rmtree(path)
        except OSError:
            # 仍被杀毒软件或索引服务占用时跳过, 下次启动再清理.
            pass
