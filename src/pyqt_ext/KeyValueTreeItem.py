""" Data interface for a tree of key-value pairs.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeItem


class KeyValueTreeItem(AbstractTreeItem):
    
    def __init__(self, key, value, parent: KeyValueTreeItem | None = None) -> None:
        self._key = key
        self._value = value
        AbstractTreeItem.__init__(self, parent=parent)

        # recursively build subtree if value is itself a container with key,value access
        if isinstance(value, dict):
            for key in value:
                KeyValueTreeItem(key, value[key], parent=self)
        elif isinstance(value, list):
            for i in range(len(value)):
                KeyValueTreeItem(None, value[i], parent=self)
    
    def __repr__(self):
        return f'{self.key}: {self.value}'
    
    # data --------------------------------------------------------------------
    
    @property
    def key(self):
        if self.parent is not None:
            if self.parent.isList():
                return self.row()
        return self._key
    
    @key.setter
    def key(self, key) -> None:
        if self.parent is not None:
            if self.parent.isDict():
                if (self.key is not None) and (self.key in self.parent.value):
                    self.parent.value.pop(self.key)
                if key in self.parent.value:
                    key = unique_name(key, list(self.parent.value.keys()))
                self.parent.value[key] = self.value
            elif self.parent.isList():
                # cannot edit list index
                return
        self._key = key
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value) -> None:
        if self.parent is not None:
            if self.parent.isDict() or self.parent.isList():
                self.parent._value[self.key] = value
        self._value = value
    
    def isDict(self):
        return isinstance(self.value, dict)
    
    def isList(self):
        return isinstance(self.value, list)
    
    def isContainer(self):
        return self.isDict() or self.isList()
    
    # tree navigation ----------------------------------------------------------
    
    @property
    def path(self) -> str:
        item = self
        path = []
        while not item.isRoot():
            path.insert(0, str(item.key))
            item = item.parent
        return '/' + '/'.join(path)
    
    def __getitem__(self, path: str) -> KeyValueTreeItem:
        """ Return item at path either from the root item (if path starts with /) or otherwise from this item. """
        if path.startswith('/'):
            # path from root item (first name in path must be a child of the root item)
            item = self.root()
        else:
            # path from this item (first name in path must be a child of this item)
            item = self
        path = path.strip('/').split('/')
        for key in path:
            child_keys = [str(child.key) for child in item.children]
            child_index = child_keys.index(key)
            item = item.children[child_index]
        return item
    
    # tree restructuring ------------------------------------------------------
    
    def setParent(self, parent: KeyValueTreeItem | None) -> None:
        """ Set the parent of this item.
        
            This is the main linkage function.
            All other tree linkage functions use this.
            This results in appending self to parent's list of children.
        """
        if self.parent is parent:
            return
        if (parent is not None) and (not parent.isContainer()):
            raise ValueError('Parent must be a container type (dict or list).')
        if self.parent is not None:
            # detach from old parent
            if self in self.parent.children:
                # remove value from parent container
                self.parent._value.pop(self.key)
                # remove item from parent's children
                self.parent.children.remove(self)
            self.parent = None
        if parent is not None:
            # attach to new parent
            if self not in parent.children:
                # insert into parent's children
                parent.children.append(self)
                # insert value into parent container
                if parent.isDict():
                    parent._value[self.key] = self.value
                elif parent.isList():
                    key = parent.children.index(self)
                    if key < len(parent._value):
                        parent._value[key] = self.value
                    else:
                        parent._value.append(self.value)
            self.parent = parent
    
    def insertChild(self, index: int, item: KeyValueTreeItem) -> None:
        if self.isDict():
            if item.key is None:
                item.setParent(None)
                item.key = 'None'
            if item.key in self.value:
                item.setParent(None)
                item.key = unique_name(item.key, list(self.value.keys()))
        item.setParent(self)
        # move item to index
        pos = self.children.index(item)
        if pos != index:
            self.children.insert(index, self.children.pop(pos))
            if self.isList():
                self._value.insert(index, self._value.pop(pos))
    
    # interface for QAbstractItemModel ----------------------------------------
    
    def data(self, column: int):
        if column == 0:
            return self.key
        elif column == 1:
            if self.isContainer():
                return
            return self.value
    
    def setData(self, column: int, value) -> bool:
        if column == 0:
            self.key = value
            return True
        elif column == 1:
            if self.isContainer():
                return False
            self.value = value
            return True
        return False


def unique_name(name: str, names: list[str]) -> str:
    if name not in names:
        return name
    i: int = 1
    uname = name + f'_{i}'
    while uname in names:
        i += 1
        uname = name + f'_{i}'
    return uname


def test_tree():
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
    root.dump()

    root.removeChild(root['/a'])
    root.dump()

    d = root['c/d']
    f = root['c/d/f']
    d.removeChild(f)
    root.dump()

    d.setParent(root)
    root.dump()

    root.insertChild(1, d)
    root.dump()

    b = root['b']
    b.insertChild(2, d)
    root.dump()

    b.removeChild(b['1'])
    root.dump()

    c = root['c']
    c.value['me'] = 'bye'
    root.dump()

    c.insertChild(0, b['1'])
    root.dump()


if __name__ == '__main__':
    test_tree()
