from abc import abstractmethod
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from .functions_collection import load_collections
from .functions_gui import add_widgets_in_layout, get_lineedit, get_combo_box


class Widget_Default_Generic(QWidget):
    def __init__(self, object_type, load_like_function, update_function, remove_function, add_function):
        super().__init__()
        self.load_like_function = load_like_function
        self.update_function = update_function
        self.remove_function = remove_function
        self.add_function = add_function

        if object_type is None:
            self.collections = None
            self.collection_current = None
        else:
            self.collections = load_collections("", object_type)
            self.collection_current = self.collections[0]
        self.search_timer = QTimer()
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.fill_in_table)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QWidget())
        self.table = self.get_table()
        self.search_bar = None
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        add_widgets_in_layout(self.layout, layout, (self.table,))

        self.search_bar = get_lineedit("medium", (12, 3))
        self.search_bar.textChanged.connect(self.reset_timer)
        widgets = [self.search_bar, *self.get_buttons()]
        if object_type is not None:
            collection_box = get_combo_box([collection.get_name() for collection in self.collections], "large", (12, 3))
            collection_box.currentIndexChanged.connect(self.change_collection)
            widgets = [collection_box] + widgets
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        add_widgets_in_layout(self.layout, layout, widgets)

        self.fill_in_table()

    @staticmethod
    @abstractmethod
    def get_table():
        pass

    @abstractmethod
    def get_buttons(self):
        pass

    @abstractmethod
    def fill_in_row(self, row, obj=None):
        pass

    def fill_in_table(self):
        if self.collections is None:
            objects = self.load_like_function("", self.search_bar.text(), 200)
        else:
            objects = self.load_like_function("", self.collection_current.get_uuid(), self.search_bar.text(), 200)
        self.table.set_objects(objects)
        for i, obj in enumerate(objects):
            self.fill_in_row(i, obj)
        self.table.reset_changes()

    def change_collection(self, i):
        self.collection_current = self.collections[i]
        self.fill_in_table()

    def reset_timer(self):
        self.search_timer.stop()
        self.search_timer.start()

    def add_new_row(self):
        self.table.add_row()
        self.fill_in_row(self.table.rowCount() - 1)

    @abstractmethod
    def get_object_from_values(self, values):
        pass

    @abstractmethod
    def edit_object_by_values(self, values, obj):
        pass

    def update_database(self):
        objects_update, objects_remove, objects_update_values, objects_add_values = self.table.retrieve_changes()
        for values, player in zip(objects_update_values, objects_update):
            self.edit_object_by_values(values, player)
        objects_update = tuple(obj for obj in objects_update if obj.is_valid())
        objects_add = tuple(self.get_object_from_values(values) for values in objects_add_values)
        objects_add = tuple(obj for obj in objects_add if obj.is_valid())
        if objects_update:
            self.update_function("", objects_update)
        if objects_remove:
            self.remove_function("", objects_remove)
        if objects_add:
            self.add_function("", objects_add)
        self.fill_in_table()
