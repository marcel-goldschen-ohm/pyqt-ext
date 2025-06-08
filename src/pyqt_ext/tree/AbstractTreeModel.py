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

    def reset(self) -> None:
        """ Reset the model. """
        self.setRoot(self.root())
    
    # !!! must reimplement if you need more than one column
    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
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

        Always returns the index for the first column.
        """
        if (item is self.root()) or (item.parent is None):
            return QModelIndex()
        row: int = item.siblingIndex()
        col: int = 0
        return self.createIndex(row, col, item)

    def pathFromItem(self, item: AbstractTreeItem) -> str:
        """ Path from the chain of item names up to root.
        """
        return item.path
    
    def itemFromPath(self, path: str, root: AbstractTreeItem = None) -> AbstractTreeItem:
        """ Find the item associated with path starting from root.
        """
        if root is None:
            root = self.root()
        # if path == '/':
        #     return root
        return root[path]

    def pathFromIndex(self, index: QModelIndex = QModelIndex()) -> str:
        """ Get the path associated with index.
        """
        if not index.isValid():
            # root item
            return '/'
        item: AbstractTreeItem = self.itemFromIndex(index)
        return self.pathFromItem(item)
    
    def indexFromPath(self, path: str) -> QModelIndex:
        """ Get the index associated with path.
        """
        item: AbstractTreeItem = self.itemFromPath(path)
        return self.indexFromItem(item)

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        """ Uses `AbstractTreeItem.parent` to get the parent index.
        """
        if not index.isValid():
            return QModelIndex()
        item: AbstractTreeItem = self.itemFromIndex(index)
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None or parent_item is self.root():
            return QModelIndex()
        return self.indexFromItem(parent_item)

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
            return item.data(index.column())

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        """ Set data via `AbstractTreeItem.set_data`.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.set_data`.
        """
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            success: bool = item.setData(index.column(), value)
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
                label = labels[section]
                if label is not None:
                    return label
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
        return root.maxDepthBelow()

    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        """ Calls `AbstractTreeItem.removeChild` to remove rows.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.removeChild`.
        """
        if count <= 0:
            return False
        n_rows: int = self.rowCount(parent_index)
        if (row < 0) or (row + count > n_rows):
            raise IndexError('Invalid row index(es).')
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        self.beginRemoveRows(parent_index, row, row + count - 1)
        did_succeed = False
        did_fail = False
        for row_ in reversed(list(range(row, row + count))):
            item: AbstractTreeItem = parent_item.children[row_]
            try:
                parent_item.removeChild(item)
                did_succeed = True
            except:
                did_fail = True
        self.endRemoveRows()
        if not did_succeed:
            return False
        if not did_fail:
            return True
        # some success, some failure
        self.reset()
        return False
    
    def removeItem(self, item: AbstractTreeItem) -> bool:
        """ Remove the item from the model.
        
        Calls `removeRows` internally.
        """
        parent_item: AbstractTreeItem = item.parent
        if parent_item is None:
            # cannot remove the root item
            return False
        parent_index: QModelIndex = self.indexFromItem(parent_item)
        item_row: int = item.siblingIndex()
        return self.removeRows(item_row, 1, parent_index)
    
    # !!! not implemented
    def insertRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        """ See `insertItems` instead.
        
        In order to implement this, the model would need to know the type of item to insert (i.e. as derived from AbstractTreeItem).
        """
        # raise NotImplementedError
        return False
    
    def insertItems(self, row: int, items: list[AbstractTreeItem], parent_index: QModelIndex = QModelIndex()) -> bool:
        """ Calls `AbstractTreeItem.insertChild` to insert items (i.e., rows).
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.insertChild`.
        """
        if not items:
            return False
        n_rows: int = self.rowCount(parent_index)
        if (row < 0) or (row > n_rows):
            raise IndexError('Invalid row index(es).')
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        count: int = len(items)
        self.beginInsertRows(parent_index, row, row + count - 1)
        did_succeed = False
        did_fail = False
        for item in items:
            try:
                parent_item.insertChild(row, item)
                row += 1
                did_succeed = True
            except:
                did_fail = True
        self.endInsertRows()
        if not did_succeed:
            return False
        if not did_fail:
            return True
        # some success, some failure
        self.reset()
        return False
    
    def appendItems(self, items: list[AbstractTreeItem], parent_index: QModelIndex = QModelIndex()) -> bool:
        row = self.rowCount(parent_index)
        return self.insertItems(row, items, parent_index)
    
    def moveRows(self, src_parent_index: QModelIndex, src_row: int, count: int, dst_parent_index: QModelIndex, dst_row: int) -> bool:
        """ !!! For now this is non-optimial and just repeatedly calls `moveRow` one item at a time.
        """
        n_moved: int = 0
        for row in reversed(list(range(src_row, src_row + count))):
            success: bool = self.moveRow(src_parent_index, row, dst_parent_index, dst_row)
            n_moved += int(success)
            if success:
                if src_parent_index == dst_parent_index:
                    if row < dst_row:
                        dst_row -= 1
        if n_moved == 0:
            return False
        if n_moved == count:
            return True
        # some success, some failure
        self.reset()
        return False
    
    def moveRow(self, src_parent_index: QModelIndex, src_row: int, dst_parent_index: QModelIndex, dst_row: int) -> bool:
        """ Calls `AbstractTreeItem.insertChild` to move an item (e.g., row) within the tree.
        
        Probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.insertChild`.
        """
        n_src_rows: int = self.rowCount(src_parent_index)
        n_dst_rows: int = self.rowCount(dst_parent_index)
        if (src_parent_index == dst_parent_index) and (src_row == dst_row):
            # no change
            return False
        if not (0 <= src_row < n_src_rows):
            raise IndexError('Invalid source row index.')
        if not (0 <= dst_row <= n_dst_rows):
            raise IndexError('Invalid destination row index.')

        src_parent_item: AbstractTreeItem = self.itemFromIndex(src_parent_index)
        src_item: AbstractTreeItem = src_parent_item.children[src_row]
        dst_parent_item: AbstractTreeItem = self.itemFromIndex(dst_parent_index)
        if dst_parent_item.hasAncestor(src_item):
            # Cannot move an item to one of its descendants.
            # Instead of raising an error, just silently fail.
            return False
        if src_parent_item is dst_parent_item:
            if (src_row == dst_row) or (src_row + 1 == dst_row):
                # attempt to move to the same position, so no change
                return False

        self.beginMoveRows(src_parent_index, src_row, src_row, dst_parent_index, dst_row)
        dst_parent_item.insertChild(dst_row, src_item)
        self.endMoveRows()
        return True
    
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
    root.appendChild(AbstractTreeItem(name='child2'))
    root.insertChild(1, AbstractTreeItem(name='child3'))
    root.children[1].appendChild(AbstractTreeItem())
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