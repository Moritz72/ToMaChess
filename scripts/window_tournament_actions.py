from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from .window_confirm import Window_Confirm
from .window_tournament_edit_parameters import Window_Tournament_Edit_Parameters
from .window_choice_table import Window_Choice_Table
from .window_remove_table import Window_Remove_Table
from .functions_type import get_function
from .functions_gui import set_window_title, set_window_size, get_button, close_window
from PySide6.QtCore import QTimer


class Window_Tournament_Actions(QMainWindow):
    reload_local_signal = Signal()
    undo_signal = Signal()
    reload_global_signal = Signal()

    def __init__(self, tournament, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "Actions")

        self.tournament = tournament
        self.participant_type = "team" if self.tournament.is_team_tournament() else "player"
        self.load_function = get_function(self.participant_type, "load", multiple=True, specification="list")
        self.child_window = None

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.setCentralWidget(self.widget)

        self.add_buttons()

    def add_button(self, button, condition):
        if condition:
            self.layout.addWidget(button)

    def add_buttons(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()
        args = {"bold": True, "translate": True}
        buttons = (
            get_button("large", (25, 5), "Reload Pairings", connect_function=self.reload_action, **args),
            get_button("large", (25, 5), "Undo Last Round", connect_function=self.undo_action, **args),
            get_button("large", (25, 5), "Edit Parameters", connect_function=self.parameters_action, **args),
            get_button("large", (25, 5), "Drop Out Participants", connect_function=self.drop_out_action, **args),
            get_button("large", (25, 5), "Drop In Participants", connect_function=self.drop_in_action, **args)
        )
        conditions = (
            not self.tournament.is_done(),
            self.tournament.get_round() > 1,
            self.tournament.get_changeable_parameters(),
            self.tournament.drop_out_participants() and not self.tournament.is_done(),
            self.tournament.drop_in_participants() and not self.tournament.is_done()
        )
        for button, condition in zip(buttons, conditions):
            self.add_button(button, condition)

        QTimer.singleShot(0, self.adjust_size)

    def adjust_size(self):
        set_window_size(self, self.sizeHint())

    def set_child_window(self, window):
        close_window(self.child_window)
        self.child_window = window
        self.child_window.show()

    def confirm_action(self, action, title):
        self.set_child_window(Window_Confirm(title, parent=self))
        self.child_window.confirmed.connect(action)

    def reload_action(self):
        self.reload_local_signal.emit()

    def undo_action(self):
        self.confirm_action(self.undo_signal.emit, "Undo Last Round")

    def parameters_action(self):
        self.set_child_window(Window_Tournament_Edit_Parameters(self.tournament, parent=self))
        self.child_window.saved_changes.connect(self.reload_global_signal.emit)

    def drop_out_action(self):
        self.set_child_window(Window_Remove_Table(
            "Drop Out Participants", self.participant_type,
            self.tournament.get_participants(drop_outs=False).copy(), parent=self
        ))
        self.child_window.window_closed.connect(self.drop_out_closed)

    def drop_in_action(self):
        self.set_child_window(Window_Choice_Table(
            "Drop In Participants", self.participant_type,
            set(participant.get_uuid() for participant in self.tournament.get_participants(drop_outs=False)),
            parent=self
        ))
        self.child_window.window_closed.connect(self.drop_in_closed)

    def drop_out_closed(self):
        self.tournament.drop_out_participants(
            [participant.get_uuid() for participant in self.child_window.get_removed_objects()]
        )
        self.reload_local_signal.emit()

    def drop_in_closed(self):
        self.tournament.drop_in_participants(self.load_function("", self.child_window.get_checked_uuids()))
        self.reload_global_signal.emit()
