from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from scripts.window_main import Window_Main


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    font = QFont("MS Shell Dlg 2", 12)
    QApplication.setFont(font)
    main_window = Window_Main()
    main_window.showMaximized()
    app.exec()
