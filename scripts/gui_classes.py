from typing import Callable, cast
from PySide6.QtWidgets import QComboBox, QLineEdit, QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtCore import Qt, QTimer, QEvent, QObject, QModelIndex, QPersistentModelIndex, QThread, Signal, QPointF, \
    QRectF


class Combo_Box_Editable(QComboBox):
    def __init__(self) -> None:
        super().__init__()
        self.setEditable(True)
        self.setLineEdit(Combo_Box_Editable_Line_Edit())
        self.lineEdit().setReadOnly(True)
        self.timer: QTimer = QTimer()
        self.timer.timeout.connect(self.time_up)
        self.timer.start(20)

    def set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        self.lineEdit().setAlignment(alignment)

    def showPopup(self) -> None:
        if not self.timer.isActive():
            super().showPopup()

    def hidePopup(self) -> None:
        self.timer.start(20)
        super().hidePopup()

    def time_up(self) -> None:
        self.timer.stop()


class Combo_Box_Editable_Line_Edit(QLineEdit):
    def mousePressEvent(self, event: QEvent) -> None:
        cast(QComboBox, self.parent()).showPopup()

    def mouseDoubleClickEvent(self, event: QEvent) -> None:
        pass


class Align_Delegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None, align: Qt.AlignmentFlag | None = None) -> None:
        super().__init__(parent)
        self.align: Qt.AlignmentFlag | None = align

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        super().initStyleOption(option, index)
        if self.align is not None:
            option.displayAlignment = self.align


class Vertical_Text_Delegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)

    def paint(self, painter, option, index):
        optionCopy = QStyleOptionViewItem(option)
        rectCenter = QPointF(QRectF(option.rect).center())
        painter.save()
        painter.translate(rectCenter.x(), rectCenter.y())
        painter.rotate(90)
        painter.translate(-rectCenter.x(), -rectCenter.y())
        optionCopy.rect = painter.worldTransform().mapRect(option.rect)
        super().paint(painter, optionCopy, index)
        painter.restore()


class Function_Worker(QThread):
    finished = Signal()

    def __init__(self, function: Callable[[], None], parent: QObject | None) -> None:
        super().__init__(parent=parent)
        self.function: Callable[[], None] = function

    def run(self) -> None:
        self.function()
        self.finished.emit()
