from abc import abstractmethod
from typing import Generic, TypeVar
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QSplitter, QVBoxLayout, QWidget
from .window_add_categories import Window_Add_Categories
from .window_choice_objects import Window_Choice_Objects, Window_Choice_Players, Window_Choice_Teams
from ..common.gui_functions import add_widgets_to_layout, get_button, get_combo_box, get_label, get_lineedit, \
    set_window_size, set_window_title
from ..widgets.widget_tournament_parameters import Widget_Tournament_Parameters
from ...tournament.registries.tournament_registry import TEAM_TOURNAMENT_REGISTRY, TOURNAMENT_REGISTRY
from ...tournament.utils.functions_tournament_get import get_blank_tournament
from ...player.player import Player
from ...team.team import Team
from ...tournament.common.category_range import CATEGORIES_PLAYER, CATEGORIES_TEAM
from ...tournament.tournaments.tournament import Participant, Tournament

T = TypeVar('T', bound=Participant)


class Window_Tournament_New_Generic(QMainWindow, Generic[T]):
    added_tournament = Signal()

    def __init__(
            self, modes: list[str], mode_default: str, categories: list[str], add_participants: bool = True,
            parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "New Tournament")

        self.add_participants: bool = add_participants
        self.modes: list[str] = modes
        self.mode_default: str = mode_default
        self.add_participants_window: Window_Choice_Objects[T] = self.get_add_participants_window()
        self.categories: list[str] = categories
        self.add_categories_window: Window_Add_Categories = Window_Add_Categories(self.categories, parent=self)
        self.widget_tournament_parameters: Widget_Tournament_Parameters | None = None
        self.new_tournament: Tournament | None = None
        self.name_line: QLineEdit | None = None
        self.mode_combo_box: QComboBox | None = None

        self.widget = QWidget()
        self.layout_main: QHBoxLayout = QHBoxLayout(self.widget)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        self.splitter: QSplitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layout_main.addWidget(self.splitter)
        self.set_up_tournament_options()
        self.splitter.addWidget(QWidget())
        self.set_up_parameter_edit()
        set_window_size(self, self.layout_main.sizeHint())

    def show_participant_window(self) -> None:
        self.add_participants_window.size_window()
        self.add_participants_window.show()

    def show_categories_window(self) -> None:
        self.add_categories_window.size_window()
        self.add_categories_window.show()

    def set_up_tournament_options(self) -> None:
        name_label = get_label("Name", "large", translate=True)
        self.name_line = get_lineedit("medium", (15, 3))
        add_participants_button = get_button(
            "medium", (10, 5), "Add\nParticipants", connect=self.show_participant_window, translate=True
        )
        mode_label = get_label("Mode", "large", translate=True)
        self.mode_combo_box = get_combo_box(
            self.modes, "medium", (15, 3), current=self.mode_default, translate=True
        )
        add_categories_button = get_button(
            "medium", (10, 5), "Add\nCategories", connect=self.show_categories_window, translate=True
        )
        create_button = get_button("large", (11, 4), "Create", connect=self.create_tournament, translate=True)

        if not self.add_participants:
            add_participants_button.setVisible(False)
        self.mode_combo_box.currentIndexChanged.connect(self.set_up_parameter_edit)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 60, 20)
        layout.setSpacing(10)
        add_widgets_to_layout(layout, [name_label, self.name_line])
        add_widgets_to_layout(layout, [QLabel(), add_participants_button])
        add_widgets_to_layout(layout, [QLabel(), mode_label, self.mode_combo_box])
        if len(self.categories) > 0:
            add_widgets_to_layout(layout, [QLabel(), add_categories_button])
        add_widgets_to_layout(layout, [QLabel(), create_button])
        self.splitter.addWidget(widget)

    def set_up_parameter_edit(self) -> None:
        assert(self.mode_combo_box is not None)
        self.splitter.widget(1).deleteLater()
        self.new_tournament = get_blank_tournament(self.mode_combo_box.currentData())
        self.widget_tournament_parameters = Widget_Tournament_Parameters(self.new_tournament, initial=True)
        self.splitter.addWidget(self.widget_tournament_parameters)

    def create_tournament(self) -> None:
        assert(self.new_tournament is not None and self.name_line is not None)
        self.new_tournament.set_name(self.name_line.text())
        self.new_tournament.set_participants(self.add_participants_window.get_checked_objects())
        self.new_tournament.set_category_ranges(self.add_categories_window.get_category_ranges())
        assert(self.widget_tournament_parameters is not None)
        valid_parameters = self.widget_tournament_parameters.apply_parameters()

        if valid_parameters and (self.new_tournament.is_valid() or not self.add_participants):
            self.new_tournament.possess_participants()
            if self.add_participants:
                self.new_tournament.seed_participants()
            self.added_tournament.emit()
            self.close()
        else:
            self.new_tournament.set_participants([])

    @abstractmethod
    def get_add_participants_window(self) -> Window_Choice_Objects[T]:
        pass


class Window_Tournament_New_Player(Window_Tournament_New_Generic[Player]):
    def __init__(self, add_participants: bool = True, parent: QWidget | None = None):
        super().__init__(
            TOURNAMENT_REGISTRY.get_modes(), TOURNAMENT_REGISTRY.get_mode_default(),
            CATEGORIES_PLAYER, add_participants, parent
        )

    def get_add_participants_window(self) -> Window_Choice_Objects[Player]:
        return Window_Choice_Players("Add Participants", parent=self)


class Window_Tournament_New_Team(Window_Tournament_New_Generic[Team]):
    def __init__(self, add_participants: bool = True, parent: QWidget | None = None):
        super().__init__(
            TEAM_TOURNAMENT_REGISTRY.get_modes(), TEAM_TOURNAMENT_REGISTRY.get_mode_default(),
            CATEGORIES_TEAM, add_participants, parent
        )

    def get_add_participants_window(self) -> Window_Choice_Objects[Team]:
        return Window_Choice_Teams("Add Participants", parent=self)
