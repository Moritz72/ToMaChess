import os.path
from json import loads, dumps
from .functions_util import read_file, write_file, get_root_directory

defaults = {
    "font_size": 12,
    "bbp_path": os.path.join(get_root_directory(), "bbp"),
    "pdf_path": ""
}

settings_valid = {
    "font_size": lambda x: 2 < x < 40,
    "bbp_path": lambda x: os.path.exists(os.path.join(x, "bbpPairings.exe")),
    "pdf_path": lambda x: os.path.exists(x) or x == ""
}

settings_display = {
    "font_size": "Font Size",
    "bbp_path": "bbpPairings Path",
    "pdf_path": "PDF Output Path"
}


def get_settings():
    settings_path = os.path.join(get_root_directory(), "settings.json")
    if not os.path.exists(settings_path):
        reset_settings()
    settings = defaults | loads(read_file(settings_path))
    save_settings(settings)
    return settings


def reset_settings():
    write_file(os.path.join(get_root_directory(), "settings.json"), dumps(defaults))


def save_settings(settings):
    write_file(os.path.join(get_root_directory(), "settings.json"), dumps(settings))


class Settings_Handler:
    def __init__(self):
        self.settings = get_settings()

    def reload(self):
        self.settings = get_settings()


settings_handler = Settings_Handler()
