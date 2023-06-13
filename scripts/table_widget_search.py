from PyQt5.QtWidgets import QTableWidget
from .functions_gui import set_up_table, size_table, get_table_value


class Table_Widget_Search(QTableWidget):
    def __init__(self, columns, row_height, max_width, widths, header_horizontal, translate=False):
        super().__init__()
        self.objects = []
        self.row_height = row_height
        self.max_width = max_width
        self.widths = widths
        self.updated_objects_dict = dict()
        self.deleted_objects = []
        set_up_table(self, 0, columns, header_horizontal=header_horizontal, translate=translate)

    def set_objects(self, objects):
        self.objects = objects
        self.resize_table()

    def reset_changes(self):
        self.updated_objects_dict = dict()
        self.deleted_objects = []
        self.itemChanged.connect(self.item_updated)

    def item_updated(self, item):
        self.mark_object_as_updated(item.row())

    def mark_object_as_updated(self, row):
        obj = self.objects[row]
        if obj is None:
            return
        self.updated_objects_dict[id(obj)] = [
            get_table_value(self, row, column) for column in range(self.columnCount())
        ]

    def resize_table(self):
        size_table(self, len(self.objects), self.row_height, max_width=self.max_width, widths=self.widths)

    def delete_current_row(self):
        row = self.currentRow()
        obj = self.objects.pop(row)
        if obj is not None:
            self.deleted_objects.append(obj)
        self.removeRow(row)
        self.resize_table()

    def add_row(self):
        self.insertRow(self.rowCount())
        self.objects.append(None)
        self.resize_table()

    def retrieve_changes(self):
        new_objects_count = self.objects.count(None)
        return tuple(obj for obj in self.objects if id(obj) in self.updated_objects_dict),\
            tuple(self.deleted_objects),\
            tuple(values for ids, values in self.updated_objects_dict.items()),\
            tuple(
                [get_table_value(self, row, column) for column in range(self.columnCount())]
                for row in range(self.rowCount() - new_objects_count, self.rowCount())
            )
