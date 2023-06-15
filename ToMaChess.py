from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from scripts.window_main import Window_Main
from scripts.functions_util import get_image, remove_temporary_files
from scripts.class_database_handler import DATABASE_HANDLER


if __name__ == "__main__":
    remove_temporary_files()
    DATABASE_HANDLER.create_tables()
    app = QApplication([])
    app.setWindowIcon(QIcon(get_image("logo.png")))
    main_window = Window_Main()
    main_window.showMaximized()
    app.exec()
