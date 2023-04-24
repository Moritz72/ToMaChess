from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_tournament import modes, mode_default
from .functions_player import load_players_all
from .functions_gui import add_widgets_to_layout, get_suitable_widget, get_value_from_suitable_widget,\
    get_button, get_label, get_lineedit, get_combo_box, get_scroll_area_widgets_and_layouts
from .window_add_players import Window_Add_Players


class Window_Tournament_New(QMainWindow):
    added_tournament = pyqtSignal()

    def __init__(self, add_participants=True):
        super().__init__()
        self.setWindowTitle("New Tournament")

        self.add_players = add_participants
        self.modes = list(modes.keys())
        self.players = load_players_all()
        self.add_players_window = Window_Add_Players(self.players)
        self.parameter_widget_data = None
        self.new_tournament = None
        self.name_line = None

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.splitter = QSplitter()
        self.splitter.setOrientation(1)
        self.layout.addWidget(self.splitter)
        self.setCentralWidget(self.widget)

        self.set_left_side()
        self.splitter.addWidget(QWidget())
        self.set_right_side(mode_default)
        self.setFixedSize(self.layout.sizeHint())

    def set_left_side(self):
        name_label = get_label("Name", "large")
        self.name_line = get_lineedit("medium", (15, 3))
        players_button = get_button(
            "medium", (10, 5), "Add\nParticipants", connect_function=self.add_players_window.show
        )
        if not self.add_players:
            players_button.setVisible(False)
        mode_label = get_label("Mode", "large")
        combo_box = get_combo_box(self.modes, "medium", (15, 3), mode_default)
        combo_box.activated[str].connect(lambda _: self.set_right_side(self.modes[combo_box.currentIndex()]))
        create_button = get_button("large", (11, 4), "Create", connect_function=self.create_tournament)

        widget = QWidget()
        layout = QVBoxLayout()
        add_widgets_to_layout(layout, (
            name_label, self.name_line, QLabel(), players_button, QLabel(),
            mode_label, combo_box, QLabel(), create_button
        ))
        widget.setLayout(layout)
        self.splitter.addWidget(widget)

    def set_right_side(self, mode):
        self.splitter.widget(1).setParent(None)
        self.new_tournament = modes[mode](None, [])
        parameter_display = self.new_tournament.get_parameter_display()

        self.parameter_widget_data = tuple((
            parameter,
            parameter_display[parameter],
            get_suitable_widget(value)
        ) for parameter, value in self.new_tournament.get_parameters())

        parameter_widgets = []
        for _, display, widget in self.parameter_widget_data:
            parameter_widgets = parameter_widgets+[get_label(display, "large"), widget, QLabel()]

        widget = QWidget()
        layout = QVBoxLayout()
        get_scroll_area_widgets_and_layouts(
            layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10
        )
        widget.setLayout(layout)
        self.splitter.addWidget(widget)

    def create_tournament(self):
        name = self.name_line.text()
        participants = [
            self.players[row] for row in range(self.add_players_window.table.rowCount())
            if self.add_players_window.table.cellWidget(row, 3).checkState() == Qt.Checked
        ]

        self.new_tournament.set_name(name)
        self.new_tournament.set_participants(participants)
        if self.add_players:
            self.new_tournament.seat_participants()

        for parameter, _, widget in self.parameter_widget_data:
            self.new_tournament.set_parameter(parameter, get_value_from_suitable_widget(widget))
        if (self.add_players and self.new_tournament.is_valid()) or \
                (not self.add_players and self.new_tournament.is_valid_parameters()):
            self.added_tournament.emit()
            self.close()
        else:
            self.new_tournament.clear_players()
