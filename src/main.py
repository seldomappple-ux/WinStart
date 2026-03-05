import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import MainWindow

def get_app_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Set high DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WinStart.Launcher")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Use Fusion style as a base for cross-platform consistency
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
