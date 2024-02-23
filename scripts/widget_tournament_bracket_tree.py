from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QTableWidget, QWidget
from PySide6.QtCore import Qt
from .bracket_tree import Bracket_Tree_Node
from .tournament import Tournament
from .widget_tournament_info import Widget_Tournament_Info
from .gui_classes import Turn_Widget, Line_Widget
from .gui_functions import set_fixed_size, get_scroll_area_widgets_and_layouts
from .gui_table import set_up_table, size_table, add_label_to_table


class Widget_Tournament_Bracket_Tree(Widget_Tournament_Info):
    def __init__(self, tournament: Tournament) -> None:
        super().__init__("Bracket Tree", tournament)
        self.layout_main = QVBoxLayout(self)
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
        self.grid.setSpacing(0)
        self.grid.setRowStretch(0, 1)
        get_scroll_area_widgets_and_layouts(self.layout_main, layout_inner=self.grid, horizontal_bar=True)
        self.make_bracket_tree()

    def add_bracket(self, node: Bracket_Tree_Node, score_length: int, row: int, column: int) -> None:
        participant_dict = self.tournament.get_uuid_to_participant_dict()
        names = [
            "" if item is None else "bye" if item.is_bye() else participant_dict[item].get_name() for item in node.items
        ]
        align_left, align_center = Qt.AlignmentFlag.AlignLeft, Qt.AlignmentFlag.AlignCenter
        match node.winner:
            case False:
                obj_name_1, obj_name_2 = "bracket_winner", "bracket_loser"
            case True:
                obj_name_1, obj_name_2 = "bracket_loser", "bracket_winner"
            case _:
                obj_name_1, obj_name_2 = "bracket", "bracket"
        obj_name_names_1, obj_name_names_2 = f"{obj_name_1}_name", f"{obj_name_2}_name"
        obj_name_blank_1, obj_name_blank_2 = f"{obj_name_1}_blank", f"{obj_name_2}_blank"

        bracket = QTableWidget()
        set_up_table(bracket, 2, score_length + 1)
        size_table(bracket, row_height=2, widths=[15] + score_length * [2], header_width=0, header_height=0)
        bracket.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        add_label_to_table(bracket, 0, 0, text=names[0], align=align_left, bold=True, object_name=obj_name_names_1)
        add_label_to_table(bracket, 1, 0, text=names[1], align=align_left, bold=True, object_name=obj_name_names_2)
        for i, (score_1, score_2) in enumerate(node.scores):
            add_label_to_table(bracket, 0, i + 1, text=score_1, align=align_center, bold=True, object_name=obj_name_1)
            add_label_to_table(bracket, 1, i + 1, text=score_2, align=align_center, bold=True, object_name=obj_name_2)
        for i in range(len(node.scores), score_length):
            add_label_to_table(bracket, 0, i + 1, align=align_center, bold=True, object_name=obj_name_blank_1)
            add_label_to_table(bracket, 1, i + 1, align=align_center, bold=True, object_name=obj_name_blank_2)

        bracket.setFixedSize(bracket.maximumSize())
        if all(item is not None and item.is_bye() for item in node.items):
            size_policy = bracket.sizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            bracket.setSizePolicy(size_policy)
            bracket.hide()
        self.grid.addWidget(bracket, row, column)

    def add_fork_part(self, fork_size: int, upper: bool, row: int, column: int) -> None:
        widgets: list[QWidget] = [Line_Widget(1) for _ in range(fork_size // 2 - 1)]
        widgets.insert(0, Turn_Widget(1 if upper else 2))
        widgets.append(Turn_Widget(-1 if upper else 0))
        for i, widget in enumerate(widgets):
            set_fixed_size(widget, (4, None))
            self.grid.addWidget(widget, row - i if upper else row + i, column)

    def add_straight_line(self, row: int, column: int) -> None:
        line = Line_Widget()
        set_fixed_size(line, (4, None))
        self.grid.addWidget(line, row, column)

    def make_bracket_tree(self) -> None:
        root = self.tournament.get_bracket_tree().root
        depth = root.get_depth()
        widths = root.get_widths()
        max_score_lengths = root.get_max_score_lengths()
        self.grid.setRowStretch(2 * max(widths), 1)
        cell_dict = {root: (max(widths), 2 * depth - 1)}
        cell_dict_new = dict()

        self.add_bracket(root, max_score_lengths[0], *cell_dict[root])
        for i in range(len(widths)):
            fork_size = max(widths[i:]) // widths[i] + 1
            no_siblings = all(node.get_n_children() < 2 for node in cell_dict)
            for node, (row, column) in cell_dict.items():
                for j, (child, connection) in enumerate(zip(node.children, node.connections)):
                    if child is None:
                        continue
                    if no_siblings:
                        row_child = row
                        if connection:
                            self.add_straight_line(row, column - 1)
                    elif j == 0:
                        row_child = row - fork_size // 2
                        if connection:
                            self.add_fork_part(fork_size, True, row, column - 1)
                    else:
                        row_child = row + fork_size // 2
                        if connection:
                            self.add_fork_part(fork_size, False, row, column - 1)
                    self.add_bracket(child, max_score_lengths[i + 1], row_child, column - 2)
                    cell_dict_new[child] = (row_child, column - 2)
            cell_dict, cell_dict_new = cell_dict_new, dict()

    def refresh(self) -> None:
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().deleteLater()
        self.make_bracket_tree()
