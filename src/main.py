import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.startup_manager import ensure_startup_option_in_task_manager
from src.core.runtime_cleanup import cleanup_stale_pyinstaller_runtime_dirs
from src.ui.main_window import MainWindow

def get_app_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    cleanup_stale_pyinstaller_runtime_dirs()
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WinStart.Launcher")
        if getattr(sys, "frozen", False):
            ensure_startup_option_in_task_manager(os.path.abspath(sys.executable), "WinStart")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    icon_path = os.path.join(get_app_root(), "assets", "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
