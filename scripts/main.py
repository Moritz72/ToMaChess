import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .window_main import Window_Main
from .functions_util import get_readme_text, get_image, remove_temporary_files
from .class_database_handler import DATABASE_HANDLER


def run():
    print(get_readme_text())
    remove_temporary_files()
    DATABASE_HANDLER.create_tables()
    app = QApplication([])
    app.setWindowIcon(QIcon(get_image("logo.png")))
    main_window = Window_Main()
    main_window.showMaximized()
    sys.exit(app.exec())
