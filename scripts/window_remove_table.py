from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidget, QHeaderView
from PySide6.QtCore import Qt, Signal, QSize
from .functions_player import PLAYER_ATTRIBUTE_LIST
from .functions_team import TEAM_ATTRIBUTE_LIST
from .functions_gui import set_up_table, size_table, add_button_to_table, set_window_title, set_window_size, \
    add_player_to_table, add_team_to_table


class Widget_Remove_Players(QTableWidget):
    def __init__(self, objects):
        super().__init__()
        self.objects = objects
        self.removed_objects = []
        self.fill_in_table()

    def add_row(self, row, obj):
        add_player_to_table(self, row, obj)
        add_button_to_table(self, row, 6, "medium", None, '-', connect_function=self.add_member_to_be_removed)

    def resize_table(self):
        size_table(self, len(self.objects), 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])

    def fill_in_table(self):
        set_up_table(self, 0, 7, header_horizontal=PLAYER_ATTRIBUTE_LIST + [""], translate=True)
        self.resize_table()

        header_horizontal, header_vertical = self.horizontalHeader(), self.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, obj in enumerate(self.objects):
            self.add_row(i, obj)

    def add_member_to_be_removed(self):
        row = self.currentRow()
        self.removed_objects.append(self.objects[row])
        del self.objects[row]
        self.removeRow(row)
        self.resize_table()


class Widget_Remove_Teams(QTableWidget):
    def __init__(self, objects):
        super().__init__()
        self.objects = objects
        self.removed_objects = []
        self.fill_in_table()

    def add_row(self, row, obj):
        add_team_to_table(self, row, obj)
        add_button_to_table(self, row, 2, "medium", None, '-', connect_function=self.add_member_to_be_removed)

    def resize_table(self):
        size_table(self, len(self.objects), 3.5, max_width=55, widths=[None, 5, 3.5])

    def fill_in_table(self):
        set_up_table(self, 0, 3, header_horizontal=TEAM_ATTRIBUTE_LIST + [""], translate=True)
        self.resize_table()

        header_horizontal, header_vertical = self.horizontalHeader(), self.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, obj in enumerate(self.objects):
            self.add_row(i, obj)

    def add_member_to_be_removed(self):
        row = self.currentRow()
        self.removed_objects.append(self.objects[row])
        del self.objects[row]
        self.removeRow(row)
        self.resize_table()


TYPE_TO_WIDGET = {"player": Widget_Remove_Players, "team": Widget_Remove_Teams}


class Window_Remove_Table(QMainWindow):
    window_closed = Signal()

    def __init__(self, title, object_type, objects, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, title)

        self.table = TYPE_TO_WIDGET[object_type](objects)
        self.setCentralWidget(self.table)

        set_window_size(self, QSize(self.table.maximumWidth(), int(QApplication.primaryScreen().size().height() * .8)))

    def get_removed_objects(self):
        return self.table.removed_objects

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
