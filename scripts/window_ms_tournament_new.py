from abc import abstractmethod
from typing import TypeVar, Generic
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QLineEdit, QCheckBox
from PySide6.QtCore import Qt, Signal, QSize
from .player import Player
from .team import Team
from .tournament import Participant
from .ms_tournament import MS_Tournament
from .widget_ms_tournament_stage_new import Widget_MS_Tournament_Stage_New_Generic,\
    Widget_MS_Tournament_Stage_New_Player, Widget_MS_Tournament_Stage_New_Team
from .gui_functions import get_button, get_scroll_area_widgets_and_layouts, add_widgets_in_layout, get_lineedit, \
    get_label, get_check_box, add_widgets_to_layout, set_window_title, set_window_size

T = TypeVar('T', bound=Participant)


class Window_MS_Tournament_New_Generic(QMainWindow, Generic[T]):
    added_tournament = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "New Multi-Stage Tournament")

        self.name_line: QLineEdit | None = None
        self.draw_lots_check: QCheckBox | None = None
        self.new_tournament: MS_Tournament | None = None
        self.stage_widgets: list[Widget_MS_Tournament_Stage_New_Generic[T]] = []

        self.widget: QWidget = QWidget()
        self.layout_main: QVBoxLayout = QVBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.add_top_line()
        _, _, self.layout_inner = get_scroll_area_widgets_and_layouts(self.layout_main, [])
        self.add_buttons()
        self.add_stage()
        self.add_stage()

        set_window_size(self, QSize(0, 0), factor_y=.8)
        self.setFixedWidth(self.height())
        self.move(self.pos().x() - self.width() // 2, self.pos().y())

    def add_top_line(self) -> None:
        name_label = get_label("Name", "large", translate=True)
        self.name_line = get_lineedit("medium", (15, 2.5))
        draw_lots_label = get_label("Draw Lots in Case of Tie", "large", translate=True)
        self.draw_lots_check = get_check_box(True, (2.5, 2.5))

        layout = QHBoxLayout()
        layout.addStretch()
        add_widgets_to_layout(layout, (name_label, self.name_line))
        layout.addStretch()
        add_widgets_to_layout(layout, (draw_lots_label, self.draw_lots_check))
        layout.addStretch()
        self.layout_main.addLayout(layout)

    def add_buttons(self) -> None:
        add_widgets_in_layout(self.layout_main, QHBoxLayout(), (
            get_button("large", None, "Add\nStage", connect=self.add_stage, translate=True),
            get_button("large", None, "Remove\nStage", connect=self.remove_stage, translate=True),
            get_button("large", None, "Create\nTournament", connect=self.create_tournament, translate=True)
        ))

    def add_stage(self) -> None:
        widget = self.get_new_stage_widget(self.layout_inner.count())
        self.layout_inner.addWidget(widget)
        self.stage_widgets.append(widget)
        widget.validate_advance_lists.connect(self.validate_advance_lists)

    def remove_stage(self) -> None:
        if len(self.stage_widgets) > 1:
            self.layout_inner.takeAt(self.layout_inner.count() - 1).widget().deleteLater()
            self.stage_widgets.pop()

    def create_tournament(self) -> None:
        stages_tournaments = [stage_widget.tournaments for stage_widget in self.stage_widgets]
        stages_advance_lists = [[
            advance_list.get_simplified(stages_tournaments[stage - 1]) for advance_list in stage_widget.advance_lists
        ] for stage, stage_widget in enumerate(self.stage_widgets)]

        assert(self.name_line is not None and self.draw_lots_check is not None)
        name = self.name_line.text()
        draw_lots = self.draw_lots_check.checkState() == Qt.CheckState.Checked
        self.new_tournament = MS_Tournament(stages_tournaments, name, None, stages_advance_lists, draw_lots)

        if self.new_tournament.is_valid():
            self.new_tournament.possess_participants_and_tournaments()
            for tournament in self.new_tournament.get_current_tournaments():
                tournament.seat_participants()
            self.added_tournament.emit()
            self.close()

    def validate_advance_lists(self, stage: int) -> None:
        for stage_widget in self.stage_widgets[stage:]:
            for advance_list in stage_widget.advance_lists:
                advance_list.validate()
            stage_widget.fill_in_table()

    @abstractmethod
    def get_new_stage_widget(self, stage: int) -> Widget_MS_Tournament_Stage_New_Generic[T]:
        pass


class Window_MS_Tournament_New_Player(Window_MS_Tournament_New_Generic[Player]):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

    def get_new_stage_widget(self, stage: int) -> Widget_MS_Tournament_Stage_New_Generic[Player]:
        return Widget_MS_Tournament_Stage_New_Player(stage, None if stage == 0 else self.stage_widgets[stage - 1])


class Window_MS_Tournament_New_Team(Window_MS_Tournament_New_Generic[Team]):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

    def get_new_stage_widget(self, stage: int) -> Widget_MS_Tournament_Stage_New_Generic[Team]:
        return Widget_MS_Tournament_Stage_New_Team(stage, None if stage == 0 else self.stage_widgets[stage - 1])
