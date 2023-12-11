import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .functions_util import get_image, make_app_data_folder, remove_temporary_files


def run() -> None:
    make_app_data_folder()
    remove_temporary_files()
    from .window_main import Window_Main
    from .manager_database import MANAGER_DATABASE
    MANAGER_DATABASE.create_tables()
    app = QApplication([])
    app.setWindowIcon(QIcon(get_image("logo.png")))
    main_window = Window_Main()
    main_window.showMaximized()
    sys.exit(app.exec())
