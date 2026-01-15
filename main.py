import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import AppStyles

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setPalette(AppStyles.get_palette())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
