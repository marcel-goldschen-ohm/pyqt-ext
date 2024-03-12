""" Base class for a tree model that uses AbstractTreeItem for its data interface.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import AbstractTreeItem


class AbstractTreeModel(QAbstractItemModel):
    """ Base class for a tree model that uses AbstractTreeItem for its data interface.

    This class can work as is, but in general you will derive from it
        and reimplement `columnCount`, `flags`, etc. to suit your data.

    For drag-and-drop, reimplement `supportedDropActions` and `flags` as needed.
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
        return root.branch_max_depth()
    
    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        """ Uses `AbstractTreeItem.children` to get the number of children of parent.
        """
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
        # Defaults to a single column tree.
        return 1

    def itemFromIndex(self, index: QModelIndex = QModelIndex()) -> AbstractTreeItem | None:
        """ Get the item associated with index.
        """
        if not index.isValid():
            return self.root()
        item: AbstractTreeItem = index.internalPointer()
        return item
    
    def indexFromItem(self, item: AbstractTreeItem) -> QModelIndex:
        """ Get the index associated with item.
        """
        if (item is self.root()) or (item.parent is None):
            return QModelIndex()
        row: int = item.sibling_index
        col: int = 0
        return self.createIndex(row, col, item)

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        """ Uses `AbstractTreeItem.parent` to get the parent index.
        """
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
        """ Return an index associated with the appropriate AbstractTreeItem.
        """
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

    # !!! you may want to cusomize this
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
            flags |= Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def data(self, index: QModelIndex, role: int):
        """ Get data via `AbstractTreeItem.get_data`.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.get_data`.
        """
        if not index.isValid():
            return
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return item.get_data(index.column())

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        """ Set data via `AbstractTreeItem.set_data`.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.set_data`.
        """
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            success: bool = item.set_data(index.column(), value)
            if success:
                self.dataChanged.emit(index, index)
            return success
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        """ Get data from `rowLabels` or `columnLabels`.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                labels = self.columnLabels()
            elif orientation == Qt.Orientation.Vertical:
                labels = self.rowLabels()
            if section < len(labels):
                return labels[section]
            return section

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value, role: int) -> bool:
        """ Set data in `rowLabels` or `columnLabels`.
        """
        if role == Qt.ItemDataRole.EditRole:
            if orientation == Qt.Orientation.Horizontal:
                labels = self.columnLabels()
            elif orientation == Qt.Orientation.Vertical:
                labels = self.rowLabels()
            if section < len(labels):
                labels[section] = value
            else:
                labels += [None] * (section - len(labels)) + [value]
            if orientation == Qt.Orientation.Horizontal:
                self.setColumnLabels(labels)
            elif orientation == Qt.Orientation.Vertical:
                self.setRowLabels(labels)
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False

    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        """ Calls `AbstractTreeItem.remove_child` to remove rows.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.remove_child`.
        """
        if count <= 0:
            return False
        n_rows: int = self.rowCount(parent_index)
        if row < 0:
            # negative indexing
            row += n_rows
        if (row < 0) or (row + count > n_rows):
            return False
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        self.beginRemoveRows(parent_index, row, row + count - 1)
        for _ in range(count):
            item: AbstractTreeItem = parent_item.children[row]
            parent_item.remove_child(item)
        self.endRemoveRows()
        return True
    
    def removeItem(self, item: AbstractTreeItem) -> bool:
        """ Remove the item from the model.
        
        Calls `removeRows` internally.
        """
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None:
            # cannot remove the root item
            return False
        parent_row: int = parent_item.sibling_index
        parent_index: QModelIndex = self.createIndex(parent_row, 0, parent_item)
        item_row: int = item.sibling_index
        return self.removeRows(item_row, 1, parent_index)
    
    # !!! not implemented
    def insertRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        """ See `insertItems` instead.
        
        In order to implement this, the model would need to know the type of item to insert (i.e. as derived from AbstractTreeItem).
        """
        return False
    
    def insertItems(self, row: int, items: list[AbstractTreeItem], parent_index: QModelIndex = QModelIndex()) -> bool:
        """ Calls `AbstractTreeItem.insert_child` to insert items (i.e., rows).
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.insert_child`.
        """
        if not items:
            return False
        n_rows: int = self.rowCount(parent_index)
        if row < 0:
            # negative indexing
            row += n_rows
        if (row < 0) or (row > n_rows):
            return False
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        count: int = len(items)
        self.beginInsertRows(parent_index, row, row + count - 1)
        for i, item in enumerate(items):
            parent_item.insert_child(row + i, item)
        self.endInsertRows()
        return True
    
    def appendItems(self, items: list[AbstractTreeItem], parent_index: QModelIndex = QModelIndex()) -> bool:
        row = self.rowCount(parent_index)
        return self.insertItems(row, items, parent_index)
    
    # !!! not implemented
    def moveRows(self, src_parent_index: QModelIndex, src_row: int, count: int, dst_parent_index: QModelIndex, dst_row: int) -> bool:
        """ See `moveRow` instead.
        """
        return False
    
    def moveRow(self, src_parent_index: QModelIndex, src_row: int, dst_parent_index: QModelIndex, dst_row: int) -> bool:
        """ Calls `AbstractTreeItem.insert_child` to move an item (e.g., row) within the tree.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.insert_child`.
        """
        n_src_rows: int = self.rowCount(src_parent_index)
        n_dst_rows: int = self.rowCount(dst_parent_index)
        if src_row < 0:
            # negative indexing
            src_row += n_src_rows
        if dst_row < 0:
            # negative indexing
            dst_row += n_dst_rows
        if (src_parent_index == dst_parent_index) and (src_row == dst_row):
            # no change
            return False
        if not (0 <= src_row < n_src_rows):
            return False
        if not (0 <= dst_row <= n_dst_rows):
            return False

        src_parent_item: AbstractTreeItem = self.itemFromIndex(src_parent_index)
        src_item: AbstractTreeItem = src_parent_item.children[src_row]
        dst_parent_item: AbstractTreeItem = self.itemFromIndex(dst_parent_index)
        if dst_parent_item.has_ancestor(src_item):
            # cannot move an item to one of its descendants
            return False
        if src_parent_item is dst_parent_item:
            if (src_row == dst_row) or (src_row + 1 == dst_row):
                # attempt to move to the same position
                return False

        self.beginMoveRows(src_parent_index, src_row, src_row, dst_parent_index, dst_row)
        success: bool = dst_parent_item.insert_child(dst_row, src_item)
        self.endMoveRows()
        return success
    
    # !!! reimplement for drag-and-drop
    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.IgnoreAction


class AbstractDndTreeModel(AbstractTreeModel):
    """ An AbstractTreeModel that supports drag-and-drop.
    """

    def __init__(self, root: AbstractTreeItem = None, parent: QObject = None):
        AbstractTreeModel.__init__(self, root, parent)
    
    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction


def test_model():
    root = AbstractTreeItem()
    AbstractTreeItem(parent=root)
    root.append_child(AbstractTreeItem(name='child2'))
    root.insert_child(1, AbstractTreeItem(name='child3'))
    root.children[1].append_child(AbstractTreeItem())
    grandchild2 = AbstractTreeItem(name='grandchild2')
    grandchild2.parent = root['child2']
    AbstractTreeItem(name='greatgrandchild', parent=root['/child2/grandchild2'])

    print('\nInitial model...')
    model = AbstractTreeModel(root)
    print(model.root())

    print('\nRemove grandchild2...')
    model.removeItem(grandchild2)
    print(model.root())

    print('\nInsert grandchild2...')
    model.insertItems(0, [grandchild2], model.indexFromItem(root['child2']))
    print(model.root())


if __name__ == '__main__':
    test_model()