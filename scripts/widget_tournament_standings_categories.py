from PySide6.QtWidgets import QWidget, QVBoxLayout
from .widget_tournament_standings import Widget_Tournament_Standings
from .functions_gui import get_scroll_area_widgets_and_layouts


class Widget_Tournament_Standings_Categories(QWidget):
    def __init__(self, tournament):
        super().__init__()
        self.tournament = tournament
        self.table_widgets = [
            Widget_Tournament_Standings(self.tournament, category_range)
            for category_range in tournament.get_parameter("category_ranges")
        ]

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        _, widget_inner, _ = get_scroll_area_widgets_and_layouts(self.layout, self.table_widgets)
        widget_inner.setFixedHeight(sum(table_widget.maximumHeight() for table_widget in self.table_widgets))

    def update(self):
        for table_widget in self.table_widgets:
            table_widget.update()
