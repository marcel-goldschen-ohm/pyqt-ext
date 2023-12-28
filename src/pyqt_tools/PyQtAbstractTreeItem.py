""" Base class for a tree of items to be used as a data interface with QAbstractItemModel.
"""

from __future__ import annotations

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class AbstractTreeItem():
    """ Base class for a tree of items to be used as a data interface with QAbstractItemModel.
    
    !!! This only implements the tree structure. You must define any data variables in a derived class.

    In a class derived from this base class:
        1. Add attributes to store/interface with your data.
        2. Reimplement data(), set_data(), and __repr__() methods.
    """
    
    def __init__(self, parent: AbstractTreeItem | None = None):
        self.parent: AbstractTreeItem = parent
        self.children: list[AbstractTreeItem] = []
    
    def __iter__(self):
        return self

    def __next__(self):
        next_item: AbstractTreeItem = self.next_item_depth_first()
        if next_item is None:
            raise StopIteration
        return next_item
    
    # !!! not implemented
    def __repr__(self):
        # raise NotImplementedError
        return str(id(self))  # for debugging
    
    def row(self) -> int:
        return self.sibling_index()
    
    def root(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.parent is not None:
            item = item.parent
        return item
    
    def first_child(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[0]

    def last_child(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[-1]

    def first_sibling(self) -> AbstractTreeItem:
        if self.parent is not None:
            return self.parent.first_child()
        return self

    def last_sibling(self) -> AbstractTreeItem:
        if self.parent is not None:
            return self.parent.last_child()
        return self

    def siblings(self) -> list[AbstractTreeItem]:
        if self.parent is not None:
            return self.parent.children
        return [self]
    
    def next_sibling(self) -> AbstractTreeItem | None:
        siblings: list[AbstractTreeItem] = self.siblings()
        if siblings:
            i: int = siblings.index(self)
            if i+1 < len(siblings):
                return siblings[i+1]

    def prev_sibling(self) -> AbstractTreeItem | None:
        siblings: list[AbstractTreeItem] = self.siblings()
        if siblings:
            i: int = siblings.index(self)
            if i-1 >= 0:
                return siblings[i-1]

    def last_item_depth_first(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.last_child()
        return item

    def next_item_depth_first(self) -> AbstractTreeItem | None:
        if self.children:
            return self.first_child()
        next_sibling: AbstractTreeItem = self.next_sibling()
        if next_sibling is not None:
            return next_sibling
        item: AbstractTreeItem = self.parent
        while item is not None:
            next_sibling: AbstractTreeItem = item.next_sibling()
            if next_sibling is not None:
                return next_sibling
            item = item.parent

    def prev_item_depth_first(self) -> AbstractTreeItem | None:
        prev_sibling: AbstractTreeItem = self.prev_sibling()
        if prev_sibling is not None:
            return prev_sibling.last_item_depth_first()
        if self.parent is not None:
            return self.parent
    
    def sibling_index(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.children.index(self)
    
    def depth(self) -> int:
        depth: int = 0
        item: AbstractTreeItem = self
        while item.parent is not None:
            depth += 1
            item = item.parent
        return depth
    
    def subtree_max_depth(self) -> int:
        root_depth: int = self.depth()
        max_depth: int = 0
        item: AbstractTreeItem = self.next_item_depth_first()
        while item is not None:
            depth: int = item.depth()
            if depth - root_depth > max_depth:
                max_depth = depth - root_depth
            item = item.next_item_depth_first()
        return max_depth
    
    def dump(self, indent: int = 0):
        print(' ' * indent + self.__repr__())
        for child in self.children:
            child.dump(indent + 4)
    
    # !!! not implemented
    def data(self, column: int):
        # raise NotImplementedError
        return self.__repr__()  # for debugging
    
    # !!! not implemented
    def set_data(self, column: int, value) -> bool:
        # raise NotImplementedError
        return False
    
    def remove_children(self, position: int, count: int) -> bool:
        if position < 0 or position + count > len(self.children):
            return False
        for row in range(count):
            item: AbstractTreeItem = self.children.pop(position)
            item.parent = None
        return True
    
    def insert_children(self, position: int, items: list[AbstractTreeItem]) -> bool:
        if position < 0 or position > len(self.children):
            return False
        for i, item in enumerate(items):
            item.parent = self
            self.children.insert(position + i, item)
        return True
    
    def append_children(self, items: list[AbstractTreeItem]) -> bool:
        position: int = len(self.children)
        return self.insert_children(position, items)


def test_tree():
    root = AbstractTreeItem()
    root.insert_children(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].insert_children(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].children[0].insert_children(0, [AbstractTreeItem(), AbstractTreeItem()])
    root.dump()


if __name__ == '__main__':
    test_tree()
