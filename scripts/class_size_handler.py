from PySide6.QtWidgets import QApplication
from .class_settings_handler import SETTINGS_HANDLER


def get_dp():
    return QApplication.instance().primaryScreen().logicalDotsPerInch()


def get_font_sizes(font_size):
    return {"medium": font_size, "large": int(font_size * 1.2), "extra_large": int(font_size * 1.5)}


def get_widget_size_factor(font_size, dp):
    return font_size * dp / 96


class Size_Handler:
    def __init__(self):
        self.dp = self.font_sizes = self.widget_size_factor = None

    def refresh(self):
        self.dp = get_dp()
        font_size = SETTINGS_HANDLER.get("font_size")
        self.font_sizes = get_font_sizes(font_size)
        self.widget_size_factor = get_widget_size_factor(font_size, self.dp)


SIZE_HANDLER = Size_Handler()
