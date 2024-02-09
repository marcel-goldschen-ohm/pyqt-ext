""" Base class for a tree model that uses AbstractTreeItem for its data interface.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeItem


class AbstractTreeModel(QAbstractItemModel):
    """ Base class for a tree model that uses AbstractTreeItem for its data interface.

    This class can work as is, but in general you will derive from it and reimplement the columnCount() method.
    Depending on your data, you may also need to reimplement flags() or other methods that restructure the tree hierarchy.

    For drag and drop, reimplement the supportedDropActions() and flags() methods.
    """

    def __init__(self, root: AbstractTreeItem = None, parent: QObject = None):
        QAbstractItemModel.__init__(self, parent)
        self._root: AbstractTreeItem = root
        self._row_labels: list = []
        self._column_labels: list = []
    
    def root(self) -> AbstractTreeItem:
        return self._root
    
    def setRoot(self, root: AbstractTreeItem) -> None:
        self.beginResetModel()
        self._root = root
        self.endResetModel()
    
    def rowLabels(self) -> list:
        return self._row_labels
    
    def setRowLabels(self, labels: list) -> None:
        old_labels = self._row_labels
        n_overlap = min(len(labels), len(old_labels))
        first_change = 0
        while (first_change < n_overlap) and (labels[first_change] == old_labels[first_change]):
            first_change += 1
        last_change = max(len(labels), len(old_labels)) - 1
        while (last_change < n_overlap) and (labels[last_change] == old_labels[last_change]):
            last_change -= 1
        self._row_labels = labels
        if first_change <= last_change: 
            self.headerDataChanged.emit(Qt.Orientation.Vertical, first_change, last_change)
    
    def columnLabels(self) -> list | None:
        return self._column_labels
    
    def setColumnLabels(self, labels: list | None) -> None:
        old_labels = self._column_labels
        n_overlap = min(len(labels), len(old_labels))
        first_change = 0
        while (first_change < n_overlap) and (labels[first_change] == old_labels[first_change]):
            first_change += 1
        last_change = max(len(labels), len(old_labels)) - 1
        while (last_change < n_overlap) and (labels[last_change] == old_labels[last_change]):
            last_change -= 1
        self._column_labels = labels
        if first_change <= last_change: 
            self.headerDataChanged.emit(Qt.Orientation.Horizontal, first_change, last_change)
    
    def maxDepth(self):
        root: AbstractTreeItem = self.root()
        if root is None:
            return 0
        return root.branch_max_depth() - 1
    
    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        if parent_index.column() > 0:
            return 0
        if not parent_index.isValid():
            parent_item: AbstractTreeItem = self.root()
        else:
            parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        if parent_item is None:
            return 0
        return len(parent_item.children)

    # !!! not implemented
    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        # raise NotImplementedError
        return 1

    def itemFromIndex(self, index: QModelIndex = QModelIndex()) -> AbstractTreeItem | None:
        if not index.isValid():
            return self.root()
        item: AbstractTreeItem = index.internalPointer()
        return item

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        item: AbstractTreeItem = self.itemFromIndex(index)
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None or parent_item is self.root():
            return QModelIndex()
        row: int = parent_item.sibling_index
        col: int = 0
        return self.createIndex(row, col, parent_item)

    def index(self, row: int, column: int, parent_index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent_index):
            return QModelIndex()
        if parent_index.isValid() and parent_index.column() != 0:
            return QModelIndex()
        try:
            parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
            item: AbstractTreeItem = parent_item.children[row]
            return self.createIndex(row, column, item)
        except IndexError:
            return QModelIndex()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            if self.supportedDropActions() != Qt.DropAction.IgnoreAction:
                # allow drops on the root item (i.e., this allows drops on the viewport away from other items)
                return Qt.ItemFlag.ItemIsDropEnabled
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        if self.supportedDropActions() != Qt.DropAction.IgnoreAction:
            flags |= Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return item.data(index.column())

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            success: bool = item.set_data(index.column(), value)
            return success
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                labels = self.columnLabels()
            elif orientation == Qt.Orientation.Vertical:
                labels = self.rowLabels()
            if section < len(labels):
                return labels[section]
            return section

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value, role: int) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            if orientation == Qt.Orientation.Horizontal:
                labels = self.columnLabels()
            elif orientation == Qt.Orientation.Vertical:
                labels = self.rowLabels()
            if section < len(labels):
                labels[section] = value
            else:
                first = len(labels)
                labels += [None] * (section - first) + [value]
            if orientation == Qt.Orientation.Horizontal:
                self.setColumnLabels(labels)
            elif orientation == Qt.Orientation.Vertical:
                self.setRowLabels(labels)
            return True
        return False

    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        if row < 0 or row + count > len(parent_item.children):
            return False
        self.beginRemoveRows(parent_index, row, row + count - 1)
        for _ in range(count):
            item: AbstractTreeItem = parent_item.children[row]
            parent_item.remove_child(item)
        self.endRemoveRows()
        return True
    
    def removeItem(self, item: AbstractTreeItem) -> bool:
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None:
            # cannot remove the root item
            return False
        parent_index: QModelIndex = self.createIndex(parent_item.row(), 0, parent_item)
        return self.removeRows(item.row(), 1, parent_index)
    
    # !!! not implemented
    def insertRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        return False
    
    def insertItems(self, row: int, items: list[AbstractTreeItem], parent_index: QModelIndex = QModelIndex()) -> bool:
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        if row < 0 or row > len(parent_item.children):
            return False
        count: int = len(items)
        self.beginInsertRows(parent_index, row, row + count - 1)
        for i, item in enumerate(items):
            parent_item.insert_child(row + i, item)
        self.endInsertRows()
        return True
    
    def moveRow(self, src_parent_index: QModelIndex, src_row: int, dst_parent_index: QModelIndex, dst_row: int) -> bool:
        if src_row < 0:
            # negative indexing
            src_row += self.rowCount(src_parent_index)
        if dst_row < 0:
            # negative indexing
            dst_row += self.rowCount(dst_parent_index)
        if (src_parent_index == dst_parent_index) and (src_row == dst_row):
            return False
        if not (0 <= src_row < self.rowCount(src_parent_index)):
            return False
        if not (0 <= dst_row <= self.rowCount(dst_parent_index)):
            return False

        src_parent_item: AbstractTreeItem = self.itemFromIndex(src_parent_index)
        src_item: AbstractTreeItem = src_parent_item.children[src_row]
        dst_parent_item: AbstractTreeItem = self.itemFromIndex(dst_parent_index)

        self.beginMoveRows(src_parent_index, src_row, src_row, dst_parent_index, dst_row)
        success: bool = dst_parent_item.insert_child(dst_row, src_item)
        self.endMoveRows()
        return success
    
    # !!! reimplement for drag and drop
    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.IgnoreAction


class AbstractDndTreeModel(AbstractTreeModel):

    def __init__(self, root: AbstractTreeItem = None, parent: QObject = None):
        AbstractTreeModel.__init__(self, root, parent)
    
    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction