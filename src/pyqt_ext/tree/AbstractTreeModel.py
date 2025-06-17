""" Base class for a tree model that uses AbstractTreeItem for its data interface.

Supports drag-and-drop within and between models in the same program/process.

TODO:
- move/copy items between different models
"""

from __future__ import annotations
from warnings import warn
from typing import Any
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import AbstractTreeItem


class AbstractTreeModel(QAbstractItemModel):
    """ Base class for a tree model that uses AbstractTreeItem for its data interface.

    Constructor takes either the tree data itself or a root item wrapping the tree data.

    This class can work as is, but in general you will derive from it and reimplement `setupItemTree`, `treeData`, `data` and `setData`. Optionally also reimplement `columnCount`, `flags`, etc. to suit your data.
    """

    MIME_TYPE = 'application/x-AbstractTreeModel'

    def __init__(self, data: AbstractTreeItem | Any = None, **kwargs):
        QAbstractItemModel.__init__(self, **kwargs)

        # tree data interface
        if (data is None) or isinstance(data, AbstractTreeItem):
            self._root: AbstractTreeItem = data
        else:
            # setup the item tree from the tree data
            self._root: AbstractTreeItem = self.setupItemTree(data)

        # headers
        self._row_labels: list = []
        self._column_labels: list = []

        # drag-and-drop
        self._supportedDropActions: Qt.DropActions = Qt.DropAction.MoveAction | Qt.DropAction.CopyAction
        self._mime_types: list[str] = [self.MIME_TYPE]
    
    # !! Must reimpliment.
    def setupItemTree(self, data: Any) -> AbstractTreeItem:
        """ Reimpliment in derived class to appropriately build an item tree from data.
        """
        if data is None:
            return
        elif isinstance(data, AbstractTreeItem):
            return data
        raise NotImplementedError
    
    # !! Must reimpliment.
    def treeData(self) -> Any:
        """ The tree data.
        """
        raise NotImplementedError
    
    def setTreeData(self, data: Any) -> None:
        """ Rebuild the item tree for the input tree data.
        """
        if (data is None) or isinstance(data, AbstractTreeItem):
            self.setRoot(data)
            return
        
        self.beginResetModel()
        self._root = self.setupItemTree(data)
        self.endResetModel()
    
    def root(self) -> AbstractTreeItem:
        return self._root
    
    def setRoot(self, root: AbstractTreeItem) -> None:
        self.beginResetModel()
        self._root = root
        self.endResetModel()
    
    def reset(self) -> None:
        """ Reset the model.
        """
        try:
            self.setTreeData(self.treeData())
        except:
            self.beginResetModel()
            self.endResetModel()
    
    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        """ Uses `AbstractTreeItem.children` to get the number of children of parent.
        """
        if parent_index.column() > 0:
            # ?? Only first column index has children. Not sure this matters.
            return 0
        if not parent_index.isValid():
            parent_item: AbstractTreeItem = self.root()
        else:
            parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        if parent_item is None:
            return 0
        return len(parent_item.children)

    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        """ Defaults to a single column tree.

        Reimplement if you need more than one column.
        """
        return 1

    def itemFromIndex(self, index: QModelIndex = QModelIndex()) -> AbstractTreeItem | None:
        """ Get the item associated with index.
        """
        if not index.isValid():
            return self.root()
        item: AbstractTreeItem = index.internalPointer()
        return item
    
    def indexFromItem(self, item: AbstractTreeItem, column: int = 0) -> QModelIndex:
        """ Get the index associated with item.

        Each item is associated with a row, so the column is either assumed to be 0 or needs to be given.
        """
        if (item is self.root()) or (item.parent() is None):
            # item is the root item
            return QModelIndex()
        row: int = item.siblingIndex()
        return self.createIndex(row, column, item)

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        """ Uses `AbstractTreeItem.parent` to get the parent index.
        """
        if not index.isValid():
            return QModelIndex()
        item: AbstractTreeItem = self.itemFromIndex(index)
        parent_item: AbstractTreeItem = item.parent()
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

    # !! Probably need to reimpliment.
    def data(self, index: QModelIndex, role: int):
        """ Reimpliment to get the data at index.
        """
        if not index.isValid():
            return
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return item.name()

    # !! Probably need to reimpliment.
    def setData(self, index: QModelIndex, value, role: int) -> bool:
        """ Reimpliment to set the data at index.
        """
        if not index.isValid():
            return False
        item: AbstractTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                item.setName(value)
                self.dataChanged.emit(index, index)  # ?? needed?
                return True
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
        
        Reimpliment if you need more efficient removal of multiple rows than the default one row at a time, or if you need custom logic to check the validity of the removals.
        Otherwise you probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.removeChild`.
        """
        if count <= 0:
            return False
        n_rows: int = self.rowCount(parent_index)
        if (row < 0) or (row + count > n_rows):
            return False
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        self.beginRemoveRows(parent_index, row, row + count - 1)
        # remove items in reverse order to preserve the sibling index of subsequent items to remove
        for i in reversed(list(range(row, row + count))):
            item: AbstractTreeItem = parent_item.children[i]
            parent_item.removeChild(item)
        self.endRemoveRows()
        return True
    
    def insertRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        """ Calls `AbstractTreeItem.insertChild` to insert rows.
        
        This only inserts `AbstractTreeItem`s. To insert derived classes, see `insertItems`.
        """
        if count <= 0:
            return False
        n_rows: int = self.rowCount(parent_index)
        if (row < 0) or (row > n_rows):
            return False
        parent_item: AbstractTreeItem = self.itemFromIndex(parent_index)
        self.beginInsertRows(parent_index, row, row + count - 1)
        for i in range(row, row + count):
            parent_item.insertChild(i, AbstractTreeItem())
        self.endInsertRows()
        return True
    
    def moveRows(self, src_parent_index: QModelIndex, src_row: int, count: int, dst_parent_index: QModelIndex, dst_row: int = -1) -> bool:
        """ Calls `AbstractTreeItem.insertChild` to move items (e.g., rows) within the tree.
        
        Reimpliment if you need custom logic to check the validity of the move.
        Otherwise you probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.insertChild`.
        """
        # print('moveRows(', self.itemFromIndex(src_parent_index).path, src_row, count, self.itemFromIndex(dst_parent_index).path, dst_row, ')')
        n_src_rows: int = self.rowCount(src_parent_index)
        n_dst_rows: int = self.rowCount(dst_parent_index)
        if (src_row < 0) or (src_row + count > n_src_rows):
            return False
        if dst_row == -1:
            # append
            dst_row = n_dst_rows
        elif not (0 <= dst_row <= n_dst_rows):
            return False
        if (src_parent_index == dst_parent_index) and (0 <= dst_row - src_row <= count):
            # no change, dst is within src items
            return False
        
        src_parent_item: AbstractTreeItem = self.itemFromIndex(src_parent_index)
        dst_parent_item: AbstractTreeItem = self.itemFromIndex(dst_parent_index)

        src_items: list[AbstractTreeItem] = src_parent_item.children[src_row: src_row + count]
        # print('items to move:', [item.path for item in src_items])

        for src_item in src_items:
            if dst_parent_item.hasAncestor(src_item):
                warn('Cannot move an item to one of its descendants.')
                return False

        self.beginMoveRows(src_parent_index, src_row, src_row + count - 1, dst_parent_index, dst_row)
        for i, src_item in enumerate(src_items):
            dst_parent_item.insertChild(dst_row + i, src_item)
            if src_parent_item is dst_parent_item:
                if src_row < dst_row:
                    dst_row -= 1
        self.endMoveRows()
        return True
    
    def removeItems(self, items: list[AbstractTreeItem]) -> bool:
        """ Calls `removeRows` to remove items from the model.

        !! The boolean return value only indicates the success for the removal of the last contiguous block of items, and thus only makes complete sense if removing a single contiguous block of items.
        """
        success: bool = False
        item_groups: list[list[AbstractTreeItem]] = self.groupItems(items)
        for item_group in item_groups:
            parent_item: AbstractTreeItem = item_group[0].parent()
            parent_index: QModelIndex = self.indexFromItem(parent_item)
            row: int = item_group[0].siblingIndex()
            count: int = len(item_group)
            success = self.removeRows(row, count, parent_index)
        # !! return value only makes complete sense if removing a single contiguous block of items
        return success
    
    def removeItem(self, item: AbstractTreeItem) -> bool:
        return self.removeItems([item])
    
    def insertItems(self, row: int, items: list[AbstractTreeItem], parent_item: AbstractTreeItem) -> bool:
        """ Calls `AbstractTreeItem.insertChild` to insert items (i.e., rows).
        
        Rempliment if you need custom logic to ensure validity of insertions.
        Otherwise you probably do not need to touch this if you have appropriately implemented `AbstractTreeItem.insertChild`.
        """
        if not items:
            return False
        n_rows: int = len(parent_item.children)
        if (row < 0) or (row > n_rows):
            return False
        parent_index: QModelIndex = self.indexFromItem(parent_item)
        count: int = len(items)
        self.beginInsertRows(parent_index, row, row + count - 1)
        for i, item in enumerate(items):
            parent_item.insertChild(row + i, item)
        self.endInsertRows()
        return True
    
    def insertItem(self, row: int, item: AbstractTreeItem, parent_item: AbstractTreeItem) -> bool:
        return self.insertItems(row, [item], parent_item)
    
    def appendItems(self, items: list[AbstractTreeItem], parent_item: AbstractTreeItem) -> bool:
        """ Calls `insertItems` to append child items.
        """
        row = len(parent_item.children)
        return self.insertItems(row, items, parent_item)
    
    def appendItem(self, item: AbstractTreeItem, parent_item: AbstractTreeItem) -> bool:
        return self.appendItems([item], parent_item)
    
    def moveItems(self, items: list[AbstractTreeItem], dst_parent_item: AbstractTreeItem, dst_row: int = -1) -> bool:
        """ Calls `moveRows` to move items within the model.

        !! The boolean return value only indicates the success for moving the last contiguous block of items, and thus only makes complete sense if moving a single contiguous block of items.
        """
        success: bool = False
        dst_parent_index: QModelIndex = self.indexFromItem(dst_parent_item)
        item_groups: list[list[AbstractTreeItem]] = self.groupItems(items)
        for item_group in item_groups:
            src_parent_item: AbstractTreeItem = item_group[0].parent()
            src_parent_index: QModelIndex = self.indexFromItem(src_parent_item)
            src_row: int = item_group[0].siblingIndex()
            count: int = len(item_group)
            success = self.moveRows(src_parent_index, src_row, count, dst_parent_index, dst_row)
        # !! return value only makes complete sense if removing a single contiguous block of items
        return success
    
    def moveItem(self, item: AbstractTreeItem, dst_parent_item: AbstractTreeItem, dst_row: int = -1) -> bool:
        return self.moveItems([item], dst_parent_item, dst_row)
    
    def transferItems(self, src_model: AbstractTreeModel, src_items: list[AbstractTreeItem], dst_model: AbstractTreeModel, dst_parent_item: AbstractTreeItem, dst_row: int = -1) -> bool:
        """ Moves items between models.

        !! The boolean return value only indicates the success for moving the last contiguous block of items, and thus only makes complete sense if moving a single contiguous block of items.
        """
        if src_model is dst_model:
            return dst_model.moveItems(src_items, dst_parent_item, dst_row)
        
        # TODO...implement transfer between different tree models
        raise NotImplementedError
    
    def transferItem(self, src_model: AbstractTreeModel, src_item: AbstractTreeItem, dst_model: AbstractTreeModel, dst_parent_item: AbstractTreeItem, dst_row: int = -1) -> bool:
        self.transferItems(src_model, [src_item], dst_model, dst_parent_item, dst_row)
    
    def groupItems(self, items: list[AbstractTreeItem]) -> list[list[AbstractTreeItem]]:
        """ Group items by their parent item and contiguous row blocks.
        
        This is used to prepare for moving or copying items in the tree.
        Note: items should never contain the root item.
        """
        root: AbstractTreeItem = self.root()
        if root in items:
            items.remove(root)
        group_parents: list[AbstractTreeItem] = []
        item_groups: list[list[AbstractTreeItem]] = []
        # group items in reverse depth-first order so that moving/removing them in order does not change the location of the remaining items
        for item in root.reverseDepthFirst():
            if item not in items:
                continue
            added = False
            for group_parent, item_group in zip(group_parents, item_groups):
                if group_parent is item.parent():
                    row: int = item.siblingIndex()
                    if row == item_group[0].siblingIndex() - 1:
                        item_group.insert(0, item)
                        added = True
                        break
            if not added:
                # start a new group
                group_parents.append(item.parent())
                item_groups.append([item])
        return item_groups
    
    def supportedDropActions(self) -> Qt.DropActions:
        return self._supportedDropActions
    
    def setSupportedDropActions(self, actions: Qt.DropActions) -> None:
        self._supportedDropActions = actions
    
    def mimeTypes(self) -> list[str]:
        """ Return the MIME types supported by this view for drag-and-drop operations.
        """
        return self._mime_types
    
    def setMimeTypes(self, mime_types :list[str]) -> None:
        self._mime_types = mime_types

    def mimeData(self, indexes: list[QModelIndex]) -> AbstractTreeMimeData | None:
        if not indexes:
            return None
        if self.root() is None:
            return None
        items: list[AbstractTreeItem] = [self.itemFromIndex(index) for index in indexes if index.isValid()]
        if not items:
            return None
        return AbstractTreeMimeData(self, items, self.MIME_TYPE)

    def dropMimeData(self, data: AbstractTreeMimeData, action: Qt.DropAction, row: int, column: int, parent_index: QModelIndex) -> bool:
        if not isinstance(data, AbstractTreeMimeData):
            return False
        if not data.hasFormat(self.MIME_TYPE):
            return False
        
        src_model: AbstractTreeModel = data.model
        src_items: list[AbstractTreeItem] = data.items
        if not src_model or not src_items:
            return False

        # move src_items to the destination (row-th child of parent_index)
        dst_model: AbstractTreeModel = self
        if dst_model.root() is None:
            return False
        dst_parent_item: AbstractTreeItem = dst_model.itemFromIndex(parent_index)
        
        # check for any move conflicts...

        self.transferItems(src_model, src_items, dst_model, dst_parent_item, row)

        # !? If we return True, the model will attempt to remove rows.
        # As we already completely handled the move, this will corrupt our model, so return False.
        return False
    
    def popupWarningDialog(self, text: str, title: str = 'Warning') -> None:
        """ Popup warning dialog at the currently focused widget.
        """
        focused_widget: QWidget = QApplication.focusWidget()
        QMessageBox.warning(focused_widget, title, text)
    
    """
    Everything below here is for path-based manipulation of the tree.
    !! This typically only makes sense if all sibling items have unique names.
       If sibling items should be able to have the same name, you probably should not use the functions below.
    """
    
    def pathFromItem(self, item: AbstractTreeItem) -> str:
        """ Path from the chain of item names up to root.
        """
        return item.path()
    
    def itemFromPath(self, path: str) -> AbstractTreeItem:
        """ Find the item associated with path starting from root.
        """
        root: AbstractTreeItem = self.root()
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

    def isValidPath(self, path: str) -> bool:
        try:
            self.itemFromPath(path)
            return True
        except:
            return False
    
    def parentPath(self, path: str) -> str | None:
        """ Get the parent path for a given path.
        """
        if path == '/':
            return None
        parts = path.split('/')
        parent_path = '/'.join(parts[:-1])
        return parent_path or '/'
    
    # def groupPaths(self, paths: list[str]) -> list[list[str]]:
    #     """ Group paths by their parent item and contiguous row blocks.
        
    #     This is used to prepare for moving or copying paths in the tree.
    #     Note: paths should never contain the root path '/'.
    #     """
    #     if '/' in paths:
    #         paths.remove('/')
    #     paths = [path for path in paths if self.isValidPath(path)]
    #     items: list[AbstractTreeItem] = [self.itemFromPath(path) for path in paths]
    #     item_groups: list[list[AbstractTreeItem]] = self.groupItems(items)
    #     path_groups: list[list[str]] = [[self.pathFromItem(item) for item in item_group] for item_group in item_groups]
    #     return path_groups
    #     # # groups[parent path][[block row indices], ...]
    #     # groups: dict[str, list[list[int]]] = {}
    #     # for path in paths:
    #     #     item: AbstractTreeItem = self.itemFromPath(path)
    #     #     parent_item: AbstractTreeItem = item.parent()  # will be valid
    #     #     parent_path: str = parent_item.path()
    #     #     if parent_path not in groups:
    #     #         groups[parent_path] = []
    #     #     row: int = item.siblingIndex()
    #     #     added = False
    #     #     rows_group: list[int]
    #     #     for rows_group in groups[parent_path]:
    #     #         if row == rows_group[0] - 1:
    #     #             rows_group.insert(0, row)
    #     #             added = True
    #     #             break
    #     #         elif row == rows_group[-1] + 1:
    #     #             rows_group.append(row)
    #     #             added = True
    #     #             break
    #     #     if not added:
    #     #         # start a new group of rows
    #     #         groups[parent_path].append([row])

    #     # # order groups by parent path from leaves to root so that moving/removing them in order does not change the paths of the remaining groups
    #     # parent_paths: list[str] = list(groups.keys())
    #     # parent_paths.sort(key=lambda p: p.count('/'), reverse=True)  # sort by depth (more slashes means deeper in the tree)
    #     # groups = {parent_path: groups[parent_path] for parent_path in parent_paths}

    #     # # order row blocks from last block to first block so that removing them in order does not change the row indices of the remaining blocks
    #     # for parent_path, row_blocks in groups.items():
    #     #     row_blocks.sort(key=lambda block: block[0], reverse=True)
        
    #     # return groups
    
    # def removePaths(self, paths: list[str]) -> None:
    #     """ Remove items by their path.
    #     """
    #     # group paths for removal block by contiguous row block
    #     path_groups: list[list[str]] = self.groupPaths(paths)
    #     for path_groups in path_groups:
    #         for row_block in row_blocks:
    #             row: int = row_block[0]
    #             count: int = len(row_block)
    #             parent_index: QModelIndex = self.indexFromPath(parent_path)
    #             self.removeRows(row, count, parent_index)
    
    # def movePaths(self, src_paths: list[str], dst_parent_path: str, dst_row: int = -1) -> None:
    #     """ Move items within tree by their path.
    #     """
    #     dst_parent_index: QModelIndex = self.indexFromPath(dst_parent_path)
    #     dst_num_rows: int = self.rowCount(dst_parent_index)
    #     if (dst_row < 0) or (dst_row > dst_num_rows):
    #         # append rows
    #         dst_row = dst_num_rows
        
    #     # group paths for moving block by contiguous row block
    #     src_path_groups: dict[str, list[list[int]]] = self.groupPaths(src_paths)
    #     for src_parent_path, row_blocks in src_path_groups.items():
    #         for row_block in row_blocks:
    #             row: int = row_block[0]
    #             count: int = len(row_block)
    #             src_parent_index: QModelIndex = self.indexFromPath(src_parent_path)
    #             self.moveRows(src_parent_index, row, count, dst_parent_index, dst_row)
    
    # def transferPaths(self, src_model: AbstractTreeModel, src_paths: list[str], dst_model: AbstractTreeModel, dst_parent_path: str, dst_row: int = -1) -> None:
    #     """ Move items by path between two different `AbstractTreeModel`s.
    #     """
    #     if src_model is dst_model:
    #         # move within the same tree model
    #         src_model.movePaths(src_paths, dst_parent_path, dst_row)
    #         return
        
    #     # TODO... implement transfer between different tree models
    #     raise NotImplementedError


