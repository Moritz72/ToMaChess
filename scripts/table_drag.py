from PySide6.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem
from PySide6.QtCore import QPoint, QModelIndex, Signal
from PySide6.QtGui import QDropEvent


class Table_Drag(QTableWidget):
    swapped = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.permutation: list[int] = []

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def reset_permutation(self) -> None:
        self.permutation = [i for i in range(self.rowCount())]

    def setRowCount(self, rows: int) -> None:
        super().setRowCount(rows)
        self.reset_permutation()

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
                self.permutation.insert(row_index, self.permutation.pop(row))
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                for column_index in range(self.columnCount()):
                    self.item(drop_row + row_index, column_index).setSelected(True)
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
