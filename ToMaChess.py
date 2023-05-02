from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QIcon
from scripts.window_main import Window_Main
from scripts.functions_util import get_root_directory


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(f"{get_root_directory()}/images/icon.png"))
    font = QFont("MS Shell Dlg 2", 12)
    QApplication.setFont(font)
    main_window = Window_Main()
    main_window.showMaximized()
    app.exec()
