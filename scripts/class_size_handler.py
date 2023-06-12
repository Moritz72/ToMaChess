from PyQt5.QtWidgets import QApplication
from .class_settings_handler import settings_handler


def get_dp():
    return QApplication.instance().primaryScreen().logicalDotsPerInch()


def get_font_sizes(font_size):
    return {"medium": font_size, "large": int(font_size * 1.2)}


def get_widget_size_factor(font_size, dp):
    return font_size * dp / 96


class Size_Handler:
    def __init__(self):
        self.dp, self.font_sizes, self.widget_size_factor = None, None, None

    def refresh(self):
        self.dp = get_dp()
        font_size = settings_handler.settings["font_size"]
        self.font_sizes = get_font_sizes(font_size)
        self.widget_size_factor = get_widget_size_factor(font_size, self.dp)


size_handler = Size_Handler()
