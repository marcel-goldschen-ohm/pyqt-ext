from __future__ import annotations
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from pyqt_ext.tree import AbstractTreeItem, AbstractTreeModel, TreeView


class CustomTreeItem(AbstractTreeItem):
    """ Custom tree item with arbitrary data stored in the `data` attribute.
    """

    def __init__(self, data = None, name: str = None, parent: CustomTreeItem = None):
        # the data associated with this tree item
        self.data = data
        
        # tree linkage
        AbstractTreeItem.__init__(self, name, parent)
    
    def __repr__(self):
        return f'{self.name()}: {self.data}'


class CustomTreeModel(AbstractTreeModel):
    """ Custom tree model with two columns (Name, Data).
    """

    def __init__(self, *args, **kwargs):
        AbstractTreeModel.__init__(self, *args, **kwargs)
        self.setColumnLabels(['Name', 'Data'])

    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        return 2

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return
        item: CustomTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return item.name()
            elif index.column() == 1:
                return item.data

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if not index.isValid():
            return False
        item: CustomTreeItem = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                item.setName(value)
                self.dataChanged.emit(index, index)  # ?? needed?
                return True
            elif index.column() == 1:
                item.data = value
                self.dataChanged.emit(index, index)  # ?? needed?
                return True
        return False


# Create the application
app = QApplication()

print('\nBuild the tree...')
root = CustomTreeItem()
CustomTreeItem(data=82, parent=root)
root.appendChild(CustomTreeItem(data=[1, 2, 3], name='child2'))
root.insertChild(1, CustomTreeItem(data=3.14, name='child3'))
root.children[1].appendChild(CustomTreeItem(data='some cool data'))
grandchild2 = CustomTreeItem(data=False, name='grandchild2')
grandchild2.parent = root['child2']
CustomTreeItem(name='greatgrandchild', parent=root['/child2/grandchild2'])
print(root)

print('\nDepth first iteration...')
for item in root.depthFirst():
    print(item.name)

# Tree model with support for drag-and-drop within and between models...
model = CustomTreeModel(root)

# To access the underlying item tree...
#root = model.root()

# To reset the underlying item tree...
#model.setRoot(root)

# Tree view widget with default behavior...
view = TreeView()
view.setModel(model)
view.expandAll()
view.resizeAllColumnsToContents()
view.show()

# Run the application...
app.exec()

# print the final tree...
print('\nFinal tree...')
print(root)