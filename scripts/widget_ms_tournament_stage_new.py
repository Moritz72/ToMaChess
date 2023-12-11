from __future__ import annotations
from abc import abstractmethod
from typing import TypeVar, Generic
from functools import partial
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from .player import Player
from .team import Team
from .tournament import Tournament, Participant
from .advance_list import Advance_List
from .table_drag import Table_Drag
from .window_choice_objects import Window_Choice_Objects, Window_Choice_Players, Window_Choice_Teams
from .window_tournament_new import Window_Tournament_New_Generic, Window_Tournament_New_Player, \
    Window_Tournament_New_Team
from .window_advance_participants import Window_Advance_Participants
from .gui_functions import get_button, add_widgets_in_layout, close_window
from .gui_table import add_content_to_table, add_button_to_table, set_up_table, size_table

T = TypeVar('T', bound=Participant)


class Widget_MS_Tournament_Stage_New_Generic(QWidget, Generic[T]):
    validate_advance_lists = Signal(int)

    def __init__(
            self, stage: int, previous_stage: Widget_MS_Tournament_Stage_New_Generic[T] | None = None
    ) -> None:
        super().__init__()
        self.stage: int = stage
        self.previous_stage: Widget_MS_Tournament_Stage_New_Generic[T] | None = previous_stage

        self.tournaments: list[Tournament] = []
        self.advance_lists: list[Advance_List] = []
        self.new_tournament_window: Window_Tournament_New_Generic[T] | None = None
        self.add_participants_window: Window_Choice_Objects[T] | None = None
        self.add_participants_tournament: Tournament | None = None
        self.advance_participants_window: Window_Advance_Participants | None = None

        self.layout_main: QHBoxLayout = QHBoxLayout(self)
        self.layout_main.addWidget(QWidget())
        self.table: Table_Drag = Table_Drag()
        self.fill_in_table()
        self.table.swapped.connect(self.swap_table)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.table)
        self.layout_main.addLayout(layout)
        self.set_buttons()

    def add_tournament_row(self, row: int, name: str, mode: str, participant_count: int) -> None:
        connect = self.open_add_participants if self.stage == 0 else self.open_advance_participants
        add_content_to_table(self.table, name, row, 0, bold=True)
        add_content_to_table(self.table, mode, row, 1, edit=False)
        add_content_to_table(self.table, participant_count, row, 2, edit=False, align=Qt.AlignmentFlag.AlignCenter)
        add_button_to_table(self.table, row, 3, "medium", None, "Participants", connect=connect, translate=True)
        add_button_to_table(self.table, row, 4, "medium", None, "Copy", connect=self.copy_tournament, translate=True)
        add_button_to_table(self.table, row, 5, "medium", None, '-', connect=self.remove_tournament, translate=True)

    def fill_in_table(self) -> None:
        for row, tournament in enumerate(self.tournaments):
            if self.table.item(row, 0) is not None:
                tournament.set_name(self.table.item(row, 0).text())

        set_up_table(self.table, 0, 6, header_horizontal=["Name", "Mode", "Participants", "", "", ""], translate=True)
        size_table(self.table, len(self.tournaments), 3.5, max_width=55, widths=[None, None, 5, 8, 8, 3.5])

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, tournament in enumerate(self.tournaments):
            self.add_tournament_row(i, tournament.get_name(), tournament.get_mode(), tournament.get_participant_count())

    def set_buttons(self) -> None:
        add_button = get_button(
            "large", (10, 5), "Add\nTournament", connect=self.open_new_tournament_window, translate=True
        )
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        add_widgets_in_layout(self.layout_main, layout_buttons, [add_button])

    def swap_table(self) -> None:
        self.tournaments = [self.tournaments[i] for i in self.table.permutation]
        if bool(self.advance_lists):
            self.advance_lists = [self.advance_lists[i] for i in self.table.permutation]
        self.fill_in_table()

    def remove_tournament(self) -> None:
        row = self.table.currentRow()
        if self.stage > 0:
            self.advance_lists.pop(row)
        tournament = self.tournaments.pop(row)
        if tournament.get_participant_count() > 0:
            self.validate_advance_lists.emit(self.stage)
        tournament.set_participants([])
        tournament.set_shallow_participant_count(0)
        self.fill_in_table()

    def open_new_tournament_window(self) -> None:
        close_window(self.new_tournament_window)
        self.new_tournament_window = self.get_new_tournament_window()
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def copy_tournament(self) -> None:
        row = self.table.currentRow()
        new_tournament = self.tournaments[row].copy()
        new_tournament.reload_uuid()
        self.tournaments.insert(row + 1, new_tournament)
        if self.stage > 0:
            new_advance_list = Advance_List(new_tournament)
            new_advance_list.extend(self.advance_lists[row])
            self.advance_lists.insert(row + 1, new_advance_list)
        self.fill_in_table()

    def add_tournament(self) -> None:
        assert(self.new_tournament_window is not None and self.new_tournament_window.new_tournament is not None)
        self.tournaments.append(self.new_tournament_window.new_tournament)
        if self.stage > 0:
            self.advance_lists.append(Advance_List(self.new_tournament_window.new_tournament))
        self.fill_in_table()

    def update_added_participants(self) -> None:
        assert(self.add_participants_window is not None and self.add_participants_tournament is not None)
        participants = self.add_participants_window.get_checked_objects()
        self.add_participants_tournament.set_participants(participants)

        self.add_participants_window, self.add_participants_tournament = None, None
        self.fill_in_table()
        self.validate_advance_lists.emit(self.stage)

    def open_add_participants(self) -> None:
        close_window(self.add_participants_window)
        self.add_participants_tournament = self.tournaments[self.table.currentRow()]
        checked_uuids = {
            participant.get_uuid_tuple() for participant in self.add_participants_tournament.get_participants()
        }
        self.add_participants_window = self.get_add_participants_window(checked_uuids)
        self.add_participants_window.window_closed.connect(self.update_added_participants)
        self.add_participants_window.show()

    def open_advance_participants(self) -> None:
        assert(self.previous_stage is not None)
        close_window(self.advance_participants_window)
        self.advance_participants_window = Window_Advance_Participants(
            self.advance_lists[self.table.currentRow()], self.previous_stage.tournaments, parent=self
        )
        self.advance_participants_window.window_closed.connect(partial(self.validate_advance_lists.emit, self.stage))
        self.advance_participants_window.show()

    @abstractmethod
    def get_new_tournament_window(self) -> Window_Tournament_New_Generic[T]:
        pass

    @abstractmethod
    def get_add_participants_window(self, checked_uuids: set[tuple[str, str]]) -> Window_Choice_Objects[T]:
        pass


