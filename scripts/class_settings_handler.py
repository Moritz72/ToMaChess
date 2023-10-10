import os.path
from json import loads, dumps
from PySide6.QtGui import QFontDatabase
from .functions_util import read_file, write_file, get_root_directory

SETTINGS_VALID = {
    "language": lambda x: True,
    "style": lambda x: True,
    "font": lambda x: True,
    "font_size": lambda x: 2 < x < 40,
    "bbp_path": lambda x: os.path.exists(os.path.join(x, "bbpPairings.exe")),
    "pdf_path": lambda x: os.path.exists(x) or x == ""
}
SETTINGS_DISPLAY = {
    "language": "Language",
    "style": "Style",
    "font": "Font",
    "font_size": "Font Size",
    "bbp_path": "bbpPairings Path",
    "pdf_path": "PDF Output Path"
}

DEFAULT_FONTS = ("Arial",)


def get_font_list():
    font_list = list(QFontDatabase().families())
    for font in DEFAULT_FONTS:
        if font in font_list:
            return sorted(font_list, key=lambda x: x == font, reverse=True)
    return font_list


def get_defaults():
    return {
        "language": ["English (en)", "Deutsch (de)", "日本語 (jp)"],
        "style": ["Light", "Dark"],
        "font": get_font_list(),
        "font_size": 12,
        "bbp_path": os.path.join(get_root_directory(), "bbp"),
        "pdf_path": ""
    }


class Settings_Handler:
    def __init__(self):
        self.settings = None

    def set(self, key, value):
        if SETTINGS_VALID[key](value):
            self.settings[key] = value

    def save(self):
        write_file(os.path.join(get_root_directory(), "settings.json"), dumps(self.settings))

    def load(self):
        settings_path = os.path.join(get_root_directory(), "settings.json")
        if not os.path.exists(settings_path):
            self.reset()
        self.settings = get_defaults()
        for key, value in loads(read_file(settings_path)).items():
            self.set(key, value)
        self.save()

    def reset(self):
        self.settings = get_defaults()
        self.save()


SETTINGS_HANDLER = Settings_Handler()
