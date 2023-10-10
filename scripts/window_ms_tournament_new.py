from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QSize
from .class_ms_tournament import MS_Tournament
from .widget_ms_tournament_stage_new import Widget_MS_Tournament_Stage_New
from .functions_gui import get_button, get_scroll_area_widgets_and_layouts, add_widgets_in_layout, get_lineedit,\
    get_label, get_check_box, add_widgets_to_layout, set_window_title, set_window_size


class Window_MS_Tournament_New(QMainWindow):
    added_tournament = Signal()

    def __init__(self, participant_type="player", parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "New Multi-Stage Tournament")

        self.participant_type = participant_type
        self.name_line = None
        self.draw_lots_check = None
        self.new_tournament = None

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.add_top_line()
        _, _, self.layout_inner = get_scroll_area_widgets_and_layouts(self.layout, [])
        self.add_buttons()
        self.add_stage()
        self.add_stage()

        set_window_size(self, QSize(
            int(QApplication.primaryScreen().size().height() * .8),
            int(QApplication.primaryScreen().size().height() * .8)
        ))

    def add_top_line(self):
        name_label = get_label("Name", "large", translate=True)
        self.name_line = get_lineedit("medium", (15, 2.5))
        draw_lots_label = get_label("Draw Lots in Case of Tie", "large", translate=True)
        self.draw_lots_check = get_check_box(True, "medium", (2.5, 2.5))

        layout = QHBoxLayout()
        layout.addStretch()
        add_widgets_to_layout(layout, (name_label, self.name_line))
        layout.addStretch()
        add_widgets_to_layout(layout, (draw_lots_label, self.draw_lots_check))
        layout.addStretch()
        self.layout.addLayout(layout)

    def add_buttons(self):
        add_widgets_in_layout(self.layout, QHBoxLayout(), (
            get_button("large", None, "Add\nStage", connect_function=self.add_stage, translate=True),
            get_button("large", None, "Remove\nStage", connect_function=self.remove_stage, translate=True),
            get_button("large", None, "Create\nTournament", connect_function=self.create_tournament, translate=True)
        ))

    def add_stage(self):
        stage = self.layout_inner.count()
        widget = Widget_MS_Tournament_Stage_New(stage, participant_type=self.participant_type)
        self.layout_inner.addWidget(widget)
        widget.update_necessary.connect(self.validate_advance_lists_signal)

    def remove_stage(self):
        if self.layout_inner.count() != 0:
            self.layout_inner.takeAt(self.layout_inner.count() - 1).widget().setParent(None)

    def get_stage_tournaments(self, i):
        return self.layout_inner.itemAt(i).widget().tournaments

    def get_stage_advance_lists(self, i):
        return self.layout_inner.itemAt(i).widget().advance_lists

    def create_tournament(self):
        stages_tournaments = [self.get_stage_tournaments(i) for i in range(self.layout_inner.count())]
        stages_advance_lists = [
            [
                [(stages_tournaments[-2].index(tournament), placement) for tournament, placement in advance_list]
                for advance_list in self.get_stage_advance_lists(i)
            ]
            for i in range(1, self.layout_inner.count())
        ]

        self.new_tournament = MS_Tournament(
            stages_tournaments, self.name_line.text(),
            stages_advance_lists=stages_advance_lists, draw_lots=self.draw_lots_check.checkState() == Qt.Checked
        )

        if self.new_tournament.is_valid():
            self.new_tournament.possess_participants_and_tournaments()
            for tournament in self.new_tournament.get_current_tournaments():
                tournament.seat_participants()
            self.added_tournament.emit()
            self.close()

    def get_stage_widget(self, stage):
        return self.layout_inner.itemAt(stage).widget()

    def validate_advance_lists_signal(self):
        for i in range(1, self.layout_inner.count()):
            self.layout_inner.itemAt(i).widget().validate_advance_lists()
