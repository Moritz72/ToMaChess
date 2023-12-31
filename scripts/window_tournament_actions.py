from __future__ import annotations
from typing import Callable, Any, cast
from dataclasses import dataclass, fields
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QTimer
from .player import Player
from .team import Team
from .tournament import Tournament
from .db_player import DB_Player_List
from .db_team import DB_Team_List
from .window_confirm import Window_Confirm
from .window_tournament_edit_parameters import Window_Tournament_Edit_Parameters
from .window_choice_objects import Window_Choice_Players, Window_Choice_Teams
from .window_drag_objects import Window_Drag_Players, Window_Drag_Teams
from .window_remove_objects import Window_Remove_Players, Window_Remove_Teams
from .gui_functions import set_window_title, set_window_size, get_button, close_window


@dataclass
class Windows:
    confirm: Window_Confirm | None = None
    parameters: Window_Tournament_Edit_Parameters | None = None
    drop_out: Window_Remove_Players | Window_Remove_Teams | None = None
    drop_in: Window_Choice_Players | Window_Choice_Teams | None = None
    add_byes: Window_Choice_Players | Window_Choice_Teams | None = None
    seeding: Window_Drag_Players | Window_Drag_Teams | None = None


class Window_Tournament_Actions(QMainWindow):
    reload_local_signal = Signal()
    undo_signal = Signal()
    reload_global_signal = Signal()

    def __init__(
            self, tournament: Tournament, associate: tuple[str, str] | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "Actions")

        self.tournament: Tournament = tournament
        self.associate: tuple[str, str] | None = associate
        self.windows: Windows = Windows()

        self.widget = QWidget()
        self.layout_main: QVBoxLayout = QVBoxLayout(self.widget)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.widget)

        self.add_buttons()

    def add_button(self, button: QPushButton, condition: bool) -> None:
        if condition:
            self.layout_main.addWidget(button)

    def add_buttons(self) -> None:
        for i in reversed(range(self.layout_main.count())):
            self.layout_main.itemAt(i).widget().deleteLater()
        args: dict[str, Any] = {"bold": True, "translate": True}
        buttons = (
            get_button("large", (25, 5), "Reload Pairings", connect=self.reload_action, **args),
            get_button("large", (25, 5), "Undo Last Round", connect=self.undo_action, **args),
            get_button("large", (25, 5), "Edit Parameters", connect=self.parameters_action, **args),
            get_button("large", (25, 5), "Drop Out Participants", connect=self.drop_out_action, **args),
            get_button("large", (25, 5), "Drop In Participants", connect=self.drop_in_action, **args),
            get_button("large", (25, 5), "Manage Byes", connect=self.add_byes_action, **args),
            get_button("large", (25, 5), "Seeding", connect=self.seeding_action, **args)
        )
        conditions = (
            not self.tournament.is_done(),
            self.tournament.is_undo_last_round_allowed(),
            bool(self.tournament.get_changeable_parameters()),
            self.tournament.is_drop_out_allowed(),
            self.tournament.is_drop_in_allowed(),
            self.tournament.is_add_byes_allowed(),
            self.tournament.is_seeding_allowed()
        )

        for button, condition in zip(buttons, conditions):
            self.add_button(button, condition)
        QTimer.singleShot(0, self.adjust_size)

    def adjust_size(self) -> None:
        set_window_size(self, self.sizeHint())

    def close_windows(self) -> None:
        for field in fields(self.windows):
            close_window(getattr(self.windows, field.name))
        self.windows = Windows()

    def confirm_action(self, action: Callable[[Window_Tournament_Actions], None], title: str) -> None:
        self.close_windows()
        self.windows.confirm = Window_Confirm(title, parent=self)
        self.windows.confirm.confirmed.connect(action)
        self.windows.confirm.show()

    def reload_action(self) -> None:
        self.reload_local_signal.emit()

    def undo_action(self) -> None:
        self.confirm_action(self.undo_signal.emit, "Undo Last Round")

    def parameters_action(self) -> None:
        self.close_windows()
        self.windows.parameters = Window_Tournament_Edit_Parameters(self.tournament, parent=self)
        self.windows.parameters.saved_changes.connect(self.reload_global_signal.emit)
        self.windows.parameters.show()

    def drop_out_action(self) -> None:
        participants = self.tournament.get_participants(drop_outs=False).copy()
        window: Window_Remove_Players | Window_Remove_Teams
        if self.tournament.is_team_tournament():
            window = Window_Remove_Teams("Drop Out Participants", cast(list[Team], participants), parent=self)
        else:
            window = Window_Remove_Players("Drop Out Participants", cast(list[Player], participants), parent=self)
        self.close_windows()
        self.windows.drop_out = window
        self.windows.drop_out.window_closed.connect(self.drop_out_closed)
        self.windows.drop_out.show()

    def drop_in_action(self) -> None:
        tuples = set(participant.get_uuid_tuple() for participant in self.tournament.get_participants(drop_outs=False))
        window: Window_Choice_Players | Window_Choice_Teams
        if self.tournament.is_team_tournament():
            window = Window_Choice_Teams("Drop In Participants", tuples, uuids_only=True, parent=self)
        else:
            window = Window_Choice_Players("Drop In Participants", tuples, uuids_only=True, parent=self)
        self.close_windows()
        self.windows.drop_in = window
        self.windows.drop_in.window_closed.connect(self.drop_in_closed)
        self.windows.drop_in.show()

    def add_byes_action(self) -> None:
        if self.associate is None:
            table_root = "tournaments_"
            uuid = self.tournament.get_uuid()
        else:
            table_root = "ms_tournaments_"
            uuid = self.associate[1]
        associates = [(self.tournament.get_name(), uuid)]
        excluded = {(uuid, associates[0][1]) for uuid in self.tournament.get_drop_outs()}
        checked = {(uuid, associates[0][1]) for uuid in self.tournament.get_byes()}
        window: Window_Choice_Players | Window_Choice_Teams
        if self.tournament.is_team_tournament():
            teams_db = DB_Team_List(cast(list[Team], self.tournament.get_participants()))
            window = Window_Choice_Teams(
                "Manage Byes", excluded, checked,
                table_root=table_root, associates=associates, db=teams_db, parent=self
            )
        else:
            players_db = DB_Player_List(cast(list[Player], self.tournament.get_participants()))
            window = Window_Choice_Players(
                "Manage Byes", excluded, checked,
                table_root=table_root, associates=associates, db=players_db, parent=self
            )
        self.close_windows()
        self.windows.add_byes = window
        self.windows.add_byes.window_closed.connect(self.add_byes_closed)
        self.windows.add_byes.show()

    def seeding_action(self) -> None:
        window: Window_Drag_Players | Window_Drag_Teams
        if self.tournament.is_team_tournament():
            teams = cast(list[Team], self.tournament.get_participants())
            window = Window_Drag_Teams(teams, "Seeding", parent=self)
        else:
            players = cast(list[Player], self.tournament.get_participants())
            window = Window_Drag_Players(players, "Seeding", parent=self)
        self.close_windows()
        self.windows.seeding = window
        self.windows.seeding.window_closed.connect(self.seeding_closed)
        self.windows.seeding.show()

    def drop_out_closed(self) -> None:
        assert(self.windows.drop_out is not None)
        uuids = [participant.get_uuid() for participant in self.windows.drop_out.get_removed_objects()]
        self.tournament.drop_out_participants(uuids)
        self.reload_local_signal.emit()

    def drop_in_closed(self) -> None:
        assert(self.windows.drop_in is not None)
        self.tournament.drop_in_participants(self.windows.drop_in.get_checked_objects())
        self.reload_global_signal.emit()

    def add_byes_closed(self) -> None:
        assert(self.windows.add_byes is not None)
        self.tournament.add_byes([uuid for uuid, _ in self.windows.add_byes.get_checked_tuples()])
        self.reload_local_signal.emit()

    def seeding_closed(self) -> None:
        assert(self.windows.seeding is not None)
        participants = self.tournament.get_participants()
        seeds = [participants.index(participant) for participant in self.windows.seeding.get_objects()]
        self.tournament.seed_participants(seeds)
        self.reload_local_signal.emit()
