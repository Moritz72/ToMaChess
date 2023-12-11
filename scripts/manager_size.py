from PySide6.QtWidgets import QApplication
from .manager_settings import MANAGER_SETTINGS


def get_dp() -> int:
    app = QApplication.instance()
    assert(app is not None)
    return app.primaryScreen().logicalDotsPerInch()


def get_font_sizes(font_size: int) -> dict[str, int]:
    return {"medium": font_size, "large": int(font_size * 1.2), "extra_large": int(font_size * 1.5)}


def get_widget_size_factor(font_size: int, dp: int) -> float:
    return font_size * dp / 96


class Manager_Size:
    def __init__(self) -> None:
        self.dp: int = 0
        self.font_sizes: dict[str, int] = dict()
        self.widget_size_factor: float = 0

    def refresh(self) -> None:
        self.dp = get_dp()
        font_size: int = MANAGER_SETTINGS["font_size"]
        self.font_sizes = get_font_sizes(font_size)
        self.widget_size_factor = get_widget_size_factor(font_size, self.dp)


MANAGER_SIZE = Manager_Size()