class Widget_MS_Tournament_Stage_New_Player(Widget_MS_Tournament_Stage_New_Generic[Player]):
    def __init__(
            self, stage: int, previous_stage: Widget_MS_Tournament_Stage_New_Generic[Player] | None = None
    ) -> None:
        super().__init__(stage, previous_stage)

    def get_new_tournament_window(self) -> Window_Tournament_New_Generic[Player]:
        return Window_Tournament_New_Player(add_participants=False, parent=self)

    def get_add_participants_window(self, checked_uuids: set[tuple[str, str]]) -> Window_Choice_Objects[Player]:
        return Window_Choice_Players("Add Participants", checked_uuids=checked_uuids, parent=self)


class Widget_MS_Tournament_Stage_New_Team(Widget_MS_Tournament_Stage_New_Generic[Team]):
    def __init__(
            self, stage: int, previous_stage: Widget_MS_Tournament_Stage_New_Generic[Team] | None = None
    ) -> None:
        super().__init__(stage, previous_stage)

    def get_new_tournament_window(self) -> Window_Tournament_New_Generic[Team]:
        return Window_Tournament_New_Team(add_participants=False, parent=self)

    def get_add_participants_window(self, checked_uuids: set[tuple[str, str]]) -> Window_Choice_Objects[Team]:
        return Window_Choice_Teams("Add Participants", checked_uuids=checked_uuids, parent=self)
