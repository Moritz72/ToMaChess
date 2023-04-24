from json import loads, dumps
from .functions_util import read_file, write_file, get_root_directory

defaults = {
    "font_size": 12,
    "bbp_path": f"{get_root_directory()}\\bbp"
}

settings_valid = {
    "font_size": lambda x: 2 < x < 40,
    "bbp_path": lambda x: True
}

settings_display = {
    "font_size": "Font Size",
    "bbp_path": "bbpPairings Path"
}


def get_settings():
    settings = defaults | loads(read_file(f"{get_root_directory()}/settings.json"))
    save_settings(settings)
    return settings


def reset_settings():
    write_file(f"{get_root_directory()}/settings.json", dumps(defaults))


def save_settings(settings):
    write_file(f"{get_root_directory()}/settings.json", dumps(settings))
