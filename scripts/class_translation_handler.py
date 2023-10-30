import os.path
import gettext
from .class_settings_handler import SETTINGS_HANDLER
from .functions_util import get_root_directory


class Translation_Handler:
    def __init__(self):
        self.language, self.translation, self.translation_shortened = None, None, None

    def refresh(self):
        self.language = SETTINGS_HANDLER.get("language")[0]
        locales_path = os.path.join(get_root_directory(), "locales")
        self.translation = gettext.translation("base", locales_path, languages=[self.language])
        self.translation_shortened = gettext.translation("short", locales_path, languages=[self.language])

    def tl(self, text, short=False, insert=None):
        if isinstance(text, str):
            return self.tl_string(text, short=short, insert=insert)
        return ''.join((self.tl_string(t, short=short, insert=insert)) for t in text)

    def tl_string(self, text, short=False, insert=None):
        if text == "":
            return ""
        tl = self.translation_shortened.gettext(text) if short else self.translation.gettext(text)
        if insert is not None:
            tl = tl.replace("{}", insert)
        return tl

    def tl_list(self, texts, short=False):
        return tuple(self.tl(text, short=short) for text in texts)


TRANSLATION_HANDLER = Translation_Handler()
