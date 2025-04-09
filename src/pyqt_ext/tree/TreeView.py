""" Tree view for an AbstractTreeModel with context menu and mouse wheel expand/collapse.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import AbstractTreeItem, AbstractTreeModel


class TreeView(QTreeView):
    """ Tree view for an AbstractTreeModel with context menu and mouse wheel expand/collapse.
    """

    selectionWasChanged = Signal()

    def __init__(self, parent: QObject = None) -> None:
        QTreeView.__init__(self, parent)
        sizePolicy = self.sizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sizePolicy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.setAlternatingRowColors(True)

        # selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        # these will appear in the item's context menu
        self._itemContextMenuFunctions: list[tuple[str, Callable[[AbstractTreeItem]]]] = [
            # ('Print', print),
            # ('Separator', None),
            ('Remove', lambda item, self=self: self.askToRemoveItem(item)),
        ]
    
    def setModel(self, model: AbstractTreeModel):
        QTreeView.setModel(self, model)

        # drag and drop?
        is_dnd: bool = model is not None and model.supportedDropActions() != Qt.DropAction.IgnoreAction
        self.setDragEnabled(is_dnd)
        self.setAcceptDrops(is_dnd)
        self.viewport().setAcceptDrops(is_dnd)
        self.setDropIndicatorShown(is_dnd)
        if is_dnd:
            self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
            self.setDefaultDropAction(Qt.DropAction.MoveAction)
        else:
            self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
    
    def resetModel(self):
        self.storeState()
        self.model().setRoot(self.model().root())
        self.restoreState()
    
    @Slot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        QTreeView.selectionChanged(self, selected, deselected)
        self.selectionWasChanged.emit()

    def selectedItems(self, column: int | None = 0) -> list[AbstractTreeItem]:
        model: AbstractTreeModel = self.model()
        if model is None:
            return []
        indexes: list[QModelIndex] = self.selectionModel().selectedIndexes()
        if column is not None:
            indexes = [index for index in indexes if index.column() == column]
        items: list[AbstractTreeItem] = [model.itemFromIndex(index) for index in indexes]
        return items
    
    def selectedPaths(self) -> list[str]:
        return [item.path for item in self.selectedItems()]
    
    def setSelectedPaths(self, paths: list[str]):
        model: AbstractTreeModel = self.model()
        self.selectionModel().clearSelection()
        selection: QItemSelection = QItemSelection()
        for item in model.root().depth_first():
            if item is model.root():
                continue
            index: QModelIndex = model.indexFromItem(item)
            if index.column() != 0:
                continue
            path: str = item.path
            if path in paths or path.lstrip('/') in paths:
                selection.merge(QItemSelection(index, index), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        if selection.count():
            self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
    
    @Slot(QPoint)
    def onCustomContextMenuRequested(self, point: QPoint):
        index: QModelIndex = self.indexAt(point)
        menu: QMenu = self.contextMenu(index)
        if menu is not None:
            menu.exec(self.viewport().mapToGlobal(point))
    
    def contextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu | None:
        model: AbstractTreeModel = self.model()
        if model is None:
            return None
        
        menu: QMenu = QMenu(self)

        # context menu for item that was clicked on
        if index.isValid() and len(self._itemContextMenuFunctions) > 0:
            item: AbstractTreeItem = model.itemFromIndex(index)
            label = self.truncateLabel(item.path)
            item_menu = QMenu(label)
            for key, func in self._itemContextMenuFunctions:
                if key.lower() == 'separator' and func is None:
                    item_menu.addSeparator()
                else:
                    item_menu.addAction(key, lambda item=item, func=func: func(item))
            menu.addMenu(item_menu)
            menu.addSeparator()
        
        menu.addAction('Expand all', self.expandAll)
        menu.addAction('Collapse all', self.collapseAll)
        if model.columnCount() > 1:
            menu.addAction('Resize columns to contents', self.resizeAllColumnsToContents)
        
        if self.selectionMode() in [QAbstractItemView.ContiguousSelection, QAbstractItemView.ExtendedSelection, QAbstractItemView.MultiSelection]:
            menu.addSeparator()
            menu.addAction('Select all', self.selectAll)
            menu.addAction('Clear selection', self.clearSelection)
        
        if len(self.selectedItems()) > 1:
            menu.addSeparator()
            menu.addAction('Remove all selected items', self.removeSelectedItems)
        
        return menu

    def truncateLabel(self, label: str, max_length: int = 50) -> str:
        """ Truncate long strings from the beginning.
        
        e.g., '...<end of label>'
        This preserves the final part of any tree paths used as labels.
        """
        if len(label) <= max_length:
            return label
        return '...' + label[-(max_length - 3):]
    
    def expandAll(self):
        QTreeView.expandAll(self)
        try:
            model: AbstractTreeModel = self.model()
            self._depth = model.maxDepth() - 1
        except:
            pass
    
    def collapseAll(self):
        QTreeView.collapseAll(self)
        self._depth = 0
    
    def expandToDepth(self, depth: int):
        model: AbstractTreeModel = self.model()
        if model is not None:
            depth = max(0, min(depth, model.maxDepth() - 1))
            if depth == 0:
                self.collapseAll()
                return
        QTreeView.expandToDepth(self, depth - 1)
        self._depth = depth
    
    def resizeAllColumnsToContents(self):
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        for col in range(model.columnCount()):
            self.resizeColumnToContents(col)
    
    def askToRemoveItem(self, item: AbstractTreeItem, label: str = None):
        if label is None:
            label = item.name
        answer = QMessageBox.question(self, 'Remove', f'Remove {label}?', 
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            defaultButton=QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.StandardButton.Yes:
            model: AbstractTreeModel = self.model()
            model.removeItem(item)
    
    def removeSelectedItems(self, ask_before_removing: bool = True):
        items: list[AbstractTreeItem] = self.selectedItems()
        if not items:
            return
        if ask_before_removing:
            answer = QMessageBox.question(self, 'Remove', f'Remove selected items?', 
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                defaultButton=QMessageBox.StandardButton.No
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        model: AbstractTreeModel = self.model()
        for item in reversed(items):
            model.removeItem(item)
    
    def eventFilter(self, obj: QObject, event: QEvent):
        if event.type() == QEvent.Wheel:
            modifiers: Qt.KeyboardModifier = event.modifiers()
            if Qt.KeyboardModifier.ControlModifier in modifiers \
            or Qt.KeyboardModifier.AltModifier in modifiers \
            or Qt.KeyboardModifier.MetaModifier in modifiers:
                self.mouseWheelEvent(event)
                return True
        # elif event.type() == QEvent.FocusIn:
        #     print('FocusIn')
        #     # self.showDropIndicator(True)
        # elif event.type() == QEvent.FocusOut:
        #     print('FocusOut')
        return QTreeView.eventFilter(self, obj, event)
    
    def mouseWheelEvent(self, event: QWheelEvent):
        delta: int = event.angleDelta().y()
        depth = getattr(self, '_depth', 0)
        if delta > 0:
            self.expandToDepth(depth + 1)
        elif delta < 0:
            self.expandToDepth(depth - 1)
    
    # def mousePressEvent(self, event: QMouseEvent):
    #     if self.selectionMode() != QAbstractItemView.SelectionMode.SingleSelection:
    #         if event.button() == Qt.MouseButton.LeftButton:
    #             index: QModelIndex = self.indexAt(event.pos())
    #             if not index.isValid():
    #                 self.selectionModel().clearSelection()
    #     QTreeView.mousePressEvent(self, event)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        # print('dragEnterEvent   ', event.mimeData().formats(), event.possibleActions())
        index: QModelIndex = event.source().currentIndex()
        if index.isValid() and index != QModelIndex():
            # because we have to clear a stupidly persisting drop indicator on each drop
            self.setDropIndicatorShown(True)

            # Not sure if this is needed?
            self.storeState()

            event.accept()
        else:
            event.ignore()
    
    # def dragMoveEvent(self, event: QDragMoveEvent):
    #     QTreeView.dragMoveEvent(self, event)
    
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        # This prevents the drop indicator from being hidden
        # when the mouse leaves the widget while dragging,
        # by not calling the default implementation of dragLeaveEvent.
        # The problem with the default behavior is that the drop indicator
        # doesn't reappear when the mouse re-enters the widget!
        # print('dragLeaveEvent')
        event.accept()
    
    def dropEvent(self, event: QDropEvent):
        # print('dropEvent')
        
        model: AbstractTreeModel = self.model()
        if model is None:
            event.ignore()
            return
        
        src_index: QModelIndex = event.source().currentIndex()
        if (src_index is None) or (not src_index.isValid()) or (src_index == QModelIndex()):
            event.ignore()
            return
        
        dst_index: QModelIndex = self.indexAt(event.pos())
        if (dst_index is None):
            event.ignore()
            return
        
        dst_parent_index: QModelIndex = model.parent(dst_index)
        dst_row = dst_index.row()

        drop_pos = self.dropIndicatorPosition()
        if drop_pos == QAbstractItemView.DropIndicatorPosition.OnViewport:
            dst_parent_index = QModelIndex()
            dst_row = model.rowCount(dst_parent_index)
        elif drop_pos == QAbstractItemView.DropIndicatorPosition.OnItem:
            dst_parent_index = dst_index
            dst_row = model.rowCount(dst_parent_index)
        elif drop_pos == QAbstractItemView.DropIndicatorPosition.AboveItem:
            pass
        elif drop_pos == QAbstractItemView.DropIndicatorPosition.BelowItem:
            dst_row += 1
        
        src_indices: list[QModelIndex] = [index for index in self.selectionModel().selectedIndexes() if index.column() == 0]

        if event.dropAction() == Qt.DropAction.MoveAction:
            # move selected rows onto drop target
            num_moved = 0
            # handle in reverse so rows are not invalidated
            for src_index in reversed(src_indices):
                if (src_index is None) or (not src_index.isValid()) or (src_index == QModelIndex()):
                    continue
        
                src_parent_index: QModelIndex = model.parent(src_index)
                src_row = src_index.row()
        
                try:
                    success: bool = model.moveRow(src_parent_index, src_row, dst_parent_index, dst_row)
                    num_moved += int(success)
                    if success:
                        if src_parent_index == dst_parent_index:
                            if src_row < dst_row:
                                dst_row -= 1
                except Exception as err:
                    QMessageBox.warning(self, 'Move Error', f'{err}')

            # We already handled the drop event, so ignore the default implementation.
            event.ignore()

            # Not sure if this is needed?
            self.restoreState()
            
            # Make sure moved rows are selected.
            self.selectionModel().clearSelection()
            selection: QItemSelection = QItemSelection()
            for row in range(dst_row, dst_row + num_moved):
                index = model.index(row, 0, dst_parent_index)
                selection.merge(QItemSelection(index, index), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
            self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)

        # clear persisting drop indicator !?
        self.setDropIndicatorShown(False)
    
    # def dropMimeData(self, index: QModelIndex, data: QMimeData, action: Qt.DropAction) -> bool:
    #     print('dropMimeData')
    #     return False
    
    # def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
    #     print('canDropMimeData')
    #     return True
    
    def storeState(self):
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        if not hasattr(self, '_state'):
            self._state = {}
        selected: list[QModelIndex] = self.selectionModel().selectedIndexes()
        for item in model.root().depth_first():
            if item is model.root():
                continue
            index: QModelIndex = model.indexFromItem(item)
            path = item.path
            self._state[path] = {
                'expanded': self.isExpanded(index),
                'selected': index in selected
            }

    def restoreState(self):
        model: AbstractTreeModel = self.model()
        if model is None:
            return
        if not hasattr(self, '_state'):
            return
        self.selectionModel().clearSelection()
        selection: QItemSelection = QItemSelection()
        for item in model.root().depth_first():
            if item is model.root():
                continue
            index: QModelIndex = model.indexFromItem(item)
            path = item.path
            if path in self._state:
                isExpanded = self._state[path].get('expanded', False)
                self.setExpanded(index, isExpanded)
                isSelected = self._state[path].get('selected', False)
                if isSelected:
                    selection.merge(QItemSelection(index, index), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        if selection.count():
            self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)


def test_live():
    from pyqt_ext.tree import AbstractDndTreeModel

    app = QApplication()

    root = AbstractTreeItem()
    root.append_child(AbstractTreeItem())
    root.append_child(AbstractTreeItem())
    root.append_child(AbstractTreeItem())
    root.children[-1].append_child(AbstractTreeItem())
    root.children[-1].append_child(AbstractTreeItem())
    root.children[-1].append_child(AbstractTreeItem())
    root.children[-1].children[0].append_child(AbstractTreeItem())
    root.children[-1].children[0].append_child(AbstractTreeItem())
    
    model = AbstractDndTreeModel(root)
    view = TreeView()
    view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    view.setModel(model)
    view.show()
    view.resize(QSize(600, 600))
    view.expandAll()
    view.resizeAllColumnsToContents()

    # view.selectAll()
    # paths = view.selectedPaths()
    # print(paths)
    # view.setSelectedPaths(paths[-2:])
    # print(view.selectedPaths())

    app.exec()


if __name__ == '__main__':
    test_live()
