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

    selection_changed = Signal()

    def __init__(self, parent: QObject = None) -> None:
        QTreeView.__init__(self, parent)
        sizePolicy = self.sizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sizePolicy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setAlternatingRowColors(True)

        # selection
        # self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        # self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        # keep track of depth
        self._depth: int = 0
    
    @Slot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        QTreeView.selectionChanged(self, selected, deselected)
        self.selection_changed.emit()

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
        self._depth = self.model().max_depth()
    
    @Slot()
    def collapseAll(self):
        QTreeView.collapseAll(self)
        self._depth = 0
    
    @Slot(int)
    def expandToDepth(self, depth: int):
        depth = max(0, min(depth, self.model().max_depth()))
        if depth == 0:
            self.collapseAll()
            return
        QTreeView.expandToDepth(self, depth - 1)
        self._depth = depth
    
    def resizeAllColumnsToContents(self):
        model: AbstractTreeModel = self.model()
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


def test_live():
    import sys
    app = QApplication(sys.argv)

    root = AbstractTreeItem()
    root.insert_children(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].insert_children(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].children[0].insert_children(0, [AbstractTreeItem(), AbstractTreeItem()])
    # root.dump()
    
    model = AbstractTreeModel(root)
    view = AbstractTreeView()
    view.setModel(model)
    view.show()
    view.resize(QSize(600, 600))
    view.expandAll()
    view.resizeAllColumnsToContents()

    sys.exit(app.exec())


if __name__ == '__main__':
    test_live()
