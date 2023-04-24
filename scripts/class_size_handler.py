from PyQt5.QtWidgets import QApplication
from .functions_settings import get_settings


def get_dp():
    app = QApplication([])
    dp = app.primaryScreen().logicalDotsPerInch()
    del app
    return dp


def get_font_sizes(font_size):
    return {"medium": font_size, "large": int(font_size*1.2)}


def get_widget_size_factor(font_size, dp):
    return font_size*dp/96


class Size_Handler:
    def __init__(self):
        self.dp = get_dp()
        font_size = get_settings()["font_size"]
        self.font_sizes = get_font_sizes(font_size)
        self.widget_size_factor = get_widget_size_factor(font_size, self.dp)

    def refresh(self):
        font_size = get_settings()["font_size"]
        self.font_sizes = get_font_sizes(font_size)
        self.widget_size_factor = get_widget_size_factor(font_size, self.dp)
