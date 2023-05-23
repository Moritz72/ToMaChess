from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QIcon
from scripts.window_main import Window_Main
from scripts.functions_util import get_image, remove_temporary_files
from scripts.class_database_handler import database_handler


if __name__ == "__main__":
    remove_temporary_files()
    database_handler.create_tables()
    app = QApplication([])
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(get_image("logo.png")))
    font = QFont("MS Shell Dlg 2", 12)
    QApplication.setFont(font)
    main_window = Window_Main()
    main_window.showMaximized()
    app.exec()
