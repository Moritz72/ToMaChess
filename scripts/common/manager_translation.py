import os.path
from typing import Sequence
from gettext import GNUTranslations, translation
from .functions_util import get_root_directory
from .manager_settings import MANAGER_SETTINGS

LOCALES_PATH = os.path.join(get_root_directory(), "locales")


class Manager_Translation:
    def __init__(self) -> None:
        self.language: str = "English (en)"
        self.translation: GNUTranslations = translation("base", LOCALES_PATH, languages=[self.language])
        self.translation_shortened: GNUTranslations = translation("short",  LOCALES_PATH, languages=[self.language])

    def refresh(self) -> None:
        self.language = MANAGER_SETTINGS["language"][0]
        self.translation = translation("base", LOCALES_PATH, languages=[self.language])
        self.translation_shortened = translation("short", LOCALES_PATH, languages=[self.language])

    def tl(self, text: str | Sequence[str], short: bool = False, insert: str | None = None) -> str:
        if isinstance(text, str):
            return self.tl_string(text, short=short, insert=insert)
        return ''.join((self.tl_string(t, short=short, insert=insert)) for t in text)

    def tl_string(self, text: str, short: bool = False, insert: str | None = None) -> str:
        if text == "":
            return ""
        tl = self.translation_shortened.gettext(text) if short else self.translation.gettext(text)
        if insert is not None:
            tl = tl.replace("{}", insert)
        return tl

    def tl_list(self, texts: Sequence[str], short: bool = False) -> list[str]:
        return [self.tl(text, short=short) for text in texts]


MANAGER_TRANSLATION = Manager_Translation()
