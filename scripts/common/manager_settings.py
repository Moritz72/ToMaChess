import os.path
from json import dumps, loads
from typing import Any, Callable
from PySide6.QtGui import QFontDatabase
from .functions_util import get_app_data_directory, get_root_directory, read_file, write_file

SETTINGS_VALID: dict[str, Callable[[Any], bool]] = {
    "language": lambda x: True,
    "style": lambda x: True,
    "font": lambda x: x[0] in get_font_list(),
    "font_size": lambda x: 2 < x < 40,
    "bbp_path": lambda x: os.path.exists(os.path.join(x, "bbpPairings.exe")),
    "pdf_path": lambda x: os.path.exists(x) or x == "",
    "server_address": lambda x: True,
    "server_username": lambda x: True,
    "server_password": lambda x: True
}
SETTINGS_DISPLAY = {
    "language": "Language",
    "style": "Style",
    "font": "Font",
    "font_size": "Font Size",
    "bbp_path": "bbpPairings Path",
    "pdf_path": "PDF Output Path",
    "server_address": "Server Address",
    "server_username": "Server Username",
    "server_password": "Server Password"
}

DEFAULT_FONTS = ("Carlito", "Arial")


def get_font_list() -> list[str]:
    font_list = list(QFontDatabase.families())
    for font in DEFAULT_FONTS:
        if font in font_list:
            return sorted(font_list, key=lambda x: x == font, reverse=True)
    return font_list


def get_defaults() -> dict[str, Any]:
    return {
        "language": ["English (en)", "Deutsch (de)", "日本語 (jp)"],
        "style": ["Light", "Dark"],
        "font": get_font_list(),
        "font_size": 12,
        "bbp_path": os.path.join(get_root_directory(), "bbp"),
        "pdf_path": "",
        "server_address": "",
        "server_username": "",
        "server_password": ""
    }


class Manager_Settings(dict[str, Any]):
    def __init__(self) -> None:
        super().__init__()

    def __setitem__(self, key: str, value: Any) -> None:
        if SETTINGS_VALID[key](value):
            super().__setitem__(key, value)

    def save(self) -> None:
        write_file(os.path.join(get_app_data_directory(), "settings.json"), dumps(self))

    def load(self) -> None:
        self.reset()
        settings_path = os.path.join(get_app_data_directory(), "settings.json")
        if not os.path.exists(settings_path):
            self.save()
        for key, value in loads(read_file(settings_path)).items():
            self[key] = value

    def reset(self) -> None:
        self.clear()
        self.update(get_defaults())


MANAGER_SETTINGS = Manager_Settings()
