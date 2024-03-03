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
        if self.is_container():
            return f'{self.key}'
        return f'{self.key}: {self.value}'
    
    @property
    def key(self) -> str | int:
        # if parent is a list, the key is the index of this item in the list
        if self.parent is not None:
            if self.parent.is_list():
                return self.sibling_index
        # otherwise, return the local key
        return self._key
    
    @key.setter
    def key(self, key: str) -> None:
        # update parent dict
        if self.parent is not None:
            if self.parent.is_dict():
                # only allow string keys for dict
                key = str(key)
                # remove old key from parent dict
                if (self.key is not None) and (self.key in self.parent.value):
                    self.parent.value.pop(self.key)
                # make sure key is unique
                if key in self.parent.value:
                    key = unique_name(key, list(self.parent.value.keys()))
                # add new key to parent dict
                self.parent.value[key] = self.value
            elif self.parent.is_list():
                # cannot edit list index
                return
        # update local key
        self._key = key
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value) -> None:
        # update parent dict or list
        if self.parent is not None:
            if self.parent.is_dict() or self.parent.is_list():
                self.parent.value[self.key] = value
        # update local value
        self._value = value
    
    @AbstractTreeItem.parent.setter
    def parent(self, parent: KeyValueTreeItem | None) -> None:
        if self.parent is parent:
            return
        if (parent is not None) and (not parent.is_container()):
            raise ValueError('Parent must be a container (dict or list).')
        old_parent: KeyValueTreeItem | None = self.parent

        # update item tree
        AbstractTreeItem.parent.fset(self, parent)

        # remove value from old parent container
        if old_parent is not None:
            if old_parent.is_dict():
                for key, value in old_parent.value.items():
                    if (value is self.value) or (value == self.value):
                        old_parent.value.pop(key)
                        break
            elif old_parent.is_list():
                if self.value in old_parent.value:
                    old_parent.value.remove(self.value)
        
        # insert value into new parent container
        if parent is not None:
            if parent.is_dict():
                if self.value not in parent.value.values():
                    # resetting key will insert value into parent dict
                    self.key = str(self.key)
                    # if key in parent.value:
                    #     key = unique_name(key, list(parent.value.keys()))
                    # self._key = key
                    # parent.value[self.key] = self.value
            elif parent.is_list():
                if self.value not in parent.value:
                    parent.value.append(self.value)
    
    @AbstractTreeItem.name.getter
    def name(self) -> str:
        return str(self.key)
    
    def is_dict(self):
        return isinstance(self.value, dict)
    
    def is_list(self):
        return isinstance(self.value, list)
    
    def is_container(self):
        return self.is_dict() or self.is_list()
    
    def insert_child(self, index: int, item: KeyValueTreeItem) -> bool:
        if not AbstractTreeItem.insert_child(self, index, item):
            return False
        if self.is_list():
            pos = self.value.index(item.value)
            if pos != index:
                self.value.insert(index, self.value.pop(pos))
        return True
    
    def get_data(self, column: int):
        if column == 0:
            return self.key
        elif column == 1:
            if self.is_container():
                return
            return self.value
    
    def set_data(self, column: int, value) -> bool:
        if column == 0:
            self.key = value
            return True
        elif column == 1:
            if self.is_container():
                return False
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
    print(root)

    root.remove_child(root['/a'])
    print('remove /a')
    print(root)

    d = root['c/d']
    f = root['c/d/f']
    d.remove_child(f)
    print('remove /c/d/f')
    print(root)

    d.parent = root
    print('move /c/d to /d')
    print(root)

    root.insert_child(1, d)
    print('move /d to 2nd child of /')
    print(root)

    b = root['b']
    b.insert_child(2, d)
    print('move /d to 3rd child of /b')
    print(root)

    b.remove_child(b['1'])
    print('remove /b/1')
    print(root)

    c = root['c']
    c.children[1].value = 'bye'
    print('/c/me:hi -> /c/me:bye')
    print(root)
    print(c)

    c.insert_child(0, b['1'])
    print('move /b/1 to first child of /c')
    print(root)


if __name__ == '__main__':
    test_tree()
