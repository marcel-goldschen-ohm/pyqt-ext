""" Tree model for key:value pairs that uses KeyValueTreeItem for its data interface.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import AbstractTreeModel, AbstractTreeMimeData, KeyValueTreeItem
import qtawesome as qta


class KeyValueTreeModel(AbstractTreeModel):

    MIME_TYPE = 'application/x-KeyValueTreeModel'
    
    def __init__(self, data: KeyValueTreeItem | dict | list = None, **kwargs):
        AbstractTreeModel.__init__(self, data, **kwargs)
        self.setColumnLabels(['Key', 'Value'])
    
    def setupItemTree(self, data: dict | list) -> KeyValueTreeItem:
        """ Build an item tree from data.
        """
        if data is None:
            return
        elif isinstance(data, KeyValueTreeItem):
            return data
        if not isinstance(data, dict) and not isinstance(data, list):
            raise ValueError('Root must be a dict or list.')
        return KeyValueTreeItem(data)
    
    def treeData(self) -> dict | list:
        """ The tree data.
        """
        root: KeyValueTreeItem = self.root()
        return root.value()
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """ Default item flags.
        
        Supports drag-and-drop if it is enabled in `supportedDropActions`.
        """
        if not index.isValid():
            # root item
            if self.supportedDropActions() != Qt.DropAction.IgnoreAction:
                # allow drops on the root item (i.e., this allows drops on the viewport away from other items)
                return Qt.ItemFlag.ItemIsDropEnabled
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        if self.supportedDropActions() != Qt.DropAction.IgnoreAction:
            flags |= Qt.ItemFlag.ItemIsDragEnabled
            item: KeyValueTreeItem = self.itemFromIndex(index)
            value = item.value()
            if isinstance(value, dict) or isinstance(value, list):
                flags |= Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return
        item: KeyValueTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return item.key()
            elif index.column() == 1:
                if item.isLeaf():
                    return item.value()
        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                value = item.value()
                if isinstance(value, dict):
                    return qta.icon('ph.folder-thin')
                elif isinstance(value, list):
                    return qta.icon('ph.list-numbers-thin')

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if not index.isValid():
            return False
        item: KeyValueTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                item.setKey(value)
                self.dataChanged.emit(index, index)
                return True
            elif index.column() == 1:
                self.beginResetModel()
                item.setValue(value)
                self.endResetModel()
                return True
        return False


class KeyValueTreeMimeData(AbstractTreeMimeData):
    """ Custom MIME data class for drag-and-drop with `AbstractTreeModel`s.

    This class allows storing a reference to an `AbstractTreeModel` and some of its `AbstractTreeItem`s (i.e., the items being dragged during drag-and-drop) in the MIME data.
    This allows simple transfer of tree items within and between `AbstractTreeModel`s in the same program/process.

    Note:
    This approach probably won't work if you need to pass items between `AbstractTreeModel`s in separate programs/processes.
    If you really need to do this, you need to somehow serialize the dragged items (maybe with pickle), pass the serialized bytes in the drag MIME data, then deserialize back to the items on drop.
    """

    MIME_TYPE = 'application/x-key-value-tree-model-items'

    def __init__(self, model: AbstractTreeModel, items: list[KeyValueTreeItem]):
        AbstractTreeMimeData.__init__(self, model, items)
