# Tree model/view interface for PyQt
Qt tree model/view classes require a large amount of boilerplate code that is often mostly the same for all trees, with only a few functions needing to be changed for custom tree behavior. Given the large number of methods that must be properly defined for the tree to work, and the relativley poor documentation beyond the most simple examples, I found myself wasting a lot of effort to *rediscover* how to construct a working tree model/view for each infrequent case where I needed such a tool. Here, I provide a general interface for a tree that you can either **1) derive from** or **2) use as a template** to speed development of your custom tree. For an example of how you might do this, see the [quick start example](#quick-start-example) below or my implementation of a [(key, value) tree](KeyValueTree.md).

# Table of contents
- [Install](#install)
- [Quick start example](#quick-start-example): Example of a simple custom tree model/view.
- [AbstractTreeItem](#abstracttreeitem): Generic tree node with parent/child linkage, navigation, path access, iteration, etc. *Only missing the data you want to associate with it.*
- [AbstractTreeModel](#abstracttreemodel): Tree model that knows how to work with `AbstractTreeItem`s.
- [AbstractDndTreeModel](#abstractdndtreemodel): Tree model with default drag-and-drop functionality.
- [TreeView](#treeview): Tree view widget with context menu and Ctrl+Wheel expand/fold.

# Install
Should work with PySide6, PyQt6, or PyQt5.
```shell
pip install PySide6 pyqt-ext
```

# Quick start example
Source code: [CustomTreeExample.py](../examples/CustomTreeExample.py)

Create the application...
```python
from qtpy.QtWidgets import QApplicaiton
app = QApplicaiton()
```

Custom tree item derived from [AbstractTreeItem](#abstracttreeitem) with a `data` attribute to store the data for each item and implementations of `get_data` and `set_data` methods for an editable tree with two columns: *name*, *data*...
```python
from pyqt_ext.tree import AbstractTreeItem

class CustomTreeItem(AbstractTreeItem):

    def __init__(self, data = None, name: str = None, parent: CustomTreeItem = None):
        # the data associated with this tree item
        self.data = data
        # tree linkage handled by AbstractTreeItem
        AbstractTreeItem.__init__(self, name, parent)
    
    def __repr__(self):
        return f'{self.name}: {self.data}'
    
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
```

Build the tree *(I used a variety of methods just to give you a flavor of some of the capabilities of AbstractTreeItem)*...
```python
root = CustomTreeItem()
CustomTreeItem(data=82, parent=root)
root.append_child(CustomTreeItem(data=[1, 2, 3], name='child2'))
root.insert_child(1, CustomTreeItem(data=3.14, name='child3'))
root.children[1].append_child(CustomTreeItem(data='some cool data'))
grandchild2 = CustomTreeItem(data=False, name='grandchild2')
grandchild2.parent = root['child2']
CustomTreeItem(name='greatgrandchild', parent=root['/child2/grandchild2'])
print(root)
```
```shell
CustomTreeItem@4386639984: None
├── CustomTreeItem@4386640032: 82
├── child3: 3.14
│   └── CustomTreeItem@4386645360: some cool data
└── child2: [1, 2, 3]
    └── grandchild2: False
        └── greatgrandchild: None
```

Just FYI, you can iterate over the tree items...
```python
for item in root.depth_first():
    print(item.name)
```
```shell
CustomTreeItem@4386639984
CustomTreeItem@4386640032
child3
CustomTreeItem@4386645360
child2
grandchild2
greatgrandchild
```

Custom tree model with drag-and-drop derived from [AbstractDndTreeModel](#abstractdndtreemodel) for an editable tree with two columns: name, data...
```python
from pyqt_ext.tree import AbstractDndTreeModel
from qtpy.QtCore import QModelIndex

class CustomDndTreeModel(AbstractDndTreeModel):

    def __init__(self, root: CustomTreeItem = None, parent: QObject = None):
        AbstractDndTreeModel.__init__(self, root, parent)
        # column titles
        self.setColumnLabels(['Name', 'Data'])

    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        # for [name, data] columns
        return 2
```

Create the tree model...
```python
model = CustomDndTreeModel(root)

# to access the underlying item tree (not necessary here)
root = model.root()

# to reset the underlying item tree (not necessary here)
model.setRoot(root)
```

Create the tree view widget as instance of [TreeView](#treeview) *(no need to define a derived tree view class unless custom behavior is needed)*...
```python
from pyqt_ext.tree import TreeView

view = TreeView()
view.setModel(model)
view.expandAll()
view.resizeAllColumnsToContents()
view.show()
```

Run the application...
```python
app.exec()
```

And voila! Try editing the data and dragging the items to rearrange the tree...

<img src="images/CustomTreeExample.png">

# AbstractTreeItem
Source code: [AbstractTreeItem.py](../src/pyqt_ext/tree/AbstractTreeItem.py)

`AbstractTreeItem` is used to interface between an `AbstractTreeModel` (derived from `QAbstractItemModel`) and **your data**. Out-of-the-box it provides the basic parent/children tree linkage (this is what the `AbstractTreeModel` will use to define the tree structure) as well as a bunch of properties/methods for tree navigation, restructuring, and printing. However, **you MUST derive from this class and add properties/methods appropriate for your data.** At minimum, you must reimplement `get_data` and `set_data` methods as these will be used by the model when displaying/editing the tree items. You may also need to reimplement properties/methods for restructuring the tree (e.g., `parent.setter`, `insert_child`) so that such changes are applied to your data as needed and not just the tree model interface. You may also want to reimplement `__repr__` to return a single line string appropriate for the data associated with each item (the default is to return the item's name property or a unique id if name has not been set). By default, printing an item will return a multi-line string tree representation for the item and all of its descendents using each item's name.

# AbstractTreeModel
Source code: [AbstractTreeModel.py](../src/pyqt_ext/tree/AbstractTreeModel.py)

`AbstractTreeModel` provides a `QAbstractItemModel` interface for a tree of `AbstractTreeItem`s. There are also convenince functions such as `rowLabels`, `setRowLabels`, `columnLabels`, and `setColumnLabels`. The model is functional out of the box, but the default is a tree with a single column. If you need multiple columns you must reimplement `columnCount` in a derived class. Depending on your data, you may also need to reimplement `flags` for custom behavior. Most functions for restructuring the tree hierarchy should probably work out-of-the-box so long as the appropriate methods in `AbstractTreeItem` have been reimplemented. Instead of `insertRows`, see `insertItems`. Currently only `moveRow` is supported, and not `moveRows`.

# AbstractDndTreeModel
Source code: [AbstractTreeModel.py](../src/pyqt_ext/tree/AbstractTreeModel.py)

Same as `AbstractTreeModel` except that drag-and-drop is enabled (`supportedDropActions` allows `MoveAction` and `CopyAction` by default). The rest of what is needed to support drag-and-drop is already in `AbstractTreeModel` (e.g., see `flags`), it is simply ignored until drag-and-drop actions are specifically supported. To customize drag-and-drop behaviour, you can reimplement `flags` and/or `moveRows`. Another place you can customize drag-and-drop behavior is by reimplementing `dragEnterEvent` and/or `dropEvent` in `TreeView`. *!!! Currently, `TreeView` does not handle mime data, so the out-of-the-box drag-and-drop only handles moving items within a tree.*

# TreeView
Source code: [TreeView.py](../src/pyqt_ext/tree/TreeView.py)

`TreeView` provides a `QTreeView` with a context menu and Ctrl+Wheel expanding/folding of the tree branches. The view is functional out-of-the-box. It also supports drag-and-drop (the model will also need to support drag-and-drop). *!!! Currently, `TreeView` does not handle mime data, so the out-of-the-box drag-and-drop only handles moving items within a tree.*
