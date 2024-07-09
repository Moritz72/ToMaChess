from PySide6.QtWidgets import QWidget
from ...tournament.tournaments.tournament import Tournament


class Widget_Tournament_Info(QWidget):
    def __init__(self, name: tuple[str, ...], tournament: Tournament) -> None:
        super().__init__()
        self.name: tuple[str, ...] = name
        self.tournament: Tournament = tournament
