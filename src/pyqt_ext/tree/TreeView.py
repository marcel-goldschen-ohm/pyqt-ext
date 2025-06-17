""" Tree view for an `AbstractTreeModel` with drag-and-drop, context menu, and mouse wheel expand/collapse.
"""

from __future__ import annotations
from typing import Callable, Any
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import qtawesome as qta
from pyqt_ext.tree import AbstractTreeItem, AbstractTreeModel, AbstractTreeMimeData


class TreeView(QTreeView):

    selectionWasChanged = Signal()

    VIEW_STATE_ATTR = 'view_state'

    def __init__(self, *args, **kwargs) -> None:
        QTreeView.__init__(self, *args, **kwargs)

        # general settings
        sizePolicy = self.sizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sizePolicy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        # selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # drag-n-drop
        self.setDragAndDropEnabled(True)

        # context menu defined in customContextMenu()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)
    
    def refresh(self) -> None:
        self.storeState()
        self.model().reset()
        self.restoreState()
    
    def model(self) -> AbstractTreeModel:
        model: AbstractTreeModel = super().model()
        return model
    
    def treeData(self) -> Any:
        return self.model().treeData()
    
    def setTreeData(self, data: Any) -> None:
        self.storeState()
        if self.model() is None:
            self.setModel(AbstractTreeModel(data))
        else:
            self.model().setTreeData(data)
        self.restoreState()
    
    def storeState(self, items: list[AbstractTreeItem] = None) -> None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        root: AbstractTreeItem = model.root()
        if root is None:
            return
        if items is None:
            items = list(root.depthFirst())
        
        selected: list[QModelIndex] = self.selectionModel().selectedIndexes()
        for item in items:
            if item is root:
                continue
            index: QModelIndex = model.indexFromItem(item)
            if not index.isValid():
                continue
            setattr(item, self.VIEW_STATE_ATTR, {
                'expanded': self.isExpanded(index),
                'selected': index in selected
            })

    def restoreState(self, items: list[AbstractTreeItem] = None) -> None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        root: AbstractTreeItem = model.root()
        if root is None:
            return
        if items is None:
            items = list(root.depthFirst())

        to_select: QItemSelection = QItemSelection()
        to_deselect: QItemSelection = QItemSelection()
        for item in items:
            if item is root:
                continue
            index: QModelIndex = model.indexFromItem(item)
            if not index.isValid():
                continue
            item_view_state = getattr(item, self.VIEW_STATE_ATTR, None)
            if item_view_state is None:
                continue
            isExpanded = item_view_state.get('expanded', None)
            if isExpanded is not None:
                self.setExpanded(index, isExpanded)
            isSelected = item_view_state.get('selected', None)
            if isSelected is not None:
                # flags = QItemSelectionModel.SelectionFlag.Rows
                # if isSelected:
                #     flags |= QItemSelectionModel.SelectionFlag.Select
                # else:
                #     flags |= QItemSelectionModel.SelectionFlag.Deselect
                # self.selectionModel().selection().select(index, index, flags)
                if isSelected:
                    to_select.merge(QItemSelection(index, index), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
                else:
                    to_deselect.merge(QItemSelection(index, index), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        if to_deselect.count():
            self.selectionModel().select(to_deselect, QItemSelectionModel.SelectionFlag.Deselect | QItemSelectionModel.SelectionFlag.Rows)
        if to_select.count():
            self.selectionModel().select(to_select, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
    
    @Slot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        QTreeView.selectionChanged(self, selected, deselected)
        self.selectionWasChanged.emit()

    def selectedItems(self) -> list[AbstractTreeItem]:
        model: AbstractTreeModel = self.model()
        if model is None:
            return []
        indexes: list[QModelIndex] = self.selectionModel().selectedIndexes()
        items: list[AbstractTreeItem] = [model.itemFromIndex(index) for index in indexes]
        return items
    
    def setSelectedItems(self, items: list[AbstractTreeItem]):
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        self.selectionModel().clearSelection()
        selection: QItemSelection = QItemSelection()
        flags = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
        for item in items:
            index: QModelIndex = model.indexFromItem(item)
            if not index.isValid():
                continue
            selection.merge(QItemSelection(index, index), flags)
        if selection.count():
            self.selectionModel().select(selection, flags)
    
    def removeItems(self, items: list[AbstractTreeItem]) -> None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        if not items:
            return
        self.model().removeItems(items)
    
    def removeSelectedItems(self) -> None:
        items: list[AbstractTreeItem] = self.selectedItems()
        self.removeItems(items)
    
    def askToRemoveItems(self, items: list[AbstractTreeItem], title: str = 'Remove', text: str = None) -> None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        if not items:
            return
        if text is None:
            if len(items) == 1:
                text = f'Remove {items[0].path}?'
            else:
                text = f'Remove items including {items[0].path}?'
        answer = QMessageBox.question(self, title, text, 
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            defaultButton=QMessageBox.StandardButton.No
        )
        if answer!= QMessageBox.StandardButton.Yes:
            return
        self.removeItems(items)
    
    def askToRemoveSelectedItems(self) -> None:
        items: list[AbstractTreeItem] = self.selectedItems()
        self.askToRemoveItems(items, text='Remove selected?')
    
    @Slot(QPoint)
    def onCustomContextMenuRequested(self, point: QPoint) -> None:
        index: QModelIndex = self.indexAt(point)
        menu: QMenu | None = self.customContextMenu(index)
        if menu is not None:
            menu.exec(self.viewport().mapToGlobal(point))
    
    def customContextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu | None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        
        menu = QMenu(self)

        # context menu for item that was clicked on
        if index.isValid():
            item: AbstractTreeItem = model.itemFromIndex(index)
            item_label = self.truncateLabel(item.path())
            menu.addAction(f'Remove {item_label}', lambda item=item: self.askToRemoveItems([item]))
            menu.addSeparator()
        
        self.appendDefaultContextMenu(menu)
        return menu
    
    def appendDefaultContextMenu(self, menu: QMenu) -> None:
        """ Append the default context menu items to the input menu.
        """
        menu.addAction('Expand All', self.expandAll)
        menu.addAction('Collapse All', self.collapseAll)
        if self.model().columnCount() > 1:
            menu.addAction('Resize Columns to Contents', self.resizeAllColumnsToContents)
            menu.addAction('Show All', self.showAll)
        
        if self.selectionMode() in [QAbstractItemView.SelectionMode.ContiguousSelection, QAbstractItemView.SelectionMode.ExtendedSelection, QAbstractItemView.SelectionMode.MultiSelection]:
            menu.addSeparator()
            menu.addAction('Select All', self.selectAll)
            menu.addAction('Select None', self.clearSelection)
        
        if len(self.selectedPaths()) > 1:
            menu.addSeparator()
            menu.addAction('Remove Selected', self.askToRemoveSelectedItems)

        menu.addSeparator()
        menu.addAction('Refresh', self.refresh)
    
    def truncateLabel(self, label: str, max_length: int = 50) -> str:
        """ Truncate long strings from the beginning.
        
        e.g., '...<end of label>'
        This preserves the final part of any tree paths used as labels.
        """
        if len(label) <= max_length:
            return label
        return '...' + label[-(max_length - 3):]
    
    def expandAll(self) -> None:
        QTreeView.expandAll(self)
        # store current expanded depth
        self._expanded_depth_ = self.model().maxDepth()
    
    def collapseAll(self) -> None:
        QTreeView.collapseAll(self)
        self._expanded_depth_ = 0
    
    def expandToDepth(self, depth: int) -> None:
        depth = max(0, min(depth, self.model().maxDepth()))
        if depth == 0:
            self.collapseAll()
            return
        QTreeView.expandToDepth(self, depth - 1)
        self._expanded_depth_ = depth
    
    def resizeAllColumnsToContents(self) -> None:
        for col in range(self.model().columnCount()):
            self.resizeColumnToContents(col)
    
    def showAll(self) -> None:
        self.expandAll()
        self.resizeAllColumnsToContents()
    
    def eventFilter(self, obj: QObject, event: QEvent) -> None:
        if event.type() == QEvent.Type.Wheel:
            # modifiers: Qt.KeyboardModifier = event.modifiers()
            # if Qt.KeyboardModifier.ControlModifier in modifiers \
            # or Qt.KeyboardModifier.AltModifier in modifiers \
            # or Qt.KeyboardModifier.MetaModifier in modifiers:
            #     self.mouseWheelEvent(event)
            #     return True
            self.mouseWheelEvent(event)
            return True
        # elif event.type() == QEvent.Type.FocusIn:
        #     print('FocusIn')
        #     # self.showDropIndicator(True)
        # elif event.type() == QEvent.Type.FocusOut:
        #     print('FocusOut')
        #     # self.showDropIndicator(False)
        return QTreeView.eventFilter(self, obj, event)
    
    def mouseWheelEvent(self, event: QWheelEvent) -> None:
        delta: int = event.angleDelta().y()
        depth = getattr(self, '_expanded_depth_', 0)
        if delta > 0:
            self.expandToDepth(depth + 1)
        elif delta < 0:
            self.expandToDepth(depth - 1)
    
    def setDragAndDropEnabled(self, enabled: bool) -> None:
        if enabled:
            self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
            self.setDefaultDropAction(Qt.DropAction.MoveAction)
        else:
            self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.setDragEnabled(enabled)
        self.setAcceptDrops(enabled)
        self.viewport().setAcceptDrops(enabled)
        self.setDropIndicatorShown(enabled)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime_data = event.mimeData()
        if isinstance(mime_data, AbstractTreeMimeData) and (mime_data.model is self.model()):
            # Store the current state of the dragged paths and all their descendent paths in the MIME data.
            # We only want to do this for the model where the drag was initiated (i.e., mime_data.model).
            # We'll use this stored state in the dropEvent to restore the view of the dropped items.
            self.storeState(mime_data.items)
        QTreeView.dragEnterEvent(self, event)
    
    def dropEvent(self, event: QDropEvent) -> None:
        mime_data = event.mimeData()
        QTreeView.dropEvent(self, event)
        if isinstance(mime_data, AbstractTreeMimeData):
            # update state of dragged items as specified in the MIME data
            self.restoreState(mime_data.items)
    
    """
    Everything below here is for path-based manipulation of the tree.
    !! This typically only makes sense if all sibling items have unique names.
       If sibling items should be able to have the same name, you probably should not use the functions below.
    """
    
    def selectedPaths(self) -> list[str]:
        items: list[AbstractTreeItem] = self.selectedItems()
        paths: list[str] = [item.path() for item in items]
        return paths
    
    def setSelectedPaths(self, paths: list[str]):
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        items: list[AbstractTreeItem] = [model.itemFromPath(path) for path in paths]
        self.setSelectedItems(items)
    
    def removePaths(self, paths: list[str]) -> None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        items: list[AbstractTreeItem] = [model.itemFromPath(path) for path in paths]
        self.removeItems(items)
    
    def askToRemovePaths(self, paths: list[str], title: str = 'Remove', text: str = None) -> None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        items: list[AbstractTreeItem] = [model.itemFromPath(path) for path in paths]
        self.askToRemoveItems(items, title, text)
    
    def askToRemoveSelectedPaths(self) -> None:
        paths: list[str] = self.selectedPaths()
        self.askToRemovePaths(paths, text='Remove selected?')


def test_live():
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
    print(root)

    app = QApplication()
    model = AbstractTreeModel(root)
    view = TreeView()
    view.setModel(model)
    view.show()
    view.resize(QSize(800, 600))
    view.showAll()
    app.exec()
    print(root)


if __name__ == '__main__':
    test_live()
