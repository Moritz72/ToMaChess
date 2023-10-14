from PySide6.QtWidgets import QMainWindow, QHeaderView
from PySide6.QtCore import Qt, Signal, QSize
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_player import load_players_like, PLAYER_ATTRIBUTE_LIST
from .functions_team import load_teams_shallow_like, TEAM_ATTRIBUTE_LIST
from .functions_gui import get_check_box, set_window_title, set_window_size, add_player_to_table, add_team_to_table


def get_load_function_exclude(load_like_function, excluded_uuids):
    def function(*args):
        res = load_like_function(*args)
        return [obj for obj in res if obj.get_uuid() not in excluded_uuids]
    return function


class Widget_Choice_Players(Widget_Default_Generic):
    def __init__(self, excluded_uuids, checked_uuids):
        self.checked_uuids = checked_uuids
        super().__init__("Players", get_load_function_exclude(load_players_like, excluded_uuids), None, None, None)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(
            7, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5], PLAYER_ATTRIBUTE_LIST + [""], translate=True
        )

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        return ()

    def get_object_from_values(self, values):
        return

    def edit_object_by_values(self, values, obj):
        return

    def fill_in_row(self, row, obj=None):
        add_player_to_table(self.table, row, obj)
        check_box = get_check_box(obj.get_uuid() in self.checked_uuids, "medium", (3.5, 3.5))
        check_box.stateChanged.connect(self.check_box_clicked)
        self.table.setCellWidget(row, 6, check_box)

    def check_box_clicked(self, state):
        obj = self.table.objects[self.table.currentRow()]
        if state == 2:
            self.checked_uuids.add(obj.get_uuid())
        else:
            self.checked_uuids.remove(obj.get_uuid())


class Widget_Choice_Teams(Widget_Default_Generic):
    def __init__(self, excluded_uuids, checked_uuids):
        self.checked_uuids = checked_uuids
        super().__init__("Teams", get_load_function_exclude(load_teams_shallow_like, excluded_uuids), None, None, None)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(3, 3.5, 55, [None, 5, 3.5], TEAM_ATTRIBUTE_LIST + [""], translate=True)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        return ()

    def get_object_from_values(self, values):
        return

    def edit_object_by_values(self, values, obj):
        return

    def fill_in_row(self, row, obj=None):
        add_team_to_table(self.table, row, obj)
        check_box = get_check_box(obj.get_uuid() in self.checked_uuids, "medium", (3.5, 3.5))
        check_box.stateChanged.connect(self.check_box_clicked)
        self.table.setCellWidget(row, 2, check_box)

    def check_box_clicked(self, state):
        obj = self.table.objects[self.table.currentRow()]
        if state == 2:
            self.checked_uuids.add(obj.get_uuid())
        else:
            self.checked_uuids.remove(obj.get_uuid())


TYPE_TO_WIDGET = {"player": Widget_Choice_Players, "team": Widget_Choice_Teams}


class Window_Choice_Table(QMainWindow):
    window_closed = Signal()

    def __init__(self, title, object_type, excluded_uuids=None, checked_uuids=None, parent=None):
        super().__init__(parent=parent)
        set_window_title(self, title)

        excluded_uuids = excluded_uuids or set()
        checked_uuids = checked_uuids or set()

        self.widget = TYPE_TO_WIDGET[object_type](excluded_uuids, checked_uuids)
        self.setCentralWidget(self.widget)
        self.size_window()

    def size_window(self):
        set_window_size(self, QSize(self.widget.table.maximumWidth() + 120, 0), factor_y=.8)

    def get_checked_uuids(self):
        return self.widget.checked_uuids

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
