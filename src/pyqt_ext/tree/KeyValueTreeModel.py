""" Tree model for key-value pairs that uses KeyValueTreeItem for its data interface.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import AbstractTreeModel, KeyValueTreeItem
import qtawesome as qta


class KeyValueTreeModel(AbstractTreeModel):

    sigKeyChanged = Signal()
    sigValueChanged = Signal()
    
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
            if item.is_container():
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
            if index.column() == 1 and item.is_container():
                return None
            return item.get_data(index.column())
        elif role == Qt.ItemDataRole.EditRole:
            return item.get_data(index.column())
        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                if item.is_dict():
                    return qta.icon('ph.folder-thin')
                if item.is_list():
                    return qta.icon('ph.list-numbers-thin')

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        item: KeyValueTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            success: bool = item.set_data(index.column(), value)
            if success:
                if index.column() == 0:
                    self.sigKeyChanged.emit()
                elif index.column() == 1:
                    self.sigValueChanged.emit()
            return success
        return False


class KeyValueDndTreeModel(KeyValueTreeModel):

    def __init__(self, root: KeyValueTreeItem = None, parent: QObject = None):
        KeyValueTreeModel.__init__(self, root, parent)
    
    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction