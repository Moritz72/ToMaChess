from PyQt5.QtWidgets import QTableWidget
from .functions_gui import size_table, get_value_from_suitable_widget


class Table_Widget_Search(QTableWidget):
    def __init__(self, columns, row_height, max_width, widths):
        super().__init__()
        self.objects = []
        self.row_height = row_height
        self.max_width = max_width
        self.widths = widths
        self.updated_objects_dict = dict()
        self.deleted_objects = []
        self.setColumnCount(columns)

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
        if obj is not None:
            self.updated_objects_dict[id(obj)] = [
                self.get_table_value(row, column) for column in range(self.columnCount())
            ]

    def resize_table(self):
        size_table(
            self, len(self.objects), self.columnCount(), self.row_height, max_width=self.max_width, widths=self.widths
        )

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

    def get_table_value(self, row, column):
        if self.cellWidget(row, column) is not None:
            return get_value_from_suitable_widget(self.cellWidget(row, column))
        if self.item(row, column) is None:
            return ""
        return self.item(row, column).text()

    def retrieve_changes(self):
        new_objects_count = self.objects.count(None)
        return tuple(obj for obj in self.objects if id(obj) in self.updated_objects_dict),\
            tuple(self.deleted_objects),\
            tuple(values for ids, values in self.updated_objects_dict.items()),\
            tuple(
                [self.get_table_value(row, column) for column in range(self.columnCount())]
                for row in range(self.rowCount() - new_objects_count, self.rowCount())
            )