class AbstractTreeMimeData(QMimeData):
    """ Custom MIME data class for drag-and-drop with `AbstractTreeModel`s.

    This class allows storing a reference to an `AbstractTreeModel` and some of its `AbstractTreeItem`s (i.e., the items being dragged during drag-and-drop) in the MIME data.
    This allows simple transfer of tree items within and between `AbstractTreeModel`s in the same program/process.

    Note:
    This approach probably won't work if you need to pass items between `AbstractTreeModel`s in separate programs/processes.
    If you really need to do this, you need to somehow serialize the dragged items (maybe with pickle), pass the serialized bytes in the drag MIME data, then deserialize back to the items on drop.
    """

    def __init__(self, model: AbstractTreeModel, items: list[AbstractTreeItem], MIME_type: str):
        QMimeData.__init__(self)

        # these define the tree items being dragged and their MIME type
        self.model: AbstractTreeModel = model
        self.items: list[AbstractTreeItem] = items
        self.MIME_type = MIME_type

        # The actual value of the data here is not important, as we won't use it.
        # Instead, we will use the above attributes to handle drag-and-drop.
        self.setData(self.MIME_type, self.MIME_type.encode('utf-8'))
    
    def hasFormat(self, MIME_type: str) -> bool:
        """ Check if the MIME data has the specified format.
        
        Overrides the default method to check for self.MIME_type.
        """
        return MIME_type == self.MIME_type or super().hasFormat(MIME_type)


def test_model():
    root = AbstractTreeItem()
    AbstractTreeItem(parent=root)
    root.appendChild(AbstractTreeItem(name='child2'))
    root.insertChild(1, AbstractTreeItem(name='child3'))
    root.children[1].appendChild(AbstractTreeItem())
    root.children[1].appendChild(AbstractTreeItem())
    root.children[1].appendChild(AbstractTreeItem())
    grandchild2 = AbstractTreeItem(name='grandchild2')
    grandchild2.setParent(root['child2'])
    AbstractTreeItem(name='greatgrandchild', parent=root['/child2/grandchild2'])

    print('\nInitial model...')
    model = AbstractTreeModel(root)
    print(model.root())

    print('\nRemove grandchild2...')
    model.removeItem(grandchild2)
    print(model.root())

    print('\nInsert grandchild2...')
    model.insertItems(0, [grandchild2], root['child2'])
    print(model.root())


if __name__ == '__main__':
    test_model()