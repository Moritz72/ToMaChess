from PyQt5.QtWidgets import QMainWindow, QHeaderView, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_player import load_players_like
from .functions_team import load_teams_like_shallow
from .functions_gui import add_content_to_table, make_headers_bold_horizontal, make_headers_bold_vertical,\
    get_check_box


def get_load_function_exclude(load_like_function, excluded_uuids):
    def function(*args):
        res = load_like_function(*args)
        return [obj for obj in res if (obj.get_uuid(), obj.get_uuid_associate()) not in excluded_uuids]
    return function


class Widget_Choice_Players(Widget_Default_Generic):
    def __init__(self, excluded_uuids, checked_uuids):
        self.checked_uuids = set(checked_uuids)
        super().__init__("Players", get_load_function_exclude(load_players_like, excluded_uuids), None, None, None)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(7, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Sex", "Birth", "Fed.", "Title", "Rating", ""])
        make_headers_bold_horizontal(table)
        make_headers_bold_vertical(table)

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
        add_content_to_table(self.table, obj.get_name(), row, 0, edit=False, bold=True)
        add_content_to_table(self.table, obj.get_sex(), row, 1, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_birthday(), row, 2, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_country(), row, 3, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_title(), row, 4, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_rating(), row, 5, edit=False, align=Qt.AlignCenter)
        check_box = get_check_box((obj.get_uuid(), obj.get_uuid_associate()) in self.checked_uuids, (3.5, 3.5))
        check_box.stateChanged.connect(self.check_box_clicked)
        self.table.setCellWidget(row, 6, check_box)

    def check_box_clicked(self, state):
        obj = self.table.objects[self.table.currentRow()]
        if state == Qt.Checked:
            self.checked_uuids.add((obj.get_uuid(), obj.get_uuid_associate()))
        else:
            self.checked_uuids.remove((obj.get_uuid(), obj.get_uuid_associate()))


class Widget_Choice_Teams(Widget_Default_Generic):
    def __init__(self, excluded_uuids, checked_uuids):
        self.checked_uuids = set(checked_uuids)
        super().__init__("Teams", get_load_function_exclude(load_teams_like_shallow, excluded_uuids), None, None, None)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(3, 3.5, 55, [None, 5, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Memb.", ""])
        make_headers_bold_horizontal(table)
        make_headers_bold_vertical(table)

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
        add_content_to_table(self.table, obj.get_name(), row, 0, bold=False)
        add_content_to_table(self.table, obj.get_member_count(), row, 1, edit=False, align=Qt.AlignCenter)
        check_box = get_check_box((obj.get_uuid(), obj.get_uuid_associate()) in self.checked_uuids, (3.5, 3.5))
        check_box.stateChanged.connect(self.check_box_clicked)
        self.table.setCellWidget(row, 2, check_box)

    def check_box_clicked(self, state):
        obj = self.table.objects[self.table.currentRow()]
        if state == Qt.Checked:
            self.checked_uuids.add((obj.get_uuid(), obj.get_uuid_associate()))
        else:
            self.checked_uuids.remove((obj.get_uuid(), obj.get_uuid_associate()))


type_to_widget = {"Players": Widget_Choice_Players, "Teams": Widget_Choice_Teams}


class Window_Choice_Table(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, title, object_type, excluded_uuids=None, checked_uuids=None):
        super().__init__()
        self.setWindowTitle(title)

        excluded_uuids = excluded_uuids or []
        checked_uuids = checked_uuids or []

        self.widget = type_to_widget[object_type](excluded_uuids, checked_uuids)
        self.setCentralWidget(self.widget)

        self.setFixedWidth(self.widget.table.maximumWidth() + 120)
        self.setFixedHeight(int(QApplication.primaryScreen().size().height() * .8))

    def get_checked_uuids(self):
        return [uuid for uuid, _ in self.widget.checked_uuids],\
               [uuid_associate for _, uuid_associate in self.widget.checked_uuids]

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
