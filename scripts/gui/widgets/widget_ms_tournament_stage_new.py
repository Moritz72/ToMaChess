from __future__ import annotations
from abc import abstractmethod
from functools import partial
from typing import Generic, TypeVar, cast
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from ..common.gui_functions import add_widgets_in_layout, close_window, get_button
from ..common.gui_table import add_button_to_table, add_content_to_table
from ..tables.table_objects import Table_Objects_Drag
from ..windows.window_advance_participants import Window_Advance_Participants
from ..windows.window_choice_objects import Window_Choice_Objects, Window_Choice_Players, Window_Choice_Teams
from ..windows.window_tournament_new import Window_Tournament_New_Generic, Window_Tournament_New_Player, \
    Window_Tournament_New_Team
from ...ms_tournament.advance_list import Advance_List
from ...player.player import Player
from ...team.team import Team
from ...tournament.common.type_declarations import Participant
from ...tournament.tournaments.tournament import Tournament

T = TypeVar('T', bound=Participant)


class Widget_MS_Tournament_Stage_New_Generic(QWidget, Generic[T]):
    validate_advance_lists = Signal(int)

    def __init__(
            self, stage: int, previous_stage: Widget_MS_Tournament_Stage_New_Generic[T] | None = None
    ) -> None:
        super().__init__()
        self.stage: int = stage
        self.previous_stage: Widget_MS_Tournament_Stage_New_Generic[T] | None = previous_stage

        self.advance_lists: dict[str, Advance_List] = dict()
        self.new_tournament_window: Window_Tournament_New_Generic[T] | None = None
        self.add_participants_window: Window_Choice_Objects[T] | None = None
        self.add_participants_tournament: Tournament | None = None
        self.advance_participants_window: Window_Advance_Participants | None = None

        self.layout_main: QHBoxLayout = QHBoxLayout(self)
        self.layout_main.addWidget(QWidget())
        self.table: Table_Objects_Drag[Tournament] = self.get_table()
        self.table.swapped.connect(self.fill_in_table)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.table)
        self.layout_main.addLayout(layout)
        self.set_buttons()

    def get_table(self) -> Table_Objects_Drag[Tournament]:
        return Table_Objects_Drag[Tournament](
            6, 3.5, 55, [None, None, 5, 8, 8, 3.5], ["Name", "Mode", "Participants", "", "", ""],
            stretches=[0, 1], translate=True, parent=self
        )

    def get_tournaments(self) -> list[Tournament]:
        return cast(list[Tournament], self.table.objects)

    def get_advance_lists(self) -> list[Advance_List]:
        if self.stage == 0:
            return []
        return [self.advance_lists[tournament.get_uuid()] for tournament in self.get_tournaments()]

    def fill_in_row(self, row: int, tournament: Tournament) -> None:
        participant_count = tournament.get_participant_count()
        connect = self.open_add_participants if self.stage == 0 else self.open_advance_participants
        add_content_to_table(self.table, tournament.get_name(), row, 0, bold=True)
        add_content_to_table(self.table, tournament.get_mode(), row, 1, edit=False, translate=True)
        add_content_to_table(self.table, str(participant_count), row, 2, edit=False, align=Qt.AlignmentFlag.AlignCenter)
        add_button_to_table(self.table, row, 3, "medium", None, "Participants", connect=connect, translate=True)
        add_button_to_table(self.table, row, 4, "medium", None, "Copy", connect=self.copy_tournament, translate=True)
        add_button_to_table(self.table, row, 5, "medium", None, '-', connect=self.remove_tournament, translate=True)

    def fill_in_table(self) -> None:
        tournaments = self.get_tournaments()
        for row, tournament in enumerate(tournaments):
            if self.table.item(row, 0) is not None:
                tournament.set_name(self.table.item(row, 0).text())
        for i, tournament in enumerate(tournaments):
            self.fill_in_row(i, tournament)

    def set_buttons(self) -> None:
        add_button = get_button(
            "large", (10, 5), "Add\nTournament", connect=self.open_new_tournament_window, translate=True
        )
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        add_widgets_in_layout(self.layout_main, layout_buttons, [add_button])

    def remove_tournament(self) -> None:
        tournament = self.get_tournaments()[self.table.currentRow()]
        is_not_empty = tournament.get_participant_count() > 0
        if self.stage > 0:
            self.advance_lists.pop(tournament.get_uuid())
        tournament.set_participants([])
        tournament.set_shallow_participant_count(0)
        self.table.delete_current_row()
        if is_not_empty:
            self.validate_advance_lists.emit(self.stage)

    def open_new_tournament_window(self) -> None:
        close_window(self.new_tournament_window)
        self.new_tournament_window = self.get_new_tournament_window()
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def copy_tournament(self) -> None:
        row = self.table.currentRow()
        tournament = self.get_tournaments()[row]
        new_tournament = tournament.copy()
        new_tournament.reload_uuid()
        if self.stage > 0:
            new_advance_list = Advance_List(new_tournament)
            new_advance_list.extend(self.advance_lists[tournament.get_uuid()])
            self.advance_lists[new_tournament.get_uuid()] = new_advance_list
        self.table.insert_object(row + 1, new_tournament)
        self.fill_in_table()

    def add_tournament(self) -> None:
        assert(self.new_tournament_window is not None and self.new_tournament_window.new_tournament is not None)
        tournament = self.new_tournament_window.new_tournament
        self.table.insert_object(self.table.rowCount(), tournament)
        if self.stage > 0:
            self.advance_lists[tournament.get_uuid()] = Advance_List(tournament)
        self.fill_in_row(self.table.rowCount() - 1, tournament)

    def update_added_participants(self) -> None:
        assert(self.add_participants_window is not None and self.add_participants_tournament is not None)
        participants = self.add_participants_window.get_checked_objects()
        self.add_participants_tournament.set_participants(participants)

        self.add_participants_window, self.add_participants_tournament = None, None
        self.fill_in_table()
        self.validate_advance_lists.emit(self.stage)

    def open_add_participants(self) -> None:
        close_window(self.add_participants_window)
        self.add_participants_tournament = self.get_tournaments()[self.table.currentRow()]
        checked_uuids = {
            participant.get_uuid_tuple() for participant in self.add_participants_tournament.get_participants()
        }
        self.add_participants_window = self.get_add_participants_window(checked_uuids)
        self.add_participants_window.window_closed.connect(self.update_added_participants)
        self.add_participants_window.show()

    def open_advance_participants(self) -> None:
        assert(self.previous_stage is not None)
        close_window(self.advance_participants_window)
        advance_list = self.advance_lists[self.get_tournaments()[self.table.currentRow()].get_uuid()]
        self.advance_participants_window = Window_Advance_Participants(
            advance_list, self.previous_stage.get_tournaments(), parent=self
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
