from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter
from PyQt5.QtCore import pyqtSignal
from .functions_player import load_players_list
from .functions_team import load_teams_list
from .functions_tournament import modes, modes_team, mode_default, mode_default_team
from .functions_categories import type_to_categories
from .functions_gui import add_widgets_to_layout, get_suitable_widget, get_value_from_suitable_widget,\
    get_button, get_label, get_lineedit, get_combo_box, get_scroll_area_widgets_and_layouts
from .window_choice_table import Window_Choice_Table
from .window_add_categories import Window_Add_Categories

type_to_modes = {"player": modes, "team": modes_team}
type_to_mode_default = {"player": mode_default, "team": mode_default_team}
type_to_load_functon = {"player": load_players_list, "team": load_teams_list}
type_to_add_participant_window_args = {"player": ("Add Player", "Players"), "team": ("Add Teams", "Teams")}


class Window_Tournament_New(QMainWindow):
    added_tournament = pyqtSignal()

    def __init__(self, participant_type="player", add_participants=True):
        super().__init__()
        self.setWindowTitle("New Tournament")

        self.add_participants = add_participants
        self.modes = type_to_modes[participant_type]
        self.mode_default = type_to_mode_default[participant_type]
        self.load_function = type_to_load_functon[participant_type]
        self.add_participants_window = Window_Choice_Table(*type_to_add_participant_window_args[participant_type])
        self.categories = type_to_categories[participant_type]
        self.add_categories_window = Window_Add_Categories(self.categories)
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
        self.set_right_side(self.mode_default)
        self.setFixedSize(self.layout.sizeHint())

    def set_left_side(self):
        name_label = get_label("Name", "large")
        self.name_line = get_lineedit("medium", (15, 3))
        add_participants_button = get_button(
            "medium", (10, 5), "Add\nParticipants", connect_function=self.add_participants_window.show
        )
        if not self.add_participants:
            add_participants_button.setVisible(False)
        mode_label = get_label("Mode", "large")
        combo_box = get_combo_box(list(self.modes), "medium", (15, 3), mode_default)
        combo_box.activated[str].connect(lambda: self.set_right_side(list(self.modes)[combo_box.currentIndex()]))
        create_button = get_button("large", (11, 4), "Create", connect_function=self.create_tournament)
        add_categories_button = get_button(
            "medium", (10, 5), "Add\nCategories", connect_function=self.add_categories_window.show
        )

        widget = QWidget()
        layout = QVBoxLayout()
        add_widgets_to_layout(layout, (name_label, self.name_line))
        add_widgets_to_layout(layout, (QLabel(), add_participants_button))
        add_widgets_to_layout(layout, (QLabel(), mode_label, combo_box))
        if len(self.categories) > 0:
            add_widgets_to_layout(layout, (QLabel(), add_categories_button))
        add_widgets_to_layout(layout, (QLabel(), create_button))
        widget.setLayout(layout)
        self.splitter.addWidget(widget)

    def set_right_side(self, mode):
        self.splitter.widget(1).setParent(None)
        self.new_tournament = self.modes[mode]([], "")
        parameter_display = self.new_tournament.get_parameter_display()

        self.parameter_widget_data = tuple(
            (parameter, parameter_display[parameter], get_suitable_widget(value))
            for parameter, value in self.new_tournament.get_parameters().items()
            if value is not None and parameter_display[parameter] is not None
        )

        parameter_widgets = []
        for _, display, widget in self.parameter_widget_data:
            parameter_widgets.extend([get_label(display, "large"), widget, QLabel()])

        widget = QWidget()
        layout = QVBoxLayout()
        get_scroll_area_widgets_and_layouts(layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10)
        widget.setLayout(layout)
        self.splitter.addWidget(widget)

    def create_tournament(self):
        self.new_tournament.set_name(self.name_line.text())
        self.new_tournament.set_participants(self.load_function("", *self.add_participants_window.get_checked_uuids()))
        self.new_tournament.possess_participants()
        if self.add_participants:
            self.new_tournament.seat_participants()
        for parameter, _, widget in self.parameter_widget_data:
            self.new_tournament.set_parameter(parameter, get_value_from_suitable_widget(widget))
        self.new_tournament.set_parameter("category_ranges", self.add_categories_window.get_entries())

        if (self.add_participants and self.new_tournament.is_valid()) or \
                (not self.add_participants and self.new_tournament.is_valid_parameters()):
            self.added_tournament.emit()
            self.close()
        else:
            self.new_tournament.set_participants([])
