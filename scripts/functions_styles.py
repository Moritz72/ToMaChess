from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream
from .functions_util import get_root_directory


def get_stylesheet(stylesheet):
    return QFile(f"{get_root_directory()}/styles/{stylesheet}")


def set_stylesheet(stylesheet):
    sheet = get_stylesheet(stylesheet)
    sheet.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(sheet)
    QApplication.instance().setStyleSheet(stream.readAll())
