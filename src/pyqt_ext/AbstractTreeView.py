""" Base class for a tree view of an AbstractTreeModel with context menu and mouse wheel expand/collapse.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeItem, AbstractTreeModel


class AbstractTreeView(QTreeView):
    """ Base class for a tree view with context menu and mouse wheel expand/collapse.
    """

    selectionWasChanged = Signal()

    def __init__(self, parent: QObject = None) -> None:
        QTreeView.__init__(self, parent)
        sizePolicy = self.sizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sizePolicy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setAlternatingRowColors(True)

        # selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        # keep track of depth
        self._depth: int = 0
    
    def setModel(self, model: AbstractTreeModel):
        QTreeView.setModel(self, model)

        # drag and drop?
        is_dnd: bool = model.supportedDropActions() != Qt.DropAction.IgnoreAction
        self.setDragEnabled(is_dnd)
        self.setAcceptDrops(is_dnd)
        self.viewport().setAcceptDrops(is_dnd)
        self.setDropIndicatorShown(is_dnd)
        if is_dnd:
            self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
            self.setDefaultDropAction(Qt.DropAction.MoveAction)
        else:
            self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
    
    @Slot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        QTreeView.selectionChanged(self, selected, deselected)
        self.selectionWasChanged.emit()

    @Slot(QPoint)
    def onCustomContextMenuRequested(self, point: QPoint):
        index: QModelIndex = self.indexAt(point)
        menu: QMenu = self.contextMenu(index)
        if menu is not None:
            menu.exec(self.viewport().mapToGlobal(point))
    
    def contextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu:
        menu: QMenu = QMenu(self)
        menu.addAction('Expand All', self.expandAll)
        menu.addAction('Collapse All', self.collapseAll)
        menu.addAction('Resize Columns to Contents', self.resizeAllColumnsToContents)
        if self.selectionMode() in [QAbstractItemView.ContiguousSelection, QAbstractItemView.ExtendedSelection, QAbstractItemView.MultiSelection]:
            menu.addSeparator()
            menu.addAction('Select All', self.selectAll)
            menu.addAction('Clear Selection', self.clearSelection)
        return menu
    
    @Slot()
    def expandAll(self):
        QTreeView.expandAll(self)
        model: AbstractTreeModel = self.model()
        if model is not None:
            self._depth = model.maxDepth()
    
    @Slot()
    def collapseAll(self):
        QTreeView.collapseAll(self)
        self._depth = 0
    
    @Slot(int)
    def expandToDepth(self, depth: int):
        model: AbstractTreeModel = self.model()
        if model is not None:
            depth = max(0, min(depth, model.maxDepth()))
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
    
    def eventFilter(self, obj: QObject, event: QEvent):
        if event.type() == QEvent.Wheel:
            modifiers: Qt.KeyboardModifier = event.modifiers()
            if Qt.KeyboardModifier.ControlModifier in modifiers \
            or Qt.KeyboardModifier.AltModifier in modifiers \
            or Qt.KeyboardModifier.MetaModifier in modifiers:
                self.mouseWheelEvent(event)
                return True
        return QTreeView.eventFilter(self, obj, event)
    
    def mouseWheelEvent(self, event: QWheelEvent):
        delta: int = event.angleDelta().y()
        if delta > 0:
            self.expandToDepth(self._depth + 1)
        elif delta < 0:
            self.expandToDepth(self._depth - 1)
    
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
            self._src_index = index
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        src_index: QModelIndex = getattr(self, '_src_index', None)
        if (src_index is None) or (not src_index.isValid()) or (src_index == QModelIndex()):
            event.ignore()
            return
        dst_index: QModelIndex = self.indexAt(event.pos())
        
        model: AbstractTreeModel = self.model()
        src_parent_index: QModelIndex = model.parent(src_index)
        src_row = src_index.row()
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
        
        src_item: AbstractTreeItem = model.itemFromIndex(src_index)
        dst_parent_item: AbstractTreeItem = model.itemFromIndex(dst_parent_index)
        if dst_parent_item.hasAncestor(src_item):
            event.ignore()
            return
        
        if event.dropAction() == Qt.DropAction.MoveAction:
            # old_max_depth = model.max_depth()
            model.moveRow(src_parent_index, src_row, dst_parent_index, dst_row)
            # moved_index = model.index(dst_row, 0, dst_parent_index)
            # model.infoChanged.emit(moved_index)
            # new_max_depth = model.max_depth()
            # if new_max_depth != old_max_depth:
            #     model.maxDepthChanged.emit(new_max_depth)
        else:
            event.ignore()
            return

        # We already handled the drop event, so ignore the default implementation.
        event.setDropAction(Qt.DropAction.IgnoreAction)
        event.accept()
    
    # def dropMimeData(self, index: QModelIndex, data: QMimeData, action: Qt.DropAction) -> bool:
    #     print('dropMimeData')
    #     return False
    
    # def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
    #     print('canDropMimeData')
    #     return True


def test_live():
    from pyqt_ext.AbstractTreeModel import AbstractDndTreeModel

    app = QApplication()

    root = AbstractTreeItem()
    root.insertChildren(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].insertChildren(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].children[0].insertChildren(0, [AbstractTreeItem(), AbstractTreeItem()])
    # root.dump()
    
    model = AbstractDndTreeModel(root)
    view = AbstractTreeView()
    view.setModel(model)
    view.show()
    view.resize(QSize(600, 600))
    view.expandAll()
    view.resizeAllColumnsToContents()

    app.exec()


if __name__ == '__main__':
    test_live()
