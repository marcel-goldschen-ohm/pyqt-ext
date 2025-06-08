""" Tree model for key-value pairs that uses KeyValueTreeItem for its data interface.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import AbstractTreeModel, KeyValueTreeItem
import qtawesome as qta


class KeyValueTreeModel(AbstractTreeModel):

    keyChanged = Signal()
    valueChanged = Signal()
    
    def __init__(self, root: KeyValueTreeItem = None, parent: QObject = None):
        AbstractTreeModel.__init__(self, root, parent)
        self.setColumnLabels(['Key', 'Value'])
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            if self.supportedDropActions() != Qt.DropAction.IgnoreAction:
                # allow drops on the root item (i.e., this allows drops on the viewport away from other items)
                return Qt.ItemFlag.ItemIsDropEnabled
            return Qt.ItemFlag.NoItemFlags
        item: KeyValueTreeItem = self.itemFromIndex(index)
        # if (index.column() == 1) and item.is_container():
        #     # cannot edit container value, only the values of items inside it
        #     flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        # else:
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        if self.supportedDropActions() != Qt.DropAction.IgnoreAction:
            flags |= Qt.ItemFlag.ItemIsDragEnabled
            if item.isContainer():
                flags |= Qt.ItemFlag.ItemIsDropEnabled
        # data = self.data(index, Qt.ItemDataRole.DisplayRole)
        # if isinstance(data, bool):
        #     flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        item: KeyValueTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 1 and item.isContainer():
                return None
            return item.data(index.column())
        elif role == Qt.ItemDataRole.EditRole:
            return item.data(index.column())
        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                if item.isDict():
                    return qta.icon('ph.folder-thin')
                if item.isList():
                    return qta.icon('ph.list-numbers-thin')

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        item: KeyValueTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            success: bool = item.setData(index.column(), value)
            if success:
                if index.column() == 0:
                    self.keyChanged.emit()
                elif index.column() == 1:
                    self.valueChanged.emit()
            return success
        return False


class KeyValueDndTreeModel(KeyValueTreeModel):

    def __init__(self, root: KeyValueTreeItem = None, parent: QObject = None):
        KeyValueTreeModel.__init__(self, root, parent)
    
    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction