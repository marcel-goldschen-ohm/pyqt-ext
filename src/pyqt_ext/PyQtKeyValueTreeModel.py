""" Tree model for key-value pairs that uses PyQtKeyValueTreeItem for its data interface.
"""

from __future__ import annotations

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeModel, KeyValueTreeItem
import qtawesome as qta


class KeyValueTreeModel(AbstractTreeModel):
    
    def __init__(self, root: KeyValueTreeItem, parent: QObject = None):
        AbstractTreeModel.__init__(self, root, parent)
        self.column_labels = ['Key', 'Value']
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        item: KeyValueTreeItem = self.get_item(index)
        if index.column() == 1:
            if item.is_container():
                # cannot edit container value, only the values of items inside it
                return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return
        item: KeyValueTreeItem = self.get_item(index)
        if item is None:
            return
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return item.data(index.column())
        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                if item.is_container():
                    if isinstance(item.value, dict):
                        return qta.icon('ph.folder-thin')
                    if isinstance(item.value, list):
                        return qta.icon('ph.list-numbers-thin')

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False
        item: KeyValueTreeItem = self.get_item(index)
        if item is None:
            return False
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                item.key = value
                return True
            elif index.column() == 1:
                if item.is_container():
                    return False
                item.value = value
                return True
        return False
