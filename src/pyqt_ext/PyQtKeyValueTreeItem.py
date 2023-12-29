""" Data interface for a tree of key-value pairs.
"""

from __future__ import annotations

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import AbstractTreeItem


class KeyValueTreeItem(AbstractTreeItem):
    
    def __init__(self, key, value, parent: KeyValueTreeItem | None = None) -> None:
        AbstractTreeItem.__init__(self, parent=parent)
        self._key = key
        self._value = value

        # recursively build subtree if value is itself a container with key,value access
        if isinstance(value, dict):
            for key in value:
                self.children.append(KeyValueTreeItem(key, value[key], parent=self))
        elif isinstance(value, list):
            for i in range(len(value)):
                self.children.append(KeyValueTreeItem(None, value[i], parent=self))
    
    def __repr__(self):
        return f'{self.key}: {self.value}'
    
    @property
    def key(self):
        if self.parent is not None:
            if self.parent.is_list():
                return self.row()
        return self._key
    
    @key.setter
    def key(self, key) -> None:
        if self.parent is not None:
            if isinstance(self.parent.value, dict):
                self.parent._value[key] = self.value
                del self.parent._value[self._key]
            elif isinstance(self.parent.value, list):
                # cannot edit list index
                return
        self._key = key
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value) -> None:
        if self.parent is not None:
            if self.parent.is_dict() or self.parent.is_list():
                self.parent._value[self.key] = value
        self._value = value
    
    def is_dict(self):
        return isinstance(self.value, dict)
    
    def is_list(self):
        return isinstance(self.value, list)
    
    def is_container(self):
        return self.is_dict() or self.is_list()
    
    def data(self, column: int):
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

    def remove_children(self, position: int, count: int) -> bool:
        if position < 0 or position + count > len(self.children):
            return False
        if not self.is_container():
            return False
        for row in range(count):
            item: KeyValueTreeItem = self.children.pop(position)
            item.parent = None
            del self._value[item.key]
        return True
    
    def insert_children(self, position: int, items: list[KeyValueTreeItem]) -> bool:
        if position < 0 or position > len(self.children):
            return False
        if not self.is_container():
            return False
        for i, item in enumerate(items):
            if self.is_dict():
                if item.key in self.value:
                    # raise KeyError(f'Key "{item.key}" already exists in parent dict.')
                    item.key = str(item.key) + '_1'
                    while item.key in self.value:
                        pos = item.key.rfind('_')
                        item.key = item.key[:pos+1] + str(int(item.key[pos+1:]) + 1)
                self._value[item.key] = item.value
            elif self.is_list():
                self._value.insert(position + i, item.value)
            item.parent = self
            self.children.insert(position + i, item)
        return True
    
    def to_obj(self):
        if self.is_dict():
            return {child.key: child.to_obj() for child in self.children}
        elif self.is_list():
            return [child.to_obj() for child in self.children]
        else:
            return self.value


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


if __name__ == '__main__':
    test_tree()
