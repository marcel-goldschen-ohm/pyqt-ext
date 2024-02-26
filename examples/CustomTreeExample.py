from __future__ import annotations
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QModelIndex
from pyqt_ext.tree import AbstractTreeItem, AbstractTreeModel, AbstractDndTreeModel, AbstractTreeView


class CustomTreeItem(AbstractTreeItem):
    """ Custom tree item for an editable tree with two columns: name, data.
    
    Contains a `data` attribute to store the data for each item and implementations of `get_data` and `set_data` methods for an editable tree with two columns: name, data.
    """

    def __init__(self, data = None, name: str = None, parent: CustomTreeItem = None):
        # the data associated with this tree item
        self.data = data
        # tree linkage
        AbstractTreeItem.__init__(self, name, parent)
    
    def __repr__(self):
        # return 'name: data'
        return AbstractTreeItem.__repr__(self) + f': {self.data}'
    
    # For an editable tree with two columns: name, data...

    def get_data(self, column: int):
        if column == 0:
            return self.name
        elif column == 1:
            return self.data
    
    def set_data(self, column: int, value) -> bool:
        if column == 0:
            self.name = value
            return True
        elif column == 1:
            self.data = value
            return True
        return False


class CustomDndTreeModel(AbstractDndTreeModel):
    """ Custom tree model (with drag and drop) for an editable tree with two columns.
    """

    def __init__(self, root: CustomTreeItem = None, parent: QObject = None):
        AbstractDndTreeModel.__init__(self, root, parent)
        # column titles
        self.setColumnLabels(['Name', 'Data'])

    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        # for [name, data] columns
        return 2


def customTreeExample():
    # Create the application
    app = QApplication()

    print('Build the tree...')
    root = CustomTreeItem()
    CustomTreeItem(data=82, parent=root)
    root.append_child(CustomTreeItem(data=[1, 2, 3], name='child2'))
    root.insert_child(1, CustomTreeItem(data=3.14, name='child3'))
    root.children[1].append_child(CustomTreeItem(data='some cool data'))
    grandchild2 = CustomTreeItem(data=False, name='grandchild2')
    grandchild2.parent = root['child2']
    CustomTreeItem(name='greatgrandchild', parent=root['/child2/grandchild2'])
    print(root)

    print('Depth first iteration...')
    for item in root.depth_first():
        print(item.name)
    
    # Tree model with drag and drop enabled...
    model = CustomDndTreeModel(root)

    # To access the underlying item tree...
    #root = model.root()

    # To reset the underlying item tree...
    #model.setRoot(root)

    # Tree view widget with default behavior...
    view = AbstractTreeView()
    view.setModel(model)
    view.expandAll()
    view.resizeAllColumnsToContents()
    view.show()

    # Run the application...
    app.exec()


if __name__ == '__main__':
    customTreeExample()
