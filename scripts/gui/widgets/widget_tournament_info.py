from abc import abstractmethod
from PySide6.QtWidgets import QWidget
from ...tournament.tournaments.tournament import Tournament


class Widget_Tournament_Info(QWidget):
    def __init__(self, name: str, tournament: Tournament) -> None:
        super().__init__()
        self.name = name
        self.tournament: Tournament = tournament

    @abstractmethod
    def refresh(self) -> None:
        pass
