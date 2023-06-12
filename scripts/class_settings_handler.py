import os.path
from json import loads, dumps
from PyQt5.QtGui import QFontDatabase
from .functions_util import read_file, write_file, get_root_directory

settings_valid = {
    "style": lambda x: True,
    "font": lambda x: True,
    "font_size": lambda x: 2 < x < 40,
    "bbp_path": lambda x: os.path.exists(os.path.join(x, "bbpPairings.exe")),
    "pdf_path": lambda x: os.path.exists(x) or x == ""
}

settings_display = {
    "style": "Style",
    "font": "Font",
    "font_size": "Font Size",
    "bbp_path": "bbpPairings Path",
    "pdf_path": "PDF Output Path"
}

default_fonts = ("MS Shell Dlg 2", "Arial")


def get_font_list():
    font_list = list(QFontDatabase().families())
    for font in default_fonts:
        if font in font_list:
            return sorted(font_list, key=lambda x: x == font, reverse=True)
    return font_list


def get_defaults():
    return {
        "style": ["Light", "Dark"],
        "font": get_font_list(),
        "font_size": 12,
        "bbp_path": os.path.join(get_root_directory(), "bbp"),
        "pdf_path": ""
    }


class Settings_Handler:
    def __init__(self):
        self.settings = None

    def save(self):
        write_file(os.path.join(get_root_directory(), "settings.json"), dumps(self.settings))

    def load(self):
        settings_path = os.path.join(get_root_directory(), "settings.json")
        if not os.path.exists(settings_path):
            self.reset()
        self.settings = get_defaults() | loads(read_file(settings_path))
        self.save()

    def reset(self):
        self.settings = get_defaults()
        self.save()


settings_handler = Settings_Handler()
