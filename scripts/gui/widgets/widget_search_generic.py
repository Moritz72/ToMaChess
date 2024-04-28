from abc import abstractmethod
from typing import Any, TypeVar, Generic
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from ..common.gui_functions import add_widgets_in_layout, get_combo_box, get_lineedit
from ..common.gui_search import Search_Bar
from ..tables.table_objects import Table_Objects
from ...common.object import Object
from ...database.db_collection import load_collections_by_type
from ...database.db_object import DB_Object

T = TypeVar('T', bound=Object)


class Widget_Search_Generic(QWidget, Generic[T]):
    def __init__(
            self, db: DB_Object[T], table_root: str = "", associates: list[tuple[str, str]] | None = None,
            shallow_load: bool = False, shallow_add: bool = False, shallow_update: bool = False
    ) -> None:
        super().__init__()
        self.db: DB_Object[T] = db
        self.table_root: str = table_root
        self.associates: list[tuple[str, str]] | None = associates
        self.shallow_load: bool = shallow_load
        self.shallow_add: bool = shallow_add
        self.shallow_update: bool = shallow_update
        self.associates_index: int = 0

        if self.associates is None and db.type != "Collection":
            self.associates = [
                (collection.get_name(), collection.get_uuid())
                for collection in load_collections_by_type(self.table_root, db.type)
            ]

        self.layout_main: QHBoxLayout = QHBoxLayout(self)
        self.layout_main.addWidget(QWidget())
        self.table: Table_Objects[T] = self.get_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        add_widgets_in_layout(self.layout_main, layout, [self.table])

        self.search_bar: Search_Bar = Search_Bar(self.fill_in_table, "medium", (14, 3))
        widgets = [self.search_bar, *self.get_buttons()]
        if self.associates is not None:
            if len(self.associates) == 1:
                lineedit = get_lineedit("large", (14, 3), text=self.associates[0][0], read_only=True)
                widgets = [lineedit] + widgets
            else:
                combo_box = get_combo_box([associate[0] for associate in self.associates], "large", (14, 3))
                combo_box.currentIndexChanged.connect(self.change_associate)
                widgets = [combo_box] + widgets
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        add_widgets_in_layout(self.layout_main, layout, widgets)

        self.fill_in_table()

    @abstractmethod
    def get_table(self) -> Table_Objects[T]:
        pass

    @abstractmethod
    def get_buttons(self) -> list[QPushButton]:
        pass

    @abstractmethod
    def fill_in_row(self, row: int, obj: T | None = None) -> None:
        pass

    def search_objects(self) -> list[T]:
        return self.db.load_like(
            self.table_root, self.get_associate_uuid(), self.search_bar.text(), 500, shallow=self.shallow_load
        )

    def fill_in_table(self) -> None:
        objects = self.search_objects()
        self.table.set_objects(objects)
        for i, obj in enumerate(objects):
            self.fill_in_row(i, obj)
        self.table.reset_changes()

    def change_associate(self, i: int) -> None:
        assert(self.associates is not None)
        self.associates_index = i
        self.fill_in_table()

    def add_new_row(self) -> None:
        self.table.add_row()
        self.fill_in_row(0)

    def get_associate_uuid(self) -> str:
        if self.associates is None:
            return ""
        return self.associates[self.associates_index][1]

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
            self.db.add_list(self.table_root, objects_add, shallow=self.shallow_add)
        if objects_update:
            self.db.update_list(self.table_root, objects_update, shallow=self.shallow_update)
        if objects_remove:
            self.db.remove_list(self.table_root, objects_remove)
        self.fill_in_table()
