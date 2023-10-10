from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter
from PySide6.QtCore import Signal, Qt
from .functions_type import TYPE_TO_MODES, TYPE_TO_MODE_DEFAULT, get_function
from .functions_categories import TYPE_TO_CATEGORIES
from .functions_gui import add_widgets_to_layout, get_button, get_label, get_lineedit, get_combo_box, \
    set_window_title, set_window_size
from .widget_tournament_parameters import Widget_Tournament_Parameters
from .window_choice_table import Window_Choice_Table
from .window_add_categories import Window_Add_Categories


class Window_Tournament_New(QMainWindow):
    added_tournament = Signal()

    def __init__(self, participant_type="player", add_participants=True, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "New Tournament")

        self.add_participants = add_participants
        self.modes = TYPE_TO_MODES[participant_type]
        self.mode_default = TYPE_TO_MODE_DEFAULT[participant_type]
        self.load_function = get_function(participant_type, "load", multiple=True, specification="list")
        self.add_participants_window = Window_Choice_Table("Add Participants", participant_type, parent=self)
        self.categories = TYPE_TO_CATEGORIES[participant_type]
        self.add_categories_window = Window_Add_Categories(self.categories, parent=self)
        self.widget_tournament_parameters = None
        self.new_tournament = None
        self.name_line = None
        self.mode_combo_box = None

        self.widget = QWidget()
        self.layout = QHBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)
        self.set_up_tournament_options()
        self.splitter.addWidget(QWidget())
        self.set_up_parameter_edit()
        set_window_size(self, self.layout.sizeHint())

    def show_participant_window(self):
        self.add_participants_window.size_window()
        self.add_participants_window.show()

    def show_categories_window(self):
        self.add_categories_window.size_window()
        self.add_categories_window.show()

    def set_up_tournament_options(self):
        name_label = get_label("Name", "large", translate=True)
        self.name_line = get_lineedit("medium", (15, 3))
        add_participants_button = get_button(
            "medium", (10, 5), "Add\nParticipants", connect_function=self.show_participant_window, translate=True
        )
        mode_label = get_label("Mode", "large", translate=True)
        self.mode_combo_box = get_combo_box(list(self.modes), "medium", (15, 3), self.mode_default, translate=True)
        add_categories_button = get_button(
            "medium", (10, 5), "Add\nCategories", connect_function=self.show_categories_window, translate=True
        )
        create_button = get_button("large", (11, 4), "Create", connect_function=self.create_tournament, translate=True)

        if not self.add_participants:
            add_participants_button.setVisible(False)
        self.mode_combo_box.currentIndexChanged.connect(self.set_up_parameter_edit)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        add_widgets_to_layout(layout, (name_label, self.name_line))
        add_widgets_to_layout(layout, (QLabel(), add_participants_button))
        add_widgets_to_layout(layout, (QLabel(), mode_label, self.mode_combo_box))
        if len(self.categories) > 0:
            add_widgets_to_layout(layout, (QLabel(), add_categories_button))
        add_widgets_to_layout(layout, (QLabel(), create_button))
        self.splitter.addWidget(widget)

    def set_up_parameter_edit(self):
        self.splitter.widget(1).setParent(None)
        self.new_tournament = self.modes[self.mode_combo_box.currentData()]([], "")
        self.widget_tournament_parameters = Widget_Tournament_Parameters(self.new_tournament, initial=True)
        self.splitter.addWidget(self.widget_tournament_parameters)

    def create_tournament(self):
        self.new_tournament.set_name(self.name_line.text())
        self.new_tournament.set_participants(self.load_function("", self.add_participants_window.get_checked_uuids()))
        self.new_tournament.set_parameter("category_ranges", self.add_categories_window.get_entries())
        valid_parameters = self.widget_tournament_parameters.apply_parameters()

        if valid_parameters and (self.new_tournament.is_valid() or not self.add_participants):
            self.new_tournament.possess_participants()
            if self.add_participants:
                self.new_tournament.seat_participants()
            self.added_tournament.emit()
            self.close()
        else:
            self.new_tournament.set_participants([])
