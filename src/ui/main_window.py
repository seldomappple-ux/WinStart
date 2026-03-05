from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QMessageBox, QApplication
)
from PySide6.QtCore import Qt

from src.core.config_manager import ConfigManager
from src.core.launcher import Launcher
from src.ui.components import LaunchCard, SlotSettingsDialog
from src.ui.styles import DARK_THEME

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinStart - 一键启动")
        self.resize(1000, 600)
        self.setStyleSheet(DARK_THEME)

        self.config_manager = ConfigManager()
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout: 3 Columns
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(40)
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.refresh_slots()

    def refresh_slots(self):
        # Clear existing
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        slots = self.config_manager.get_slots()
        
        for slot_data in slots:
            card = LaunchCard(slot_data)
            card.launch_requested.connect(self.launch_items)
            card.edit_requested.connect(self.open_settings)
            self.main_layout.addWidget(card)

    def launch_items(self, items):
        if not items:
            return
        Launcher.launch_group(items)

    def open_settings(self, slot_id):
        slots = self.config_manager.get_slots()
        slot_data = next((s for s in slots if s["id"] == slot_id), None)
        if not slot_data: return

        dialog = SlotSettingsDialog(slot_data, self.config_manager, self)
        dialog.exec()
        
        # Refresh UI after dialog closes
        self.refresh_slots()
