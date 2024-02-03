""" Base class for a tree model that uses AbstractTreeItem for its data interface.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeItem


class AbstractTreeModel(QAbstractItemModel):
    """ Base class for a tree model that uses AbstractTreeItem for its data interface.

    This class can work as is, but in general 
    you should derive from it and reimplement the columnCount() method.

    Depending on your data, you may also need to reimplement methods that restrucutre the tree hierarchy.

    To enable drag and drop, reimplement the supportedDropActions() and flags() methods to allow drops and to return flags enabling dragging and dropping.
    """

    def __init__(self, root: AbstractTreeItem, parent: QObject = None):
        QAbstractItemModel.__init__(self, parent)
        self._root: AbstractTreeItem = root
        self._row_labels: list | None = None
        self._column_labels: list | None = None
    
    @property
    def root(self) -> AbstractTreeItem:
        return self._root
    
    @root.setter
    def root(self, root: AbstractTreeItem) -> None:
        self.beginResetModel()
        self._root = root
        self.endResetModel()
    
    @property
    def row_labels(self) -> list | None:
        return self._row_labels
    
    @row_labels.setter
    def row_labels(self, row_labels: list | None) -> None:
        n_old_row_labels = len(self._row_labels) if self._row_labels is not None else 0
        n_new_row_labels = len(row_labels) if row_labels is not None else 0
        n_row_labels = max(n_old_row_labels, n_new_row_labels)
        self._row_labels = row_labels
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, n_row_labels - 1)
    
    @property
    def column_labels(self) -> list | None:
        return self._column_labels
    
    @column_labels.setter
    def column_labels(self, column_labels: list | None) -> None:
        n_old_column_labels = len(self._column_labels) if self._column_labels is not None else 0
        n_new_column_labels = len(column_labels) if column_labels is not None else 0
        n_column_labels = max(n_old_column_labels, n_new_column_labels)
        self._column_labels = column_labels
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, n_column_labels - 1)
    
    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        if parent_index.column() > 0:
            return 0
        if not parent_index.isValid():
            parent_item: AbstractTreeItem = self.root
        else:
            parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        return len(parent_item.children)

    # !!! not implemented
    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        # raise NotImplementedError
        return 1

    def itemFromIndex(self, index: QModelIndex = QModelIndex()) -> AbstractTreeItem | None:
        if not index.isValid():
            return self.root
        item: AbstractTreeItem = index.internalPointer()
        return item

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        item: AbstractTreeItem = self.itemFromIndex(index)
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None or parent_item is self.root:
            return QModelIndex()
        row: int = parent_item.row()
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
            # for drag and drop, allow drops on the root item (i.e., this allows drops on the viewport)
            return Qt.ItemFlag.ItemIsDropEnabled # Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return item.data(index.column())

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            success: bool = item.set_data(index.column(), value)
            return success
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if self.column_labels is None:
                    return section
                if section < len(self.column_labels):
                    return self.column_labels[section]
            elif orientation == Qt.Orientation.Vertical:
                if self.row_labels is None:
                    return section
                if section < len(self.row_labels):
                    return self.row_labels[section]

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value, role: int) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            if orientation == Qt.Orientation.Horizontal:
                if self.column_labels is None:
                    self.column_labels = [None] * section + [value]
                    return True
                if section < len(self.column_labels):
                    self._column_labels[section] = value
                    self.headerDataChanged.emit(orientation, section, section)
                    return True
                else:
                    first = len(self.column_labels)
                    self._column_labels += [None] * (section - first) + [value]
                    self.headerDataChanged.emit(orientation, first, section)
                    return True
            elif orientation == Qt.Orientation.Vertical:
                if self.row_labels is None:
                    self.row_labels = [None] * section + [value]
                    return True
                if section < len(self.row_labels):
                    self._row_labels[section] = value
                    self.headerDataChanged.emit(orientation, section, section)
                    return True
                else:
                    first = len(self.row_labels)
                    self._row_labels += [None] * (section - first) + [value]
                    self.headerDataChanged.emit(orientation, first, section)
                    return True
        return False

    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        if row < 0 or row + count > len(parent_item.children):
            return False
        self.beginRemoveRows(parent_index, row, row + count - 1)
        success: bool = parent_item.remove_children(row, count)
        self.endRemoveRows()
        return success
    
    def removeItem(self, item: AbstractTreeItem) -> bool:
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None:
            # cannot remove the root item
            return False
        parent_index: QModelIndex = self.createIndex(parent_item.row(), 0, parent_item)
        return self.removeRows(item.row(), 1, parent_index)
    
    def insertItems(self, row: int, items: list[AbstractTreeItem], parent_index: QModelIndex = QModelIndex()) -> bool:
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        if row < 0 or row > len(parent_item.children):
            return False
        count: int = len(items)
        self.beginInsertRows(parent_index, row, row + count - 1)
        success: bool = parent_item.insert_children(row, items)
        self.endInsertRows()
        return success
    
    def moveRow(self, src_parent_index: QModelIndex, src_row: int, dst_parent_index: QModelIndex, dst_row: int) -> bool:
        if (src_parent_index == dst_parent_index) and (src_row == dst_row):
            return False
        if src_row < 0:
            # negative indexing
            src_row += self.rowCount(src_parent_index)
        if dst_row < 0:
            # negative indexing
            dst_row += self.rowCount(dst_parent_index)
        if not (0 <= src_row < self.rowCount(src_parent_index)):
            return False
        if not (0 <= dst_row <= self.rowCount(dst_parent_index)):
            return False

        src_parent_item: AbstractTreeItem = self.itemFromIndex(src_parent_index)
        src_item: AbstractTreeItem = src_parent_item.children[src_row]
        dst_parent_item: AbstractTreeItem = self.itemFromIndex(dst_parent_index)

        self.beginMoveRows(src_parent_index, src_row, src_row, dst_parent_index, dst_row)
        dst_parent_item.insert_child(dst_row, src_item)
        self.endMoveRows()
        return True
    
    def supportedDropActions(self) -> Qt.DropActions:
        # to disable dropping: return Qt.DropAction.IgnoreAction
        # to enable dropping: return, e.g., Qt.DropAction.MoveAction | Qt.DropAction.CopyAction
        return Qt.DropAction.MoveAction #| Qt.DropAction.CopyAction
    
    def max_depth(self):
        return self.root.subtree_max_depth() - 1
