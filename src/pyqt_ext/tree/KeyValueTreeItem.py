""" Data interface for a tree of key:value pairs.

e.g., Any level of nesting of dict and list objects.
"""

from __future__ import annotations
from warnings import warn
from typing import Any
from pyqt_ext.tree import AbstractTreeItem


class KeyValueTreeItem(AbstractTreeItem):
    
    def __init__(self, data: dict | list | str | None, parent: KeyValueTreeItem | None = None) -> None:
        # A key:value mapping (dict or list) if this is the root item.
        # Otherwise a key into the parent item's key:value mapping (ignored if parent is a list).
        self._data: dict | list | str | None = data

        AbstractTreeItem.__init__(self, parent=parent)
        self.setupSubtree()
    
    def key(self) -> str | int | None:
        if isinstance(self._data, dict) or isinstance(self._data, list):
            # no key for the root key:value map
            return
        
        # this item stores a key into its parent key:value map.
        parent: KeyValueTreeItem = self.parent()
        if parent is None:
            # default to the stored key
            return self._data or self.siblingIndex()
        parent_map: dict | list = parent.value()
        if isinstance(parent_map, dict):
            # this item stores a key into the parent dict
            if (self._data is None) or (self._data == ''):
                # ensure a valid key
                key = self.uniqueName('?', list(parent_map.keys()))
                parent_map[key] = None
                self._data = key
            return self._data
        elif isinstance(parent_map, list):
            # the list index is taken from the order of the parent item's children
            return self.siblingIndex()
    
    def setKey(self, key: str) -> None:
        if isinstance(self._data, dict) or isinstance(self._data, list):
            # no key for the root key:value map
            return
        
        # this item stores a key into its parent key:value map
        parent: KeyValueTreeItem = self.parent()
        if parent is None:
            return
        parent_map: dict | list = parent.value()
        if isinstance(parent_map, dict):
            # must have a valid key
            if key is None:
                key = 'None'
            elif key == '':
                return
            elif type(key) not in [str, int, float, bool]:
                return
            # check if key has changed
            if key == self.key():
                return
            # make sure key is unique
            if key in parent_map:
                warn(f'Key {key} already exists.')
                # key = self.uniqueName(key, list(parent_map.keys()))
                return
            # swap keys in map
            parent_map[key] = parent_map.pop(self.key())
            # store new key in item
            self._data = key
        elif isinstance(parent_map, list):
            # Keys are not used for lists.
            # Instead, the sibling index is used as the list index.
            return
    
    def value(self) -> Any:
        if isinstance(self._data, dict) or isinstance(self._data, list):
            # this item stores the root key:value map
            return self._data
        
        # this item stores a key into its parent key:value map
        parent: KeyValueTreeItem = self.parent()
        if parent is None:
            return
        # get value from parent key:value mapping (dict or list)
        parent_map: dict | list = parent.value()
        if isinstance(parent_map, dict) or isinstance(parent_map, list):
            try:
                return parent_map[self.key()]
            except (KeyError, IndexError):
                return
    
    def setValue(self, value) -> None:
        if isinstance(self._data, dict) or isinstance(self._data, list):
            # this is the root item which must be a key:value map
            if not isinstance(value, dict) and not isinstance(value, list):
                return
            # reset the entire tree
            for child in self.children:
                child._parent = None
            self.children = []
            self._data = value
            self.setupSubtree()
            return
        
        # this item stores a key into its parent key:value map
        # remove any child items (in case this item was itself a key:value container)
        for child in self.children:
            child._parent = None
        self.children = []
        parent: KeyValueTreeItem = self.parent()
        if parent is None:
            self._data = value
        else:
            # set value in parent key:value mapping (dict or list)
            parent_map: dict | list = parent.value()
            parent_map[self.key()] = value
        self.setupSubtree()
    
    def setupSubtree(self):
        """ Recursively build subtree if value is itself a container with key:value access.
        """
        value = self.value()
        if isinstance(value, dict):
            for key in list(value.keys()):
                KeyValueTreeItem(key, parent=self)
        elif isinstance(value, list):
            for i in range(len(value)):
                # list keys are not explicitly set, they will default to the list index
                KeyValueTreeItem(None, parent=self)
    
    def name(self) -> str:
        key = self.key()
        return str(key) if key is not None else None
    
    def setName(self, name: str) -> None:
        self.setKey(name)
    
    def __repr__(self):
        key = self.key()
        value = self.value()
        if isinstance(value, dict):
            return f'{key}: {{}}'
        elif isinstance(value, list):
            return f'{key}: []'
        else:
            return f'{key}: {value}'
    
    def __str__(self) -> str:
        return self._tree_repr(lambda item: item.__repr__())
    
    def setParent(self, parent: KeyValueTreeItem | None) -> None:
        old_parent: KeyValueTreeItem | None = self.parent()
        new_parent: KeyValueTreeItem | None = parent
        if old_parent is new_parent:
            # nothing to do
            return
        if new_parent is not None:
            if new_parent.hasAncestor(self):
                raise ValueError('Cannot set parent to a descendant.')
            # the new parent must be a key:value container
            new_parent_value = new_parent.value()
            if not isinstance(new_parent_value, dict) and not isinstance(new_parent_value, list):
                raise ValueError('Parent must be a key:value mapping (dict or list).')
        
        value = self.value()
        
        if old_parent is not None:
            # detach from old parent
            old_parent_map: dict | list = old_parent.value()
            old_parent_map.pop(self.key())
            old_parent.children.remove(self)
        
        if new_parent is None:
            # root items must have a key:value mapping
            if isinstance(value, dict) or isinstance(value, list):
                self._data = value
            self._parent = None
        else:
            # attach to new parent (appends as last child)
            new_parent.children.append(self)
            self._parent = new_parent
            new_parent_map: dict | list = new_parent.value()
            # update new parent key:value mapping
            if isinstance(new_parent_map, dict):
                key = self.key()
                if (key is None) or (key == ''):
                    # ensure valid dict key
                    sibling_names = [sibling.name for sibling in self.siblings()]
                    key = self.uniqueName('?', sibling_names)
                if value is None:
                    value = self.value()
                # print('data:', self._data, 'key:', key, 'value:', value, 'parent dict:', new_parent_map)
                if (key not in new_parent_map) or (new_parent_map[key] is not value):
                    new_parent_map[key] = value
            elif isinstance(new_parent_map, list):
                if value is None:
                    value = self.value()
                # print('data:', self._data, 'value:', value, 'parent list:', new_parent_map)
                if len(new_parent_map) <= self.siblingIndex():
                    new_parent_map.append(value)
    
    def insertChild(self, index: int, child: KeyValueTreeItem) -> None:
        if not (0 <= index <= len(self.children)):
            raise IndexError('Index out of range.')
        # append as last child
        child.setParent(self)
        # move item to index
        pos = self.children.index(child)
        if pos != index:
            if pos < index:
                index -= 1
            if pos != index:
                this_map: dict | list = self.value()
                if isinstance(this_map, list):
                    this_map.insert(index, this_map.pop(pos))
                self.children.insert(index, self.children.pop(pos))


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
    root = KeyValueTreeItem(data)
    print('-'*82)
    print(root)
    import json
    print(json.dumps(data, indent='    '))

    print('-'*82)
    print('remove /a')
    root.removeChild(root['/a'])
    print(root)

    print('-'*82)
    print('remove /c/d/f')
    d = root['c/d']
    f = root['c/d/f']
    d.removeChild(f)
    print(root)

    print('-'*82)
    print('move /c/d to /d')
    d.setParent(root)
    print(root)

    print('-'*82)
    print('move /d to 2nd child of /')
    root.insertChild(1, d)
    print(root)

    print('-'*82)
    print('move /d to 3rd child of /b')
    b = root['b']
    b.insertChild(2, d)
    print(root)

    print('-'*82)
    print('remove /b/1')
    b.removeChild(b['1'])
    print(root)

    print('-'*82)
    print('/c/me:hi -> /c/me:bye')
    c = root['c']
    c.children[0].setValue('bye')
    print(root)
    print(c)

    print('-'*82)
    print('move /b/1 to first child of /c')
    c.insertChild(0, b['1'])
    print(root)


if __name__ == '__main__':
    test_tree()
