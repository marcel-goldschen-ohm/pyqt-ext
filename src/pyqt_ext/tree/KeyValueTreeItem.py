""" Data interface for a tree of key-value pairs.
"""

from __future__ import annotations
from pyqt_ext.tree import AbstractTreeItem


class KeyValueTreeItem(AbstractTreeItem):
    
    def __init__(self, key: str | None, value, parent: KeyValueTreeItem | None = None) -> None:
        self._key: str | None = key
        self._value = value
        AbstractTreeItem.__init__(self, parent=parent)

        # recursively build subtree if value is itself a container with key,value access
        if isinstance(value, dict):
            for key in value:
                KeyValueTreeItem(key, value[key], parent=self)
        elif isinstance(value, list):
            for i in range(len(value)):
                # list keys are not explicitly set, they will default to the list index
                KeyValueTreeItem(None, value[i], parent=self)
    
    def __repr__(self):
        if self.isBasicValue():
            return f'{self.key}: {self.value}, <{type(self.value)}>'
        return f'{self.key}: {type(self.value)}'
    
    def __str__(self) -> str:
        return self._tree_repr(lambda item: item.__repr__())
    
    @property
    def key(self) -> str | int:
        # if parent is a list, the key is the index of this item in the list
        parent: KeyValueTreeItem = self.parent
        if (parent is not None) and parent.isList():
            return self.siblingIndex()
        # otherwise, return the local key
        return self._key
    
    @key.setter
    def key(self, key: str) -> None:
        # update parent dict
        parent: KeyValueTreeItem = self.parent
        if parent is not None:
            parent_container = parent.value
            if isinstance(parent_container, dict):
                parent_dict: dict = parent_container
                # only allow string keys for dict
                key = str(key)
                # remove old key from parent dict
                if (self.key is not None) and (self.key in parent_dict):
                    parent_dict.pop(self.key)
                # make sure key is unique
                if key in parent_dict:
                    key = unique_name(key, list(parent_dict.keys()))
                # add new key to parent dict
                parent_dict[key] = self.value
            elif isinstance(parent_container, list):
                # key is always the list index
                return
        # update local key
        self._key = key
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value) -> None:
        # remove any children
        for child in self.children.copy():
            self.removeChild(child)

        # update parent dict or list
        if self.parent is not None:
            parent_container = self.parent.value
            parent_container[self.key] = value
        # update local value
        self._value = value

        # recursively build subtree if value is itself a container with key,value access
        if isinstance(value, dict):
            for key in value:
                KeyValueTreeItem(key, value[key], parent=self)
        elif isinstance(value, list):
            for i in range(len(value)):
                # list keys are not explicitly set, they will default to the list index
                KeyValueTreeItem(None, value[i], parent=self)
    
    @AbstractTreeItem.parent.setter
    def parent(self, parent: KeyValueTreeItem | None) -> None:
        if self.parent is parent:
            return
        if (parent is not None):
            parent_container = parent.value
            if not (isinstance(parent_container, dict) or isinstance(parent_container, list)):
                raise ValueError('Parent must be a key[value] container (currently only dict or list supported).')

        # remove value from old parent container
        old_parent: KeyValueTreeItem | None = self.parent
        if old_parent is not None:
            old_parent_container = old_parent.value
            # old_parent_container is a dict or list
            old_parent_container.pop(self.key)
        
        # insert value into new parent container
        if parent is not None:
            parent_container = parent.value
            if isinstance(parent_container, dict):
                existing_sibling_item_keys = [child.key for child in parent.children]
                if self.key in existing_sibling_item_keys:
                    # add key[value] pair without overwritting existing key[value] pair
                    self._key = unique_name(self.key, existing_sibling_item_keys)
                # if the parent dict alreayd has this key[value pair], this won't do anything
                parent_container[self.key] = self.value
            elif isinstance(parent_container, list):
                index = len(parent.children)
                if len(parent_container) <= index:
                    parent_container.append(self.value)
                else:
                    # parent list already has data at this position (probably this value already)
                    parent_container[index] = self.value

        # update item tree linkage
        AbstractTreeItem.parent.fset(self, parent)
    
    @AbstractTreeItem.name.getter
    def name(self) -> str:
        return str(self.key)
    
    def isContainer(self) -> bool:
        return self.isDict() or self.isList()
    
    def isDict(self) -> bool:
        return isinstance(self.value, dict)
    
    def isList(self) -> bool:
        return isinstance(self.value, list)
    
    def isBasicValue(self) -> bool:
        return not self.isContainer()
    
    def insertChild(self, index: int, item: KeyValueTreeItem) -> bool:
        if not AbstractTreeItem.insertChild(self, index, item):
            return False
        if isinstance(self.value, list):
            # above appends item.value to self.value
            pos = len(self.value) - 1
            # if needed, move item.value to index in self.value
            if pos != index:
                if pos < index:
                    index -= 1
                if pos != index:
                    self.value.insert(index, self.value.pop(pos))
        return True
    
    def data(self, column: int):
        if column == 0:
            return self.key
        elif column == 1:
            return self.value
    
    def setData(self, column: int, value) -> bool:
        if column == 0:
            self.key = value
            return True
        elif column == 1:
            self.value = value
            return True
        return False


def unique_name(name: str, names: list[str]) -> str:
    if name not in names:
        return name
    i: int = 1
    uname = f'{name}_{i}'
    while uname in names:
        i += 1
        uname = f'{name}_{i}'
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
    print('-'*82, root)

    root.removeChild(root['/a'])
    print('\nremove /a')
    print(root)

    d = root['c/d']
    f = root['c/d/f']
    d.removeChild(f)
    print('\nremove /c/d/f')
    print(root)

    d.parent = root
    print('\nmove /c/d to /d')
    print(root)

    root.insertChild(1, d)
    print('\nmove /d to 2nd child of /')
    print(root)

    b = root['b']
    b.insertChild(2, d)
    print('\nmove /d to 3rd child of /b')
    print(root)

    b.removeChild(b['1'])
    print('\nremove /b/1')
    print(root)

    c = root['c']
    c.children[0].value = 'bye'
    print('\n/c/me:hi -> /c/me:bye')
    print(root)
    print(c)

    c.insertChild(0, b['1'])
    print('\nmove /b/1 to first child of /c')
    print(root)


if __name__ == '__main__':
    test_tree()
