from typing import Any, TypeVar, Generic, cast
from PySide6.QtWidgets import QTableWidget
from .object import Object
from .gui_table import set_up_table, size_table, get_table_value

T = TypeVar('T', bound=Object)


class Table_Objects(QTableWidget, Generic[T]):
    def __init__(
            self, columns: int, row_height: float, max_width: float, widths: list[float | None] | list[float],
            header_horizontal: list[str], limit: int = 200, translate: bool = False
    ) -> None:
        super().__init__()
        self.objects: list[T | None] = []
        self.row_height: float = row_height
        self.max_width: float = max_width
        self.widths: list[float | None] | list[float] = widths
        self.limit: int = limit
        self.deleted_objects: list[T] = []
        set_up_table(self, 0, columns, header_horizontal=header_horizontal, translate=translate)

    def set_objects(self, objects: list[T]) -> None:
        self.objects = cast(list[T | None], objects)[:self.limit]
        self.resize_table()

    def reset_changes(self) -> None:
        self.deleted_objects = []

    def resize_table(self) -> None:
        size_table(self, len(self.objects), self.row_height, max_width=self.max_width, widths=self.widths)

    def delete_current_row(self) -> None:
        row = self.currentRow()
        obj = self.objects.pop(row)
        if obj is not None:
            self.deleted_objects.append(obj)
        self.removeRow(row)
        self.resize_table()

    def add_row(self) -> None:
        self.insertRow(0)
        self.objects.insert(0, None)
        self.resize_table()

    def retrieve_changes(self) -> tuple[list[T], list[T], list[tuple[Any, ...]], list[tuple[Any, ...]]]:
        nones = self.objects.count(None)
        objects_data = [
            tuple(get_table_value(self, row, column) for column in range(self.columnCount()))
            for row in range(self.rowCount())
        ]
        return cast(list[T], self.objects[nones:]), self.deleted_objects, objects_data[nones:], objects_data[:nones]
