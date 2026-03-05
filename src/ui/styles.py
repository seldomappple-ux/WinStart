DARK_THEME = """
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Card Styles - Logic moved to PaintEvent for better animation */
QFrame#LaunchCard {
    /* Background handled by painter */
}

QLabel#CardTitle {
    font-size: 18px;
    font-weight: bold;
    color: #FFFFFF;
    background: transparent;
}

QPushButton#MenuButton {
    background-color: transparent;
    border: none;
    border-radius: 15px;
    color: #888888;
    font-size: 16px;
    font-weight: bold;
}
QPushButton#MenuButton:hover {
    background-color: #333333;
    color: #FFFFFF;
}

/* Dialog Styles */
QDialog {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
}

QLineEdit {
    background-color: #2D2D2D;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 8px;
    color: #FFFFFF;
    selection-background-color: #007ACC;
}
QLineEdit:focus {
    border: 1px solid #007ACC;
}

QPushButton {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 6px 12px;
    color: #E0E0E0;
}
QPushButton:hover {
    background-color: #444444;
}
QPushButton:pressed {
    background-color: #222222;
}

QPushButton#PrimaryButton {
    background-color: #007ACC;
    border: 1px solid #007ACC;
    color: white;
}
QPushButton#PrimaryButton:hover {
    background-color: #0063A5;
}

QPushButton#DangerButton {
    background-color: #D32F2F;
    border: 1px solid #D32F2F;
    color: white;
}
QPushButton#DangerButton:hover {
    background-color: #B71C1C;
}

QListWidget {
    background-color: #252526;
    border: 1px solid #333333;
    border-radius: 4px;
    outline: none;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #2D2D2D;
}
QListWidget::item:selected {
    background-color: #37373D;
    color: #FFFFFF;
}
QListWidget::item:hover {
    background-color: #2D2D2D;
}

QScrollBar:vertical {
    border: none;
    background: #2D2D2D;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #555555;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
