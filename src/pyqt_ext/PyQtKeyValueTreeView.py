""" Tree view for a KeyValueTreeModel with context menu and mouse wheel expand/collapse.
"""

from __future__ import annotations

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeView, KeyValueTreeItem, KeyValueTreeModel


class KeyValueTreeView(AbstractTreeView):

    def __init__(self, parent: QObject = None) -> None:
        AbstractTreeView.__init__(self, parent)
    
    def contextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu:
        menu: QMenu = AbstractTreeView.contextMenu(self, index)
        if not index.isValid():
            return menu
        model: KeyValueTreeModel = self.model()
        item: KeyValueTreeItem = model.get_item(index)
        parent_index: QModelIndex = model.parent(index)
        menu.addSeparator()
        insert_menu: QMenu = QMenu('Insert')
        insert_menu.addAction('int', lambda model=model, row=item.row(), item=KeyValueTreeItem('int', int(0)), parent_index=parent_index: model.insert_items(row, [item], parent_index))
        insert_menu.addAction('float', lambda model=model, row=item.row(), item=KeyValueTreeItem('float', float(0)), parent_index=parent_index: model.insert_items(row, [item], parent_index))
        insert_menu.addAction('bool', lambda model=model, row=item.row(), item=KeyValueTreeItem('bool', False), parent_index=parent_index: model.insert_items(row, [item], parent_index))
        insert_menu.addAction('str', lambda model=model, row=item.row(), item=KeyValueTreeItem('str', ''), parent_index=parent_index: model.insert_items(row, [item], parent_index))
        insert_menu.addAction('dict', lambda model=model, row=item.row(), item=KeyValueTreeItem('dict', {}), parent_index=parent_index: model.insert_items(row, [item], parent_index))
        insert_menu.addAction('list', lambda model=model, row=item.row(), item=KeyValueTreeItem('list', []), parent_index=parent_index: model.insert_items(row, [item], parent_index))
        menu.addMenu(insert_menu)
        if item.is_dict() or item.is_list():
            append_menu: QMenu = QMenu('Append Child')
            append_menu.addAction('int', lambda model=model, row=-1, item=KeyValueTreeItem('int', int(0)), parent_index=index: model.insert_items(row, [item], parent_index))
            append_menu.addAction('float', lambda model=model, row=-1, item=KeyValueTreeItem('float', float(0)), parent_index=index: model.insert_items(row, [item], parent_index))
            append_menu.addAction('bool', lambda model=model, row=-1, item=KeyValueTreeItem('bool', False), parent_index=index: model.insert_items(row, [item], parent_index))
            append_menu.addAction('str', lambda model=model, row=-1, item=KeyValueTreeItem('str', ''), parent_index=index: model.insert_items(row, [item], parent_index))
            append_menu.addAction('dict', lambda model=model, row=-1, item=KeyValueTreeItem('dict', {}), parent_index=index: model.insert_items(row, [item], parent_index))
            append_menu.addAction('list', lambda model=model, row=-1, item=KeyValueTreeItem('list', []), parent_index=index: model.insert_items(row, [item], parent_index))
            menu.addMenu(append_menu)
        menu.addSeparator()
        menu.addAction('Delete', lambda model=model, item=item: model.remove_item(item))
        return menu


def test_live():
    import sys
    app = QApplication(sys.argv)

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
    model = KeyValueTreeModel(root)
    view = KeyValueTreeView()
    view.setModel(model)
    view.show()
    view.resize(QSize(400, 400))

    sys.exit(app.exec())

if __name__ == '__main__':
    test_live()
