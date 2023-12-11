from PySide6.QtWidgets import QVBoxLayout
from .tournament import Tournament
from .widget_tournament_info import Widget_Tournament_Info
from .widget_tournament_standings import Widget_Tournament_Standings
from .gui_functions import get_scroll_area_widgets_and_layouts


class Widget_Tournament_Standings_Categories(Widget_Tournament_Info):
    def __init__(self, tournament: Tournament) -> None:
        super().__init__(tournament)
        self.tournament = tournament
        self.standing_widgets = [
            Widget_Tournament_Standings(self.tournament, category_range)
            for category_range in tournament.get_category_ranges()
        ]

        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        _, widget_inner, _ = get_scroll_area_widgets_and_layouts(self.layout_main, self.standing_widgets)
        widget_inner.setFixedHeight(sum(standing_widget.maximumHeight() for standing_widget in self.standing_widgets))

    def refresh(self) -> None:
        for standing_widget in self.standing_widgets:
            standing_widget.refresh()
