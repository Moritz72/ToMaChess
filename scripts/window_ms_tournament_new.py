from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from .class_ms_tournament import MS_Tournament
from .widget_ms_tournament_stage_new import Widget_MS_Tournament_Stage_New
from .functions_gui import get_button, get_scroll_area_widgets_and_layouts, add_widgets_in_layout, get_lineedit,\
    get_label


class Window_MS_Tournament_New(QMainWindow):
    added_tournament = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Multi Stage Tournament")
        self.name_line = None
        self.new_tournament = None

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.add_name_line()
        _, _, self.layout_inner = get_scroll_area_widgets_and_layouts(self.layout, [])
        self.add_buttons()
        self.add_stage()
        self.add_stage()

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.setFixedWidth(int(QApplication.primaryScreen().size().height()*.8))
        self.setFixedHeight(int(QApplication.primaryScreen().size().height()*.8))

    def add_name_line(self):
        label = get_label("Name", "large")
        self.name_line = get_lineedit("medium", (15, 2.5))
        layout = QHBoxLayout()
        layout.addStretch()
        add_widgets_in_layout(self.layout, layout, (label, self.name_line))
        layout.addStretch()

    def add_buttons(self):
        add_widgets_in_layout(self.layout, QHBoxLayout(), (
            get_button("large", None, "Add\nStage", connect_function=self.add_stage),
            get_button("large", None, "Remove\nStage", connect_function=self.remove_stage),
            get_button("large", None, "Create\nTournament", connect_function=self.create_tournament)
        ))

    def add_stage(self):
        stage = self.layout_inner.count()
        widget = Widget_MS_Tournament_Stage_New(stage, self)
        self.layout_inner.addWidget(widget)
        widget.update_necessary.connect(self.validate_advance_lists_signal)

    def remove_stage(self):
        if self.layout_inner.count() != 0:
            self.layout_inner.takeAt(self.layout_inner.count()-1).widget().setParent(None)

    def create_tournament(self):
        self.new_tournament = MS_Tournament(self.name_line.text(), [], [])
        for i in range(self.layout_inner.count()):
            stage_tounaments = self.layout_inner.itemAt(i).widget().tournaments
            self.new_tournament.add_stage_tournaments(stage_tounaments)
            if i == 0:
                continue

            stage_advance_lists = [
                [
                    (self.new_tournament.stages_tournaments[-2].index(tournament), placement)
                    for tournament, placement in advance_list
                ]
                for advance_list in self.layout_inner.itemAt(i).widget().advance_lists
            ]
            self.new_tournament.add_stage_advance_lists(stage_advance_lists)

        if self.new_tournament.is_valid():
            for tournament in self.new_tournament.get_current_tournaments():
                tournament.seat_participants()
            self.new_tournament.save()
            self.added_tournament.emit()
            self.close()

    def get_stage_widget(self, stage):
        return self.layout_inner.itemAt(stage).widget()

    def validate_advance_lists_signal(self):
        for i in range(1, self.layout_inner.count()):
            self.layout_inner.itemAt(i).widget().validate_advance_lists()
