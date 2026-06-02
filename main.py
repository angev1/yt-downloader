import sys
import os
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    project_root = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(project_root, 'app', 'style.qss')) as f:
        app.setStyleSheet(f.read())

    window = MainWindow(project_root)

    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()