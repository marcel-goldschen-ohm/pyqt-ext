from __future__ import annotations
from PySide6.QtWidgets import QApplication
from pyqt_ext.tree import KeyValueTreeItem, KeyValueDndTreeModel, KeyValueTreeView


def keyValueTreeExample():
    # Create the application
    app = QApplication()

    # (key, value) data hierarchy...
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

    print('Build the tree...')
    root = KeyValueTreeItem('/', data)
    print(root)
    
    # Tree model with drag and drop enabled...
    model = KeyValueDndTreeModel(root)

    # Tree view widget with default behavior...
    view = KeyValueTreeView()
    view.setModel(model)
    view.expandAll()
    view.resizeAllColumnsToContents()
    view.show()

    # Run the application...
    app.exec()


if __name__ == '__main__':
    keyValueTreeExample()
