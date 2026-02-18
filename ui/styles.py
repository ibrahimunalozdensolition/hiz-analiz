from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class AppStyles:
    BG_WHITE = "#FFFFFF"
    BG_LIGHT_GRAY = "#F5F5F5"
    TEXT_DARK_GRAY = "#2C3E50"
    TEXT_BLACK = "#000000"
    ACCENT_NAVY = "#1E3A8A"
    ACCENT_LIGHT_NAVY = "#2563EB"
    BORDER_LIGHT_GRAY = "#E5E7EB"
    
    @staticmethod
    def get_stylesheet():
        return f"""
            QMainWindow {{
                background-color: {AppStyles.BG_LIGHT_GRAY};
            }}
            
            QWidget {{
                background-color: {AppStyles.BG_WHITE};
                color: {AppStyles.TEXT_DARK_GRAY};
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 15px;
                font-weight: bold;
            }}
            
            QPushButton {{
                background-color: {AppStyles.ACCENT_NAVY};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                min-height: 35px;
            }}
            
            QPushButton:hover {{
                background-color: {AppStyles.ACCENT_LIGHT_NAVY};
            }}
            
            QPushButton:pressed {{
                background-color: #1E40AF;
            }}
            
            QPushButton:disabled {{
                background-color: {AppStyles.BORDER_LIGHT_GRAY};
                color: #9CA3AF;
            }}
            
            QLabel {{
                color: {AppStyles.TEXT_DARK_GRAY};
                background-color: transparent;
                font-weight: bold;
            }}
            
            QLabel#title {{
                font-size: 20px;
                font-weight: bold;
                color: {AppStyles.TEXT_BLACK};
                padding: 10px;
            }}
            
            QLabel#videoLabel {{
                background-color: {AppStyles.TEXT_BLACK};
                border: 2px solid {AppStyles.BORDER_LIGHT_GRAY};
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }}
            
            QGroupBox {{
                background-color: {AppStyles.BG_WHITE};
                border: 2px solid {AppStyles.BORDER_LIGHT_GRAY};
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px 10px 10px 10px;
                font-size: 16px;
                font-weight: bold;
                color: {AppStyles.TEXT_BLACK};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 5px;
                padding: 0 8px;
            }}
            
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                border: 2px solid {AppStyles.BORDER_LIGHT_GRAY};
                border-radius: 6px;
                padding: 8px;
                background-color: {AppStyles.BG_WHITE};
                color: {AppStyles.TEXT_BLACK};
                font-size: 15px;
                font-weight: bold;
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {AppStyles.ACCENT_NAVY};
            }}
            
            QSlider::groove:horizontal {{
                border: 1px solid {AppStyles.BORDER_LIGHT_GRAY};
                height: 8px;
                background: {AppStyles.BG_LIGHT_GRAY};
                margin: 2px 0;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background: {AppStyles.ACCENT_NAVY};
                border: 2px solid {AppStyles.BG_WHITE};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {AppStyles.ACCENT_LIGHT_NAVY};
            }}
            
            QStatusBar {{
                background-color: {AppStyles.BG_WHITE};
                color: {AppStyles.TEXT_DARK_GRAY};
                border-top: 1px solid {AppStyles.BORDER_LIGHT_GRAY};
                font-size: 14px;
                font-weight: bold;
            }}
            
            QTextEdit {{
                border: 2px solid {AppStyles.BORDER_LIGHT_GRAY};
                border-radius: 6px;
                padding: 10px;
                background-color: {AppStyles.BG_WHITE};
                color: {AppStyles.TEXT_DARK_GRAY};
                font-family: "Consolas", "Courier New", monospace;
                font-size: 14px;
                font-weight: bold;
            }}
            
            QListWidget {{
                border: 2px solid {AppStyles.BORDER_LIGHT_GRAY};
                border-radius: 6px;
                background-color: {AppStyles.BG_WHITE};
                color: {AppStyles.TEXT_DARK_GRAY};
                font-size: 14px;
                font-weight: bold;
            }}
            
            QListWidget::item {{
                padding: 5px;
                font-weight: bold;
            }}
            
            QListWidget::item:selected {{
                background-color: {AppStyles.ACCENT_NAVY};
                color: white;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {AppStyles.BG_LIGHT_GRAY};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {AppStyles.BORDER_LIGHT_GRAY};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {AppStyles.ACCENT_NAVY};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            QScrollArea {{
                border: none;
                background-color: {AppStyles.BG_WHITE};
            }}
        """
    
    @staticmethod
    def get_palette():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(AppStyles.BG_LIGHT_GRAY))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(AppStyles.TEXT_DARK_GRAY))
        palette.setColor(QPalette.ColorRole.Base, QColor(AppStyles.BG_WHITE))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(AppStyles.BG_LIGHT_GRAY))
        palette.setColor(QPalette.ColorRole.Text, QColor(AppStyles.TEXT_DARK_GRAY))
        palette.setColor(QPalette.ColorRole.Button, QColor(AppStyles.ACCENT_NAVY))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
        return palette
