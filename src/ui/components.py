import random
import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QFileDialog, QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
    QScrollArea, QGraphicsOpacityEffect, QListWidget, QListWidgetItem, QMenu
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QRect, QRectF, Property, QPointF
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QPainter, QBrush, QPen, QPainterPath, QRadialGradient
from src.ui.icon_loader import IconLoader

class PhysicsIconWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.balls = []
        self.icon_size = 56
        self.active = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_physics)
        self.setMouseTracking(True)
        self.setMinimumHeight(240)
        self.setMinimumWidth(200)

    def sizeHint(self):
        return QSize(200, 240)
        
    def set_items(self, items):
        self.items = items
        self.balls = []
        
        # Initialize balls
        center_x = self.width() / 2 if self.width() > 0 else 150
        center_y = self.height() / 2 if self.height() > 0 else 150
        
        # Calculate static positions (centered row)
        total_width = len(items) * (self.icon_size + 10)
        start_x = center_x - total_width / 2 + self.icon_size / 2
        
        for i, item in enumerate(items):
            # Target static position
            target_x = start_x + i * (self.icon_size + 10)
            
            self.balls.append({
                "x": target_x, "y": center_y, # Start at static pos
                "vx": 0, "vy": 0,
                "target_x": target_x, "target_y": center_y,
                "state": "static",
                "icon": IconLoader.get_pixmap(item.get("path", ""), self.icon_size),
                "trail": [] 
            })
            
        self.update_layout() # Ensure layout is correct
        self.update()

    def resizeEvent(self, event):
        self.update_layout()
        super().resizeEvent(event)

    def update_layout(self):
        # Recalculate static positions based on current size
        if not self.active and self.balls:
            center_x = self.width() / 2
            center_y = self.height() / 2
            
            # Static Grid/Row Layout
            display_count = min(len(self.balls), 3)
            total_width = display_count * (self.icon_size + 10) - 10
            start_x = center_x - total_width / 2 + self.icon_size / 2
            
            for i, ball in enumerate(self.balls):
                if i < display_count:
                    target_x = start_x + i * (self.icon_size + 10)
                    ball["target_x"] = target_x
                    ball["target_y"] = center_y
                    
                    if ball["state"] == "static":
                        ball["x"] = target_x
                        ball["y"] = center_y
                else:
                    ball["target_x"] = center_x
                    ball["target_y"] = center_y
                    if ball["state"] == "static":
                        ball["x"] = center_x
                        ball["y"] = center_y

    def set_active(self, active):
        self.active = active
        if active:
            # Wake up balls
            for ball in self.balls:
                ball["state"] = "falling"
                ball["x"] += random.uniform(-5, 5) 
                ball["vx"] = random.uniform(-1, 1)
                ball["vy"] = random.uniform(2, 5) 
                
            if not self.timer.isActive():
                self.timer.start(16) 
        else:
            self.update_layout()
            for ball in self.balls:
                ball["state"] = "returning"

    def update_physics(self):
        width = self.width()
        height = self.height()
        radius = self.icon_size / 2
        
        all_static = True
        
        for i, ball in enumerate(self.balls):
            if ball["state"] == "static":
                continue
            
            all_static = False
            
            if ball["state"] == "falling" or ball["state"] == "bouncing":
                # Gravity
                ball["vy"] += 0.2 
                
                # Update Position
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]
                
                # Floor Collision
                if ball["y"] + radius > height:
                    ball["y"] = height - radius
                    ball["vy"] *= -0.85
                    ball["state"] = "bouncing"
                    ball["vx"] *= 0.95 # Friction
                    
                # Ceiling Collision
                if ball["y"] - radius < 0:
                    ball["y"] = radius
                    ball["vy"] *= -0.85
                    
                # Wall Collision
                if ball["x"] - radius < 0:
                    ball["x"] = radius
                    ball["vx"] *= -0.85
                elif ball["x"] + radius > width:
                    ball["x"] = width - radius
                    ball["vx"] *= -0.85

            elif ball["state"] == "returning":
                # Lerp to target
                dx = ball["target_x"] - ball["x"]
                dy = ball["target_y"] - ball["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 1 or (i >= 3 and dist < 10): 
                    ball["x"] = ball["target_x"]
                    ball["y"] = ball["target_y"]
                    ball["state"] = "static"
                    ball["vx"] = 0
                    ball["vy"] = 0
                    ball["trail"] = []
                else:
                    ball["x"] += dx * 0.15
                    ball["y"] += dy * 0.15
            
            # Collisions
            if ball["state"] in ["falling", "bouncing"]:
                 for j in range(i + 1, len(self.balls)):
                    other = self.balls[j]
                    dx = other["x"] - ball["x"]
                    dy = other["y"] - ball["y"]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < self.icon_size and dist > 0:
                        overlap = self.icon_size - dist
                        nx = dx / dist
                        ny = dy / dist
                        
                        ball["x"] -= nx * overlap * 0.5
                        ball["y"] -= ny * overlap * 0.5
                        other["x"] += nx * overlap * 0.5
                        other["y"] += ny * overlap * 0.5
                        
                        dvx = ball["vx"] - other["vx"]
                        dvy = ball["vy"] - other["vy"]
                        dot = dvx * nx + dvy * ny
                        
                        if dot > 0:
                            ball["vx"] -= dot * nx
                            ball["vy"] -= dot * ny
                            other["vx"] += dot * nx
                            other["vy"] += dot * ny

            # Trail Logic
            if ball["state"] != "static":
                ball["trail"].insert(0, (ball["x"], ball["y"], 1.0))
                if len(ball["trail"]) > 15: 
                    ball["trail"].pop()
                
                for k in range(len(ball["trail"])):
                    x, y, a = ball["trail"][k]
                    ball["trail"][k] = (x, y, a * 0.85)

        if all_static and not self.active:
            self.timer.stop()
            
        self.update()

    def paintEvent(self, event):
        if not self.items:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw Trails
        if self.active:
            for ball in self.balls:
                for i, (x, y, alpha) in enumerate(ball["trail"]):
                    if alpha < 0.05: continue
                    
                    radius = (self.icon_size / 2) * (1.0 - i/15.0) * 0.7
                    if radius < 1: radius = 1
                    
                    color = QColor("#69F0AE") 
                    color.setAlphaF(alpha * 0.4)
                    
                    painter.setBrush(QBrush(color))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(x, y), radius, radius)

        # Draw Icons
        for i, ball in enumerate(self.balls):
            if not self.active and i >= 3: continue 
            
            pixmap = ball["icon"]
            x = ball["x"] - self.icon_size / 2
            y = ball["y"] - self.icon_size / 2
            painter.drawPixmap(int(x), int(y), pixmap)

class ThreeDotsButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setCursor(Qt.PointingHandCursor)
        self._hover_factor = 0.0
        self.force_active = False # Flag to keep button lit
        
        self.anim = QPropertyAnimation(self, b"hover_factor")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def get_hover_factor(self): return self._hover_factor
    def set_hover_factor(self, f): self._hover_factor = f; self.update()
    hover_factor = Property(float, get_hover_factor, set_hover_factor)
    
    def set_active(self, active):
        self.force_active = active
        if active:
            self.anim.stop()
            self._hover_factor = 1.0
            self.update()
        else:
            inside = self.rect().contains(self.mapFromGlobal(QCursor.pos()))
            self.anim.setStartValue(self._hover_factor)
            self.anim.setEndValue(1.0 if inside else 0.0)
            self.anim.start()

    def enterEvent(self, event):
        if not self.force_active:
            self.anim.setStartValue(self._hover_factor)
            self.anim.setEndValue(1.0)
            self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.force_active:
            self.anim.setStartValue(self._hover_factor)
            self.anim.setEndValue(0.0)
            self.anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center of button
        cx, cy = self.width() / 2, self.height() / 2
        
        # Dot configuration
        dot_radius = 2.0
        spacing = 6.0
        
        # Draw 3 dots
        positions = [(cx - spacing, cy), (cx, cy), (cx + spacing, cy)]
        
        for px, py in positions:
            # Base dot color
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#888888"))
            painter.drawEllipse(QPointF(px, py), dot_radius, dot_radius)
            
            # Glow effect on hover
            if self._hover_factor > 0.01:
                glow_radius = dot_radius + (4.0 * self._hover_factor)
                
                gradient = QRadialGradient(px, py, glow_radius)
                c1 = QColor("#69F0AE")
                c1.setAlphaF(0.8 * self._hover_factor)
                c2 = QColor("#69F0AE")
                c2.setAlphaF(0.0)
                
                gradient.setColorAt(0, c1)
                gradient.setColorAt(1, c2)
                
                painter.setBrush(QBrush(gradient))
                painter.drawEllipse(QPointF(px, py), glow_radius, glow_radius)
                
                # Highlight center dot
                painter.setBrush(QColor("#FFFFFF"))
                painter.setOpacity(self._hover_factor)
                painter.drawEllipse(QPointF(px, py), dot_radius, dot_radius)
                painter.setOpacity(1.0)

