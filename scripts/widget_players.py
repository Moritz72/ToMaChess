from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidget
from PyQt5.QtCore import Qt
from .class_player import Player
from .functions_player import load_players_all
from .functions_gui import add_content_to_table, add_button_to_table, make_headers_bold_horizontal,\
    make_headers_bold_vertical, add_widgets_in_layout, get_button, clear_table, size_table


class Widget_Players(QWidget):
    def __init__(self):
        super().__init__()
        self.players = load_players_all()
        self.deleted_players = []

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QWidget())
        self.table = QTableWidget()
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        add_widgets_in_layout(self.layout, layout, (self.table,))
        self.set_buttons()

    def add_player_row(self, row, first_name, last_name, rating):
        add_content_to_table(self.table, first_name, row, 0)
        add_content_to_table(self.table, last_name, row, 1, bold=True)
        add_content_to_table(self.table, rating, row, 2, align=Qt.AlignCenter)
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.add_player_to_be_removed)

    def resize_table(self):
        size_table(self.table, len(self.players), 4, 3.5, max_width=55, widths=[None, None, 4.5, 3.5])

    def fill_in_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["First Name", "Last Name", "ELO", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, player in enumerate(self.players):
            self.add_player_row(i, player.get_first_name(), player.get_last_name(), player.get_rating())

    def set_buttons(self):
        add_button = get_button("large", (10, 5), "Add\nPlayer", connect_function=self.add_new_player_row)
        save_button = get_button("large", (10, 5), "Save", connect_function=self.update_players)
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        add_widgets_in_layout(self.layout, layout_buttons, (add_button, save_button))

    def add_new_player_row(self):
        self.players.append(Player(""))
        self.fill_in_table()

    def add_player_to_be_removed(self):
        row = self.table.currentRow()
        if self.players[row].is_valid():
            self.deleted_players.append(self.players[row])
        del self.players[row]
        self.table.removeRow(row)
        self.resize_table()

    def remove_players(self):
        while self.deleted_players:
            self.deleted_players.pop().remove()

    def get_table_text(self, row, column):
        if self.table.item(row, column) is None:
            return ""
        return self.table.item(row, column).text()

    def save_players(self):
        for i, player in enumerate(self.players):
            player.set_first_name(self.get_table_text(i, 0))
            player.set_last_name(self.get_table_text(i, 1))
            try:
                player.set_rating(int(self.get_table_text(i, 2)))
            except (ValueError, AttributeError):
                player.set_rating(0)

            if player.is_valid():
                player.save()

    def update_players(self):
        self.save_players()
        self.remove_players()
        clear_table(self.table)
        self.players = load_players_all()
        self.fill_in_table()
