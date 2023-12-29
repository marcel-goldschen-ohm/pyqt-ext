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
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item: AbstractTreeItem = self.root
        else:
            parent_item: AbstractTreeItem = self.get_item(parent)
        return len(parent_item.children)

    # !!! not implemented
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # raise NotImplementedError
        return 1

    def get_item(self, index: QModelIndex = QModelIndex()) -> AbstractTreeItem | None:
        if not index.isValid():
            return self.root
        item: AbstractTreeItem = index.internalPointer()
        try:
            AbstractTreeItem(item)
            return item
        except:
            return None

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        item: AbstractTreeItem = self.get_item(index)
        if item is None:
            return QModelIndex()
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None or parent_item is self.root:
            return QModelIndex()
        row: int = parent_item.row()
        col: int = 0
        return self.createIndex(row, col, parent_item)

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_item: AbstractTreeItem = self.root
        else:
            if parent.column() != 0:
                return QModelIndex()
            parent_item: AbstractTreeItem = self.get_item(parent)
        try:
            item: AbstractTreeItem = parent_item.children[row]
            return self.createIndex(row, column, item)
        except IndexError:
            return QModelIndex()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return
        item: AbstractTreeItem = self.get_item(index)
        if item is None:
            return
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return item.data(index.column())

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False
        item: AbstractTreeItem = self.get_item(index)
        if item is None:
            return False
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

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        if not parent.isValid():
            parent_item: AbstractTreeItem = self.root
        else:
            parent_item: AbstractTreeItem = self.get_item(parent)
        if parent_item is None:
            return False
        if row < 0 or row + count > len(parent_item.children):
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        success: bool = parent_item.remove_children(row, count)
        self.endRemoveRows()
        return success
    
    def remove_item(self, item: AbstractTreeItem) -> bool:
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None:
            # cannot remove the root item
            return False
        parent_index: QModelIndex = self.createIndex(parent_item.row(), 0, parent_item)
        return self.removeRows(item.row(), 1, parent_index)
    
    def insert_items(self, row: int, items: list[AbstractTreeItem], parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: AbstractTreeItem = self.get_item(parent)
        if parent_item is None:
            return False
        if row < 0 or row > len(parent_item.children):
            return False
        count: int = len(items)
        self.beginInsertRows(parent, row, row + count - 1)
        success: bool = parent_item.insert_children(row, items)
        self.endInsertRows()
        return success
    
    def max_depth(self):
        return self.root.subtree_max_depth() - 1