class LaunchCard(QFrame):
    launch_requested = Signal(list) # Emits list of items to launch
    edit_requested = Signal(str)    # Emits slot_id

    def __init__(self, slot_data, parent=None):
        super().__init__(parent)
        self.slot_data = slot_data
        self.setObjectName("LaunchCard")
        self.setFixedSize(300, 400)
        self.setCursor(Qt.PointingHandCursor)
        
        # Custom Painting Attributes
        self._bg_color = QColor("#1E1E1E")
        self._border_color = QColor("#333333")
        self._scale_factor = 1.0
        self._pulse_factor = 0.0
        self.hovering = False
        self.is_launching = False
        self.menu_active = False  # Flag to keep animation running when menu is open
        
        # Data
        self.items = slot_data.get("items", [])
        self.slot_id = slot_data.get("id")
        self.slot_name = slot_data.get("name", "未命名")

        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header (Title + Menu)
        header_layout = QHBoxLayout()
        self.title_label = QLabel(self.slot_name)
        self.title_label.setObjectName("CardTitle")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.menu_btn = ThreeDotsButton()
        self.menu_btn.clicked.connect(self.show_menu)
        header_layout.addWidget(self.menu_btn)
        
        self.layout.addLayout(header_layout)

        # Content Area (Physics Icons)
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setAlignment(Qt.AlignCenter)
        
        self.icon_widget = PhysicsIconWidget()
        self.content_layout.addWidget(self.icon_widget)
        
        # Empty State (Removed as requested)
        # self.empty_label = QLabel("空")
        # self.empty_label.setStyleSheet("font-size: 40px; color: #333333; font-weight: bold; background: transparent;")
        # self.empty_label.setAlignment(Qt.AlignCenter)
        # self.empty_label.setVisible(False)
        # self.content_layout.addWidget(self.empty_label)

        self.layout.addWidget(self.content_area, stretch=1)
        
        self.refresh_icons()
        
        # Status Label (Removed as requested)
        # self.status_label = QLabel("一键启动")
        # self.status_label.setAlignment(Qt.AlignCenter)
        # self.status_label.setStyleSheet("color: #888888; font-size: 12px; background: transparent;")
        # self.layout.addWidget(self.status_label)

    def refresh_icons(self):
        if not self.items:
            self.icon_widget.setVisible(False)
            # self.empty_label.setVisible(True) # Removed
        else:
            self.icon_widget.setVisible(True)
            # self.empty_label.setVisible(False) # Removed
            self.icon_widget.set_items(self.items)

    def setup_animations(self):
        # Background Color Animation
        self.bg_anim = QPropertyAnimation(self, b"bg_color")
        self.bg_anim.setDuration(300)
        self.bg_anim.setEasingCurve(QEasingCurve.InOutQuad)

        # Scale Animation
        self.scale_anim = QPropertyAnimation(self, b"scale_factor")
        self.scale_anim.setDuration(150)
        self.scale_anim.setEasingCurve(QEasingCurve.OutQuad)

        self.pulse_anim = QPropertyAnimation(self, b"pulse_factor")
        self.pulse_anim.setDuration(1500)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.setStartValue(0.0)
        self.pulse_anim.setEndValue(1.0)
        self.pulse_anim.setEasingCurve(QEasingCurve.InOutSine)

    # Property for Animation
    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, color):
        self._bg_color = color
        self.update()

    bg_color = Property(QColor, get_bg_color, set_bg_color)

    def get_scale_factor(self):
        return self._scale_factor

    def set_scale_factor(self, factor):
        self._scale_factor = factor
        self.update()

    scale_factor = Property(float, get_scale_factor, set_scale_factor)

    def get_pulse_factor(self):
        return self._pulse_factor

    def set_pulse_factor(self, factor):
        self._pulse_factor = factor
        self.update()

    pulse_factor = Property(float, get_pulse_factor, set_pulse_factor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-self.width() / 2, -self.height() / 2)

        path = QPainterPath()
        path.addRoundedRect(QRectF(1, 1, self.width()-2, self.height()-2), 12, 12)
        
        # Base Background
        painter.fillPath(path, self._bg_color)
        
        # Pulse Effect (Ripple Expanding from Center)
        if self.hovering and not self.is_launching:
            # Advanced Gradient Green Style (Edge Deep, Center Light, Translucent)
            
            # 1. Base Gradient (Simulating glass/light effect)
            # Center is lighter/brighter, edges are deeper
            base_gradient = QRadialGradient(self.width()/2, self.height()/2, self.width()*0.8)
            
            # Colors
            c_center = QColor("#4CAF50") # Base Green
            c_center.setAlpha(40)       # Light transparency
            
            c_edge = QColor("#1B5E20")   # Deep Green
            c_edge.setAlpha(180)        # More opaque at edges
            
            base_gradient.setColorAt(0, c_center)
            base_gradient.setColorAt(1, c_edge)
            
            painter.fillPath(path, QBrush(base_gradient))
            
            # 2. Dynamic Pulse Glow (Breathing from center)
            pulse_val = 0.5 + 0.5 * math.sin(self._pulse_factor * 6.28) # 0 to 1
            
            # Radius expands slightly with pulse
            glow_radius = self.width() * 0.6 + pulse_val * 40
            
            glow_gradient = QRadialGradient(self.width()/2, self.height()/2, glow_radius)
            c_glow = QColor("#69F0AE")   # Bright Neon Green
            c_glow.setAlpha(int(60 * pulse_val)) # Breathing alpha
            c_fade = QColor("#69F0AE")
            c_fade.setAlpha(0)
            
            glow_gradient.setColorAt(0, c_glow)
            glow_gradient.setColorAt(1, c_fade)
            
            painter.fillPath(path, QBrush(glow_gradient))
            
            # 3. Enhanced Border (Neon Green, breathing thickness/alpha)
            border_alpha = int(180 + 75 * pulse_val)
            border_color = QColor("#69F0AE")
            border_color.setAlpha(border_alpha)
            
            border_width = 1.5 + 1.0 * pulse_val
            border_pen = QPen(border_color, border_width)
            painter.setPen(border_pen)
            painter.drawPath(path)
            return # Skip default border drawing

        pen = QPen(self._border_color, 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

    def enterEvent(self, event):
        if not self.is_launching:
            self.hovering = True
            # Only start if not already running to avoid glitchy restarts
            if self.pulse_anim.state() != QPropertyAnimation.Running:
                self.pulse_anim.start()
            self.update()
            self.icon_widget.set_active(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_launching and not self.menu_active:
            self.hovering = False
            self.pulse_anim.stop()
            self.update()
            self.icon_widget.set_active(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.menu_btn.geometry().contains(event.pos()):
                super().mousePressEvent(event)
                return
            
            # Press Animation
            self.scale_anim.setStartValue(self._scale_factor)
            self.scale_anim.setEndValue(0.98)
            self.scale_anim.start()
            
            self.trigger_launch()

    def mouseReleaseEvent(self, event):
        # Release Animation
        self.scale_anim.setStartValue(self._scale_factor)
        self.scale_anim.setEndValue(1.0)
        self.scale_anim.start()
        super().mouseReleaseEvent(event)
    
    def trigger_launch(self):
        if not self.items:
            return

        self.hovering = False
        self.is_launching = True
        self.pulse_anim.stop()

        # Animate Color to Green
        self.bg_anim.stop()
        self.bg_anim.setStartValue(self._bg_color)
        self.bg_anim.setEndValue(QColor("#1B5E20"))
        self.bg_anim.start()
        
        self._border_color = QColor("#4CAF50")
        
        # self.status_label.setText("正在启动...")
        # self.status_label.setStyleSheet("color: #4CAF50; background: transparent;")
        
        # Launch
        self.launch_requested.emit(self.items)

        # Reset after delay
        QTimer.singleShot(1500, self.reset_style)

    def reset_style(self):
        self.is_launching = False

        # Animate back to original
        self.bg_anim.stop()
        self.bg_anim.setStartValue(self._bg_color)
        self.bg_anim.setEndValue(QColor("#1E1E1E"))
        self.bg_anim.start()

        self._border_color = QColor("#333333")
        
        # self.status_label.setText("一键启动")
        # self.status_label.setStyleSheet("color: #888888; background: transparent;")

    def show_menu(self):
        self.menu_active = True
        self.menu_btn.set_active(True) # Keep button lit
        
        menu = QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        
        # Enhanced Menu Styling with Gradient Green
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 30px;
                border-radius: 4px;
                font-size: 14px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                /* Transparent Texture: Edge Light Green (Low Alpha), Center Transparent/Dark */
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(105, 240, 174, 30), 
                    stop:0.2 rgba(0, 0, 0, 0), 
                    stop:0.8 rgba(0, 0, 0, 0), 
                    stop:1 rgba(105, 240, 174, 30));
                color: #FFFFFF;
                border: 1px solid rgba(105, 240, 174, 80); /* Soft Neon Border */
            }
            QMenu::separator {
                height: 1px;
                background: #333333;
                margin: 4px 10px;
            }
        """)
        
        edit_action = menu.addAction("编辑配置")
        rename_action = menu.addAction("重命名卡槽")
        
        # Position menu elegantly
        pos = self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height() + 8))
        
        action = menu.exec(pos)
        
        self.menu_active = False
        self.menu_btn.set_active(False)

        if not self.is_launching:
            inside = self.rect().contains(self.mapFromGlobal(QCursor.pos()))
            self.hovering = inside
            if inside:
                self.pulse_anim.start()
                self.icon_widget.set_active(True)
            else:
                self.pulse_anim.stop()
                self.icon_widget.set_active(False)
            self.update()
        
        if action == edit_action:
            self.edit_requested.emit(self.slot_id)
        elif action == rename_action:
            self.rename_slot()

    def rename_slot(self):
        # Simple input dialog
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "重命名", "请输入新的卡槽名称:", text=self.slot_name)
        if ok and new_name:
            self.slot_name = new_name
            self.title_label.setText(new_name)
            # Update data structure
            self.slot_data["name"] = new_name
            # Emit edit requested to force save in main window context (or we need a better signal)
            # Since we don't have direct access to config manager here easily without passing it,
            # We will rely on the fact that slot_data is a reference to the dict in ConfigManager's list (in Python it usually is)
            # So we just need to trigger a save.
            # But ConfigManager needs to be told to save.
            # Let's emit a special signal or just reuse edit_requested with a flag, but for now 
            # let's just accept the UI update and assume user will open settings eventually or we rely on parent to save.
            # Correct way: emit signal
            self.edit_requested.emit(self.slot_id) # This opens the dialog, which is a bit annoying for just rename.
            # Ideally we should have a signal rename_requested(str, str)
            
    def update_data(self, slot_data):
        self.slot_data = slot_data
        self.items = slot_data.get("items", [])
        self.slot_name = slot_data.get("name", "未命名")
        self.title_label.setText(self.slot_name)
        self.refresh_icons()


class ItemEditorDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.item_data = item_data or {}
        self.setWindowTitle("编辑启动项" if item_data else "添加启动项")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.name_input = QLineEdit(self.item_data.get("name", ""))
        self.name_input.setPlaceholderText("例如：Photoshop")
        
        self.path_input = QLineEdit(self.item_data.get("path", ""))
        self.path_input.setPlaceholderText("选择程序路径 (.exe)")
        self.path_btn = QPushButton("浏览...")
        self.path_btn.clicked.connect(self.browse_file)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_btn)

        self.args_input = QLineEdit(self.item_data.get("args", ""))
        self.args_input.setPlaceholderText("启动参数 (可选)")
        
        self.delay_input = QLineEdit(str(self.item_data.get("delay", 0)))
        self.delay_input.setPlaceholderText("延迟秒数 (0为立即启动)")
        
        layout.addRow("名称:", self.name_input)
        layout.addRow("路径:", path_layout)
        layout.addRow("参数:", self.args_input)
        layout.addRow("延迟 (秒):", self.delay_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择程序", "", "可执行文件 (*.exe);;所有文件 (*.*)")
        if file_path:
            self.path_input.setText(file_path)
            if not self.name_input.text():
                import os
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_input.setText(name)

    def get_data(self):
        try:
            delay = int(self.delay_input.text())
        except ValueError:
            delay = 0
            
        return {
            "name": self.name_input.text(),
            "path": self.path_input.text(),
            "args": self.args_input.text(),
            "delay": delay
        }

class SlotSettingsDialog(QDialog):
    def __init__(self, slot_data, config_manager, parent=None):
        super().__init__(parent)
        self.slot_data = slot_data
        self.config_manager = config_manager
        self.setWindowTitle(f"配置 - {slot_data.get('name')}")
        self.setFixedSize(500, 600)
        self.setup_ui()
        self.load_items()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel(f"配置 - {self.slot_data.get('name')}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; margin-bottom: 10px;")
        layout.addWidget(title)

        # Rename Slot Section
        name_container = QWidget()
        name_container.setStyleSheet("background-color: #252526; border-radius: 6px;")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(15, 15, 15, 15)
        
        name_label = QLabel("卡槽名称")
        name_label.setStyleSheet("color: #AAAAAA; font-weight: bold;")
        
        self.name_edit = QLineEdit(self.slot_data.get("name"))
        self.name_edit.setPlaceholderText("输入名称...")
        self.name_edit.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px; border-bottom: 1px solid #444444; border-radius: 0px;")
        
        save_name_btn = QPushButton("保存")
        save_name_btn.setFixedWidth(60)
        save_name_btn.setStyleSheet("""
            QPushButton { background: #333333; border: none; color: #CCCCCC; }
            QPushButton:hover { background: #444444; color: white; }
        """)
        save_name_btn.clicked.connect(self.save_name)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(save_name_btn)
        layout.addWidget(name_container)

        # List Section
        list_label = QLabel("启动项列表")
        list_label.setStyleSheet("color: #888888; font-size: 13px; margin-top: 10px;")
        layout.addWidget(list_label)

        # List
        self.item_list = QListWidget()
        self.item_list.setDragDropMode(QListWidget.InternalMove) # Enable Drag & Drop
        layout.addWidget(self.item_list)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        add_btn = QPushButton("添加程序")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setFixedHeight(36)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_item)
        
        edit_btn = QPushButton("编辑")
        edit_btn.setFixedHeight(36)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self.edit_item)
        
        del_btn = QPushButton("删除")
        del_btn.setObjectName("DangerButton")
        del_btn.setFixedHeight(36)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(self.delete_item)

        btn_layout.addWidget(add_btn, 2)
        btn_layout.addWidget(edit_btn, 1)
        btn_layout.addWidget(del_btn, 1)
        layout.addLayout(btn_layout)

        # Hint
        hint = QLabel("提示: 可拖拽列表项进行排序")
        hint.setStyleSheet("color: #555555; font-size: 12px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

    def load_items(self):
        self.item_list.clear()
        for item in self.slot_data.get("items", []):
            widget_item = QListWidgetItem(item["name"])
            widget_item.setData(Qt.UserRole, item["id"])
            icon = IconLoader.get_icon(item["path"])
            widget_item.setIcon(icon)
            self.item_list.addItem(widget_item)

    def save_name(self):
        new_name = self.name_edit.text()
        if new_name:
            self.config_manager.update_slot_name(self.slot_data["id"], new_name)
            self.slot_data["name"] = new_name # Update local ref

    def add_item(self):
        dialog = ItemEditorDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["name"] and data["path"]:
                self.config_manager.add_item(
                    self.slot_data["id"],
                    data["name"],
                    data["path"],
                    data["args"],
                    data["delay"]
                )
                self.refresh_data()

    def edit_item(self):
        current = self.item_list.currentItem()
        if not current: return
        
        item_id = current.data(Qt.UserRole)
        item = next((i for i in self.slot_data["items"] if i["id"] == item_id), None)
        
        if item:
            dialog = ItemEditorDialog(self, item)
            if dialog.exec():
                data = dialog.get_data()
                if data["name"] and data["path"]:
                    self.config_manager.update_item(
                        self.slot_data["id"],
                        item_id,
                        data["name"],
                        data["path"],
                        data["args"],
                        data["delay"]
                    )
                    self.refresh_data()

    def delete_item(self):
        current = self.item_list.currentItem()
        if not current: return
        
        item_id = current.data(Qt.UserRole)
        self.config_manager.delete_item(self.slot_data["id"], item_id)
        self.refresh_data()

    def refresh_data(self):
        # Reload from config manager
        slots = self.config_manager.get_slots()
        self.slot_data = next((s for s in slots if s["id"] == self.slot_data["id"]), self.slot_data)
        self.load_items()
    
    def closeEvent(self, event):
        # Save order on close
        new_order = []
        for i in range(self.item_list.count()):
            item = self.item_list.item(i)
            new_order.append(item.data(Qt.UserRole))
        
        self.config_manager.reorder_items(self.slot_data["id"], new_order)
        super().closeEvent(event)
