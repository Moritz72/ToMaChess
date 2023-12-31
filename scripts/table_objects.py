from typing import Any, TypeVar, Generic, cast
from PySide6.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QTableWidgetItem
from PySide6.QtCore import Qt, QPoint, QModelIndex, Signal
from PySide6.QtGui import QDropEvent
from .object import Object
from .gui_table import set_up_table, size_table, get_table_value

T = TypeVar('T', bound=Object)


class Table_Objects(QTableWidget, Generic[T]):
    def __init__(
            self, columns: int, row_height: float, max_width: float, widths: list[float | None] | list[float],
            header_horizontal: list[str], stretches: list[int] | None = None, limit: int = 200,
            translate: bool = False, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.objects: list[T | None] = []
        self.row_height: float = row_height
        self.max_width: float = max_width
        self.widths: list[float | None] | list[float] = widths
        self.stretches: list[int] | None = stretches
        self.limit: int = limit
        self.deleted_objects: list[T] = []
        set_up_table(self, 0, columns, header_horizontal=header_horizontal, translate=translate)
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resize_table()

    def set_objects(self, objects: list[T]) -> None:
        self.objects = cast(list[T | None], objects)[:self.limit]
        self.resize_table()

    def insert_object(self, i: int, obj: T) -> None:
        self.objects.insert(i, obj)
        self.resize_table()

    def reset_changes(self) -> None:
        self.deleted_objects = []

    def resize_table(self) -> None:
        size_table(
            self, rows=len(self.objects), row_height=self.row_height,
            max_width=self.max_width, widths=self.widths, stretches_h=self.stretches
        )

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


class Table_Objects_Drag(Table_Objects[T], Generic[T]):
    swapped = Signal()

    def __init__(
            self, columns: int, row_height: float, max_width: float, widths: list[float | None] | list[float],
            header_horizontal: list[str], stretches: list[int] | None = None, limit: int = 1000,
            translate: bool = False, parent: QWidget | None = None
    ) -> None:
        super().__init__(columns, row_height, max_width, widths, header_horizontal, stretches, limit, translate, parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [
                [QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                for row_index in rows
            ]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1
            for row_index, (data, row) in enumerate(zip(rows_to_move, rows)):
                row_index += drop_row
                self.objects.insert(row_index, self.objects.pop(row))
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                for column_index in range(self.columnCount()):
                    self.item(drop_row + row_index, column_index).setSelected(True)
            self.resize_table()
            self.swapped.emit()
        super().dropEvent(event)

    def drop_on(self, event: QDropEvent) -> int:
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()
        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos: QPoint, index: QModelIndex) -> bool:
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        return rect.contains(pos, True) and pos.y() >= rect.center().y()
