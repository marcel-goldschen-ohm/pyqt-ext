""" Tree view for a KeyValueTreeModel with context menu and mouse wheel expand/collapse.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import TreeView, KeyValueTreeItem, KeyValueTreeModel


class KeyValueTreeView(TreeView):

    def __init__(self, parent: QObject = None) -> None:
        TreeView.__init__(self, parent)
    
    def contextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu:
        menu: QMenu = TreeView.contextMenu(self, index)
       
        model: KeyValueTreeModel = self.model()
        if not index.isValid():
            if model.root() is not None and not model.root().children:
                menu.addSeparator()
                menu.addMenu(self._insertMenu(parentIndex=QModelIndex(), row=0, title='Add'))
            return menu
        
        item: KeyValueTreeItem = model.itemFromIndex(index)
        menu.addSeparator()
        menu.addMenu(self._insertMenu(parentIndex=model.parent(index), row=item.sibling_index, title='Insert before'))
        menu.addMenu(self._insertMenu(parentIndex=model.parent(index), row=item.sibling_index + 1, title='Insert after'))
        if item.is_container():
            menu.addMenu(self._insertMenu(parentIndex=index, row=len(item.children), title='Append child'))
        
        menu.addSeparator()
        menu.addAction('Delete', lambda item=item: self.askToRemoveItem(item))
        return menu
    
    def _insertMenu(self, parentIndex: QModelIndex, row: int, title: str = 'Insert') -> QMenu:
        model: KeyValueTreeModel = self.model()
        menu: QMenu = QMenu(title)
        menu.addAction('int', lambda model=model, row=row, item=KeyValueTreeItem('int', int(0)), parentIndex=parentIndex: model.insertItems(row, [item], parentIndex))
        menu.addAction('float', lambda model=model, row=row, item=KeyValueTreeItem('float', float(0)), parentIndex=parentIndex: model.insertItems(row, [item], parentIndex))
        menu.addAction('bool', lambda model=model, row=row, item=KeyValueTreeItem('bool', False), parentIndex=parentIndex: model.insertItems(row, [item], parentIndex))
        menu.addAction('str', lambda model=model, row=row, item=KeyValueTreeItem('str', ''), parentIndex=parentIndex: model.insertItems(row, [item], parentIndex))
        menu.addAction('dict', lambda model=model, row=row, item=KeyValueTreeItem('dict', {}), parentIndex=parentIndex: model.insertItems(row, [item], parentIndex))
        menu.addAction('list', lambda model=model, row=row, item=KeyValueTreeItem('list', []), parentIndex=parentIndex: model.insertItems(row, [item], parentIndex))
        return menu
    
    def askToRemoveItem(self, item: KeyValueTreeItem):
        item_path = item.path
        if len(item_path) > 50:
            item_path = '...' + item_path[-47:]
        TreeView.askToRemoveItem(self, item, label=item_path)


def test_live():
    from pyqt_ext.tree import KeyValueDndTreeModel
    
    app = QApplication()

    data = {
        'a': 1,
        'b': [4, 8, 9, 5, 7, 99],
        'c': {
            'me': 'hi',
            3: 67,
            'd': {
                'e': 3,
                'f': 'ya!',
                'g': 5,
            },
        },
    }
    root = KeyValueTreeItem('/', data)
    model = KeyValueDndTreeModel(root)
    view = KeyValueTreeView()
    view.setModel(model)
    view.show()
    view.resize(QSize(400, 400))

    app.exec()

if __name__ == '__main__':
    test_live()
