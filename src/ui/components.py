import random
import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QFileDialog, QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
    QScrollArea, QGraphicsOpacityEffect, QListWidget, QListWidgetItem, QMenu,
    QCheckBox, QWidgetAction
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QRect, QRectF, Property, QPointF
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QPainter, QBrush, QPen, QPainterPath, QRadialGradient
from src.ui.icon_loader import IconLoader
from PySide6.QtGui import QPixmap, QImage

_grayscale_cache: dict = {}

def _make_grayscale_pixmap(pixmap: QPixmap) -> QPixmap:
    key = pixmap.cacheKey()
    if key in _grayscale_cache:
        return _grayscale_cache[key]
    image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
    for y in range(image.height()):
        for x in range(image.width()):
            c = image.pixel(x, y)
            alpha = (c >> 24) & 0xFF
            r = (c >> 16) & 0xFF
            g = (c >> 8) & 0xFF
            b = c & 0xFF
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            dimmed = int(gray * 0.45)
            image.setPixel(x, y, (alpha << 24) | (dimmed << 16) | (dimmed << 8) | dimmed)
    result = QPixmap.fromImage(image)
    _grayscale_cache[key] = result
    return result


class ToggleMenuRow(QWidget):
    toggled = Signal(str, bool)

    def __init__(self, item, icon_pixmap=None, parent=None):
        super().__init__(parent)
        self.item_id = item["id"]
        self.setObjectName("ToggleMenuRow")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(icon_pixmap or IconLoader.get_pixmap(item.get("path", ""), 20))
        icon_label.setFixedSize(20, 20)
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        self.name_label = QLabel(item["name"])
        self.name_label.setStyleSheet(
            "color: #E0E0E0; background: transparent;" if item.get("enabled", True) else "color: #8A8A8A; background: transparent;"
        )
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.name_label)

        self.toggle = QCheckBox()
        self.toggle.setChecked(item.get("enabled", True))
        self.toggle.setCursor(Qt.PointingHandCursor)
        self.toggle.setStyleSheet("""
            QCheckBox {
                spacing: 0px;
            }
            QCheckBox::indicator {
                width: 38px;
                height: 22px;
                border-radius: 11px;
                background-color: #3A3A3A;
                border: 1px solid #4A4A4A;
            }
            QCheckBox::indicator:checked {
                background-color: #1F7A45;
                border: 1px solid #4CAF50;
            }
        """)
        self.toggle.toggled.connect(self._on_toggled)
        layout.addWidget(self.toggle)

        # The knob is drawn as a lightweight overlay instead of relying on platform style.
        self.knob = QFrame(self)
        self.knob.setFixedSize(16, 16)
        self.knob.setStyleSheet("background-color: #F5F5F5; border-radius: 8px;")
        self.knob.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._update_knob()

    def resizeEvent(self, event):
        self._update_knob()
        super().resizeEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.childAt(event.pos()) is not self.toggle:
            self.toggle.toggle()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _update_knob(self):
        indicator = self.toggle.geometry()
        if indicator.isNull():
            return
        x = indicator.x() + (19 if self.toggle.isChecked() else 3)
        y = indicator.y() + 3
        self.knob.move(x, y)

    def _on_toggled(self, checked):
        self.name_label.setStyleSheet("color: #E0E0E0; background: transparent;" if checked else "color: #8A8A8A; background: transparent;")
        self._update_knob()
        self.toggled.emit(self.item_id, checked)

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
            target_x = start_x + i * (self.icon_size + 10)
            enabled = item.get("enabled", True)
            pixmap = IconLoader.get_pixmap(item.get("path", ""), self.icon_size)
            self.balls.append({
                "x": target_x, "y": center_y,
                "vx": 0, "vy": 0,
                "target_x": target_x, "target_y": center_y,
                "state": "static",
                "icon": pixmap if enabled else _make_grayscale_pixmap(pixmap),
                "enabled": enabled,
                "trail": []
            })
            
        self.update_layout()
        self.update()

    def update_item_enabled(self, item_id: str, enabled: bool):
        for i, item in enumerate(self.items):
            if item["id"] == item_id:
                item["enabled"] = enabled
                pixmap = IconLoader.get_pixmap(item.get("path", ""), self.icon_size)
                self.balls[i]["icon"] = pixmap if enabled else _make_grayscale_pixmap(pixmap)
                self.balls[i]["enabled"] = enabled
                self.update()
                return

    def resizeEvent(self, event):
        self.update_layout()
        super().resizeEvent(event)

    def update_layout(self):
        # Recalculate static positions based on current size
        if not self.active and self.balls:
            center_x = self.width() / 2
            center_y = self.height() / 2
            
            # Static Grid Layout (Auto-flow, max 3 per row for balance)
            count = len(self.balls)
            cols = 3
            rows = (count + cols - 1) // cols
            
            # Total height of the grid
            total_height = rows * (self.icon_size + 10) - 10
            start_y = center_y - total_height / 2 + self.icon_size / 2
            
            for i, ball in enumerate(self.balls):
                row = i // cols
                col = i % cols
                
                # Items in current row
                items_in_row = min(cols, count - row * cols)
                
                # Row width
                row_width = items_in_row * (self.icon_size + 10) - 10
                start_x = center_x - row_width / 2 + self.icon_size / 2
                
                target_x = start_x + col * (self.icon_size + 10)
                target_y = start_y + row * (self.icon_size + 10)
                
                ball["target_x"] = target_x
                ball["target_y"] = target_y
                
                if ball["state"] == "static":
                    ball["x"] = target_x
                    ball["y"] = target_y

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
                
                if dist < 1: 
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
            if ball["state"] != "static" and ball.get("enabled", True):
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

        # Draw Trails (only enabled balls)
        if self.active:
            for ball in self.balls:
                if not ball.get("enabled", True):
                    continue
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
            pixmap = ball["icon"]
            x = ball["x"] - pixmap.width() / 2
            y = ball["y"] - pixmap.height() / 2
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
    launch_requested = Signal(list)
    edit_requested = Signal(str)
    toggle_item_requested = Signal(str, str, bool)  # slot_id, item_id, enabled

    def __init__(self, slot_data, parent=None, defer_load=False):
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
        self.menu_icon_cache = {}
        self.icons_loaded = False
        
        # Data
        self.items = slot_data.get("items", [])
        self.slot_id = slot_data.get("id")
        self.slot_name = slot_data.get("name", "未命名")
        self.defer_load = defer_load

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

        self.placeholder_label = QLabel("加载中...")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet(
            "color: #666666; font-size: 16px; background: transparent;"
        )
        self.content_layout.addWidget(self.placeholder_label)
        
        self.icon_widget = PhysicsIconWidget()
        self.content_layout.addWidget(self.icon_widget)
        
        # Empty State (Removed as requested)
        # self.empty_label = QLabel("空")
        # self.empty_label.setStyleSheet("font-size: 40px; color: #333333; font-weight: bold; background: transparent;")
        # self.empty_label.setAlignment(Qt.AlignCenter)
        # self.empty_label.setVisible(False)
        # self.content_layout.addWidget(self.empty_label)

        self.layout.addWidget(self.content_area, stretch=1)

        if self.defer_load:
            self.set_loading_state(True)
        else:
            self.load_card_content()
        
        # Status Label (Removed as requested)
        # self.status_label = QLabel("一键启动")
        # self.status_label.setAlignment(Qt.AlignCenter)
        # self.status_label.setStyleSheet("color: #888888; font-size: 12px; background: transparent;")
        # self.layout.addWidget(self.status_label)

    def set_loading_state(self, loading):
        if loading:
            self.placeholder_label.setVisible(bool(self.items))
            self.icon_widget.setVisible(False)
            return

        self.placeholder_label.setVisible(False)
        self.icon_widget.setVisible(bool(self.items))

    def load_card_content(self):
        if self.icons_loaded:
            return

        self.menu_icon_cache = {}
        if not self.items:
            self.icons_loaded = True
            self.set_loading_state(False)
        else:
            self.icon_widget.set_items(self.items)
            for item in self.items:
                path = item.get("path", "")
                if path not in self.menu_icon_cache:
                    base_pixmap = IconLoader.get_pixmap(path, self.icon_widget.icon_size)
                    self.menu_icon_cache[path] = base_pixmap.scaled(
                        20,
                        20,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
            self.icons_loaded = True
            self.set_loading_state(False)

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
            if self.icons_loaded:
                self.icon_widget.set_active(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_launching and not self.menu_active:
            self.hovering = False
            self.pulse_anim.stop()
            self.update()
            if self.icons_loaded:
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
        if not self.icons_loaded:
            self.load_card_content()

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
            QWidget#ToggleMenuRow {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
            }
            QWidget#ToggleMenuRow:hover {
                background-color: rgba(105, 240, 174, 24);
                border: 1px solid rgba(105, 240, 174, 60);
            }
        """)
        
        edit_action = menu.addAction("编辑配置")
        menu.addSeparator()
        section_action = menu.addAction("软件开关")
        section_action.setEnabled(False)
        if self.items:
            for item in self.items:
                row_action = QWidgetAction(menu)
                row_widget = ToggleMenuRow(
                    item,
                    self.menu_icon_cache.get(item.get("path", "")),
                    menu,
                )
                row_widget.toggled.connect(self.handle_toggle_item)
                row_action.setDefaultWidget(row_widget)
                menu.addAction(row_action)
        else:
            no_item = menu.addAction("（暂无启动项）")
            no_item.setEnabled(False)

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

    def handle_toggle_item(self, item_id, enabled):
        for item in self.items:
            if item["id"] == item_id:
                item["enabled"] = enabled
                break
        self.toggle_item_requested.emit(self.slot_id, item_id, enabled)
        if self.icons_loaded:
            self.icon_widget.update_item_enabled(item_id, enabled)

    def update_data(self, slot_data):
        self.slot_data = slot_data
        self.items = slot_data.get("items", [])
        self.slot_name = slot_data.get("name", "未命名")
        self.title_label.setText(self.slot_name)
        self.icons_loaded = False
        if self.defer_load:
            self.set_loading_state(True)
        else:
            self.load_card_content()


class ItemEditorDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.item_data = item_data or {}
        self.setWindowTitle("编辑启动项" if item_data else "添加启动项")
        self.setMinimumWidth(450)
        parent_icon = parent.windowIcon() if parent else QIcon()
        if not parent_icon.isNull():
            self.setWindowIcon(parent_icon)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Helper for custom label with green indicator
        def create_label(text):
            container = QWidget()
            container.setAttribute(Qt.WA_TranslucentBackground) # Ensure transparency
            container.setStyleSheet("background: transparent;") # Double ensure
            l = QHBoxLayout(container)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(10)
            
            # Green rounded rectangular line (Vertical Pill)
            indicator = QFrame()
            indicator.setFixedSize(4, 16)
            indicator.setStyleSheet("background-color: #4CAF50; border-radius: 2px;")
            
            # Text label
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #E0E0E0; font-size: 14px; background: transparent; border: none;")
            
            l.addWidget(indicator)
            l.addWidget(lbl)
            # l.addStretch() # No stretch needed for FormLayout label role
            return container

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
        
        # Use custom labels
        layout.addRow(create_label("名称:"), self.name_input)
        layout.addRow(create_label("路径:"), path_layout)
        layout.addRow(create_label("参数:"), self.args_input)
        layout.addRow(create_label("延迟 (秒):"), self.delay_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        layout.addRow(self.buttons)

        # OK Button Logic
        self.ok_btn = self.buttons.button(QDialogButtonBox.Ok)
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.update_ok_button() # Set initial state
        
        self.path_input.textChanged.connect(self.update_ok_button)

    def update_ok_button(self):
        path = self.path_input.text().strip()
        if path:
            self.ok_btn.setEnabled(True)
            self.ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2E7D32;
                    border: 1px solid #2E7D32;
                    color: #FFFFFF;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
                QPushButton:pressed {
                    background-color: #1B5E20;
                }
            """)
        else:
            self.ok_btn.setEnabled(False)
            self.ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    border: 1px solid #444444;
                    color: #888888;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
            """)

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
        parent_icon = parent.windowIcon() if parent else QIcon()
        if not parent_icon.isNull():
            self.setWindowIcon(parent_icon)
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
        
        # Add Button Style (Green Gradient)
        self.add_btn = QPushButton("添加程序")
        self.add_btn.setFixedHeight(36)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(105, 240, 174, 30), 
                    stop:0.2 rgba(0, 0, 0, 0), 
                    stop:0.8 rgba(0, 0, 0, 0), 
                    stop:1 rgba(105, 240, 174, 30));
                border: 1px solid rgba(105, 240, 174, 80);
                border-radius: 6px;
                color: #E0E0E0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(105, 240, 174, 60), 
                    stop:0.2 rgba(0, 0, 0, 0), 
                    stop:0.8 rgba(0, 0, 0, 0), 
                    stop:1 rgba(105, 240, 174, 60));
                border: 1px solid #69F0AE;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: rgba(46, 125, 50, 100);
            }
            QPushButton:disabled {
                border: 1px solid #333333;
                color: #555555;
                background-color: transparent;
            }
        """)
        self.add_btn.clicked.connect(self.add_item)
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setFixedHeight(36)
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(self.edit_item)
        
        # Delete Button Style (Red Gradient - Low Saturation)
        self.del_btn = QPushButton("删除")
        self.del_btn.setFixedHeight(36)
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(229, 115, 115, 30), 
                    stop:0.2 rgba(0, 0, 0, 0), 
                    stop:0.8 rgba(0, 0, 0, 0), 
                    stop:1 rgba(229, 115, 115, 30));
                border: 1px solid rgba(229, 115, 115, 80);
                border-radius: 6px;
                color: #E0E0E0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(229, 115, 115, 60), 
                    stop:0.2 rgba(0, 0, 0, 0), 
                    stop:0.8 rgba(0, 0, 0, 0), 
                    stop:1 rgba(229, 115, 115, 60));
                border: 1px solid #FFCDD2;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: rgba(183, 28, 28, 80);
            }
            QPushButton:disabled {
                border: 1px solid #333333;
                color: #555555;
                background-color: transparent;
            }
        """)
        self.del_btn.clicked.connect(self.delete_item)

        btn_layout.addWidget(self.add_btn, 2)
        btn_layout.addWidget(self.edit_btn, 1)
        btn_layout.addWidget(self.del_btn, 1)
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
            widget_item.setFlags(widget_item.flags() | Qt.ItemIsUserCheckable)
            widget_item.setCheckState(Qt.Checked if item.get("enabled", True) else Qt.Unchecked)
            icon = IconLoader.get_icon(item["path"])
            widget_item.setIcon(icon)
            self.item_list.addItem(widget_item)

    def save_name(self):
        new_name = self.name_edit.text()
        if new_name:
            self.config_manager.update_slot_name(self.slot_data["id"], new_name)
            self.slot_data["name"] = new_name # Update local ref

    def add_item(self):
        # Disable buttons
        self.add_btn.setEnabled(False)
        self.del_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        
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
        
        # Enable buttons
        self.add_btn.setEnabled(True)
        self.del_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)

    def edit_item(self):
        current = self.item_list.currentItem()
        if not current: return
        
        item_id = current.data(Qt.UserRole)
        item = next((i for i in self.slot_data["items"] if i["id"] == item_id), None)
        
        if item:
            # Disable buttons
            self.add_btn.setEnabled(False)
            self.del_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            
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
            
            # Enable buttons
            self.add_btn.setEnabled(True)
            self.del_btn.setEnabled(True)
            self.edit_btn.setEnabled(True)

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
        new_order = []
        for i in range(self.item_list.count()):
            list_item = self.item_list.item(i)
            item_id = list_item.data(Qt.UserRole)
            new_order.append(item_id)
            enabled = list_item.checkState() == Qt.Checked
            self.config_manager.toggle_item_enabled(self.slot_data["id"], item_id, enabled)

        self.config_manager.reorder_items(self.slot_data["id"], new_order)
        super().closeEvent(event)
