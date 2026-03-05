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
    selection-background-color: #2E7D32;
}
QLineEdit:focus {
    border: 1px solid #4CAF50;
    background-color: #333333;
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
    border: 1px solid #555555;
}
QPushButton:pressed {
    background-color: #222222;
}

QPushButton#PrimaryButton {
    background-color: #2E7D32;
    border: 1px solid #2E7D32;
    color: #E8F5E9;
    font-weight: bold;
}
QPushButton#PrimaryButton:hover {
    background-color: #1B5E20;
    border: 1px solid #1B5E20;
}

QPushButton#DangerButton {
    background-color: #5D1010;
    border: 1px solid #5D1010;
    color: #EF9A9A;
}
QPushButton#DangerButton:hover {
    background-color: #7F1515;
    border: 1px solid #7F1515;
    color: #FFCDD2;
}

QListWidget {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    outline: none;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #252526;
    color: #CCCCCC;
}
QListWidget::item:selected {
    background-color: #1B5E20;
    color: #FFFFFF;
    border-left: 3px solid #4CAF50;
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
