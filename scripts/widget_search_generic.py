from abc import abstractmethod
from typing import Any, TypeVar, Generic
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer
from .object import Object
from .collection import Collection
from .db_object import DB_Object
from .db_collection import load_collections_by_type
from .table_objects import Table_Objects
from .gui_functions import add_widgets_in_layout, get_lineedit, get_combo_box

T = TypeVar('T', bound=Object)


class Widget_Search_Generic(QWidget, Generic[T]):
    def __init__(
            self, db: DB_Object[T], shallow_load: bool = False, shallow_add: bool = False, shallow_update: bool = False
    ) -> None:
        super().__init__()
        self.db: DB_Object[T] = db
        self.shallow_load: bool = shallow_load
        self.shallow_add: bool = shallow_add
        self.shallow_update: bool = shallow_update
        self.collections: list[Collection] = []
        self.collection_current: Collection | None = None

        if self.db.type != "Collection":
            self.collections = load_collections_by_type("", db.type)
            self.collection_current = self.collections[0]

        self.search_timer: QTimer = QTimer()
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.fill_in_table)

        self.layout_main: QHBoxLayout = QHBoxLayout(self)
        self.layout_main.addWidget(QWidget())
        self.table: Table_Objects[T] = self.get_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        add_widgets_in_layout(self.layout_main, layout, [self.table])

        self.search_bar = get_lineedit("medium", (14, 3))
        self.search_bar.textChanged.connect(self.reset_timer)
        widgets = [self.search_bar, *self.get_buttons()]
        if db.type != "Collection":
            collection_box = get_combo_box([collection.get_name() for collection in self.collections], "large", (14, 3))
            collection_box.currentIndexChanged.connect(self.change_collection)
            widgets = [collection_box] + widgets
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        add_widgets_in_layout(self.layout_main, layout, widgets)

        self.fill_in_table()

    @staticmethod
    @abstractmethod
    def get_table() -> Table_Objects[T]:
        pass

    @abstractmethod
    def get_buttons(self) -> list[QPushButton]:
        pass

    @abstractmethod
    def fill_in_row(self, row: int, obj: T | None = None) -> None:
        pass

    def search_objects(self) -> list[T]:
        return self.db.load_like("", self.get_collection_uuid(), self.search_bar.text(), 500, shallow=self.shallow_load)

    def fill_in_table(self) -> None:
        objects = self.search_objects()
        self.table.set_objects(objects)
        for i, obj in enumerate(objects):
            self.fill_in_row(i, obj)
        self.table.reset_changes()

    def change_collection(self, i: int) -> None:
        self.collection_current = self.collections[i]
        self.fill_in_table()

    def reset_timer(self) -> None:
        self.search_timer.stop()
        self.search_timer.start()

    def add_new_row(self) -> None:
        self.table.add_row()
        self.fill_in_row(0)

    def get_collection_uuid(self) -> str:
        if self.collection_current is None:
            return NotImplemented
        return self.collection_current.get_uuid()

    @abstractmethod
    def get_object_from_values(self, values: tuple[Any, ...]) -> T:
        pass

    @abstractmethod
    def edit_object_by_values(self, values: tuple[Any, ...], obj: T) -> None:
        pass

    def update_database(self) -> None:
        objects_update, objects_remove, objects_update_values, objects_add_values = self.table.retrieve_changes()
        for values, obj in zip(objects_update_values, objects_update):
            self.edit_object_by_values(values, obj)
        objects_update = [obj for obj in objects_update if obj.is_valid()]
        objects_add = [self.get_object_from_values(values) for values in objects_add_values]
        objects_add = [obj for obj in objects_add if obj.is_valid()]

        if objects_add:
            self.db.add_list("", objects_add, shallow=self.shallow_add)
        if objects_update:
            self.db.update_list("", objects_update, shallow=self.shallow_update)
        if objects_remove:
            self.db.remove_list("", objects_remove)
        self.fill_in_table()
