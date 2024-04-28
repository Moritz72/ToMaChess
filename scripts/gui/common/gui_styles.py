import os.path
from typing import cast
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QApplication
from ...common.functions_util import get_root_directory


def get_stylesheet(stylesheet: str) -> QFile:
    return QFile(os.path.join(get_root_directory(), "styles", stylesheet))


def set_stylesheet(stylesheet: str) -> None:
    sheet = get_stylesheet(stylesheet)
    sheet.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
    stream = QTextStream(sheet)
    app = QApplication.instance()
    assert(app is not None)
    cast(QApplication, app).setStyleSheet(stream.readAll())
