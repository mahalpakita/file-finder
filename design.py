from pathlib import Path

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import QTimer, Qt, QRect
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QMovie


class LoadingOverlay(QWidget):
    """Overlay that shows a semi-transparent background and either an animated GIF
    (preferred) or a drawn spinner as a fallback.

    By default it will try to load `amelia-watson.gif` from the current working
    directory. If the file is missing or invalid, the painted spinner is used.
    """
    def __init__(self, parent=None, gif_path: str = "amelia-watson.gif"):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_angle)
        # spinner fallback uses the timer
        self.timer.start(50)

        self.movie = None
        self.gif_label = None

        # Try to load the animated GIF if available
        try:
            p = Path(gif_path)
            if not p.is_absolute():
                p = Path.cwd() / gif_path
            if p.exists():
                m = QMovie(str(p))
                if m.isValid():
                    self.movie = m
                    self.gif_label = QLabel(self)
                    self.gif_label.setAttribute(Qt.WA_TranslucentBackground, True)
                    self.gif_label.setAlignment(Qt.AlignCenter)
                    self.gif_label.setMovie(self.movie)
                    # make label cover the overlay so the movie is centered
                    self.gif_label.setGeometry(self.rect())
                    self.movie.start()
        except Exception:
            # any failure falls back to painted spinner
            self.movie = None
            self.gif_label = None

    def update_angle(self):
        self.angle = (self.angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        import math
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw semi-transparent overlay background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

        # If a GIF is present and playing, the label will display it; still draw
        # the small caption under the animation for consistency.
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # Draw caption text (same look as before)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.setPen(QColor(230, 190, 255))
        painter.drawText(QRect(0, cy + 80, w, 40), Qt.AlignCenter, "Searching... 🔍")
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor(180, 140, 220))
        painter.drawText(QRect(0, cy + 130, w, 30), Qt.AlignCenter, "Finding files for you! ✨")

        # If no GIF, draw fallback spinner
        if not self.movie:
            colors = [QColor(138, 43, 226), QColor(75, 0, 130), QColor(30, 144, 255)]
            spinner_radius = 40
            line_length = 20
            for i in range(12):
                angle = (self.angle + i * 30) % 360
                rad = (angle * 3.14159) / 180.0
                color = colors[i % len(colors)]
                alpha = int(255 * (1.0 - (i / 12.0)))
                color.setAlpha(alpha)
                pen = QPen(color)
                pen.setWidth(3)
                painter.setPen(pen)
                x1 = cx + (spinner_radius * math.cos(rad))
                y1 = cy + (spinner_radius * math.sin(rad))
                x2 = cx + ((spinner_radius + line_length) * math.cos(rad))
                y2 = cy + ((spinner_radius + line_length) * math.sin(rad))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.end()

    def stop(self):
        try:
            if self.movie:
                self.movie.stop()
        except Exception:
            pass
        self.timer.stop()


def generate_stylesheet(accent1: str, accent2: str):
    """Return (stylesheet, label_color) for the dark theme using given accents."""
    # Dark mode colors (only dark theme supported)
    bg_color = "#1e1e1e"
    text_color = "#e0e0e0"
    border_color = "#3a3a3a"
    hover_border = "#555555"
    input_bg = "#2d2d2d"
    list_bg = "#252525"
    list_alt_bg = "#2a2a2a"
    list_hover = "#333333"
    list_select_bg = "#3a3a3a"
    list_select_border = "#555555"
    button_hover_stop1 = "#9c6e35"
    button_hover_stop2 = "#8a5c2a"
    button_press_stop1 = "#7a4f23"
    button_press_stop2 = "#6b431a"
    button_disabled_bg = "#3a3a3a"
    button_disabled_text = "#666666"
    label_color = "#b0b0b0"
    checkbox_border = "#555555"
    checkbox_checked_border = "#777777"

    app_css = f"""
    QWidget {{
        background: {bg_color};
        color: {text_color};
        font-family: Segoe UI, Arial, Helvetica, sans-serif;
        font-size: 11pt;
    }}
    QLabel {{
        color: {label_color};
    }}
    QLineEdit {{
        border: 1px solid {border_color};
        border-radius: 6px;
        padding: 6px;
        background: {input_bg};
        color: {text_color};
        selection-background-color: {accent1};
    }}
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent1}, stop:1 {accent2});
        border: 1px solid {hover_border};
        border-radius: 8px;
        padding: 6px 12px;
        font-weight: 500;
        color: #222222;
    }}
    QPushButton:hover {{
        border: 1px solid {hover_border};
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {button_hover_stop1}, stop:1 {button_hover_stop2});
        color: {text_color};
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {button_press_stop1}, stop:1 {button_press_stop2});
    }}
    QPushButton:disabled {{
        background: {button_disabled_bg};
        color: {button_disabled_text};
    }}
    QListWidget {{
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 6px;
        background: {list_bg};
        alternate-background-color: {list_alt_bg};
        color: {text_color};
        outline: 0px;
    }}
    QListWidget::item:alternate {{
        background-color: {list_alt_bg};
    }}
    QListWidget::item:selected {{
        background-color: {list_select_bg};
        border: 1px solid {list_select_border};
    }}
    QListWidget::item:hover {{
        background-color: {list_hover};
    }}
    QComboBox {{
        border: 1px solid {border_color};
        border-radius: 6px;
        padding: 4px 6px;
        background: {input_bg};
        color: {text_color};
        selection-background-color: {accent1};
    }}
    QComboBox:hover {{
        border: 1px solid {hover_border};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QCheckBox {{
        padding: 4px;
        color: {text_color};
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {checkbox_border};
        border-radius: 3px;
        background: {input_bg};
    }}
    QCheckBox::indicator:checked {{
        background: {accent1};
        border: 1px solid {checkbox_checked_border};
    }}
    QStatusBar {{
        background: {bg_color};
        color: {text_color};
        border-top: 1px solid {border_color};
    }}
    """

    return app_css, label_color
