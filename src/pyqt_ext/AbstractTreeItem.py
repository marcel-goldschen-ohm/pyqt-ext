""" Base class for a tree of items to be used as a data interface with QAbstractItemModel.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class AbstractTreeItem():
    """ Base class for a tree of items to be used as a data interface with QAbstractItemModel.
    
    !!! This only implements the tree structure. You must define any data variables in a derived class.

    In a derived class:
        1. Add attributes to store/interface with your data.
        2. Reimplement data(), set_data(), and __repr__() methods.
    """
    
    def __init__(self, parent: AbstractTreeItem | None = None):
        self.parent: AbstractTreeItem = None
        self.children: list[AbstractTreeItem] = []
        if parent is not None:
            # if self not in parent.children:
            #     parent.children.append(self)
            self.setParent(parent)
    
    # !!! not implemented
    def __repr__(self):
        # raise NotImplementedError
        return str(id(self))  # for debugging
    
    # tree linkage ------------------------------------------------------------
    
    def setParent(self, parent: AbstractTreeItem | None) -> None:
        """ Set the parent of this item.
        
            This is the main linkage function.
            All other tree linkage functions use this.
            This results in appending self to parent's list of children.
        """
        if self.parent is parent:
            return
        if self.parent is not None:
            # detach from old parent
            if self in self.parent.children:
                self.parent.children.remove(self)
        if parent is not None:
            # attach to new parent
            if self not in parent.children:
                parent.children.append(self)
        self.parent = parent
    
    def appendChild(self, item: AbstractTreeItem) -> None:
        item.setParent(self)
    
    def insertChild(self, index: int, item: AbstractTreeItem) -> None:
        item.setParent(self)
        # move item to index
        pos = self.children.index(item)
        if pos != index:
            self.children.insert(index, self.children.pop(pos))
    
    def removeChild(self, item: AbstractTreeItem) -> None:
        if item.parent is not self:
            return
        item.setParent(None)
    
    # interface for QAbstractItemModel ----------------------------------------
    
    def row(self) -> int:
        return self.siblingIndex()
    
    # !!! not implemented
    def data(self, column: int):
        # raise NotImplementedError
        return self.__repr__()  # for debugging
    
    # !!! not implemented
    def setData(self, column: int, value) -> bool:
        # raise NotImplementedError
        return False
    
    def removeChildren(self, position: int, count: int) -> bool:
        if position < 0 or position + count > len(self.children):
            return False
        for _ in range(count):
            item: AbstractTreeItem = self.children[position]
            self.removeChild(item)
        return True
    
    def insertChildren(self, position: int, items: list[AbstractTreeItem]) -> bool:
        if position < 0 or position > len(self.children):
            return False
        for i, item in enumerate(items):
            self.insertChild(position + i, item)
        return True
    
    def appendChildren(self, items: list[AbstractTreeItem]) -> bool:
        for item in items:
            self.appendChild(item)
        return True
    
    # tree traversal ----------------------------------------------------------
    
    def root(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.parent is not None:
            item = item.parent
        return item
    
    def firstChild(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[0]

    def lastChild(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[-1]

    def firstSibling(self) -> AbstractTreeItem:
        if self.parent is not None:
            return self.parent.firstChild()
        return self

    def lastSibling(self) -> AbstractTreeItem:
        if self.parent is not None:
            return self.parent.lastChild()
        return self

    def siblings(self) -> list[AbstractTreeItem]:
        if self.parent is not None:
            return self.parent.children
        return [self]
    
    def nextSibling(self) -> AbstractTreeItem | None:
        siblings: list[AbstractTreeItem] = self.siblings()
        if siblings:
            i: int = siblings.index(self)
            if i+1 < len(siblings):
                return siblings[i+1]

    def prevSibling(self) -> AbstractTreeItem | None:
        siblings: list[AbstractTreeItem] = self.siblings()
        if siblings:
            i: int = siblings.index(self)
            if i-1 >= 0:
                return siblings[i-1]

    # depth first traversal
    def last(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.lastChild()
        return item

    # depth first traversal
    def next(self) -> AbstractTreeItem | None:
        if self.children:
            return self.firstChild()
        next_sibling: AbstractTreeItem = self.nextSibling()
        if next_sibling is not None:
            return next_sibling
        item: AbstractTreeItem = self.parent
        while item is not None:
            next_sibling: AbstractTreeItem = item.nextSibling()
            if next_sibling is not None:
                return next_sibling
            item = item.parent

    # depth first traversal
    def prev(self) -> AbstractTreeItem | None:
        prev_sibling: AbstractTreeItem = self.prevSibling()
        if prev_sibling is not None:
            return prev_sibling.last()
        if self.parent is not None:
            return self.parent
    
    def siblingIndex(self) -> int:
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
    
    def subtreeMaxDepth(self) -> int:
        root_depth: int = self.depth()
        max_depth: int = 0
        item: AbstractTreeItem = self.next()
        while item is not None:
            depth: int = item.depth()
            if depth - root_depth > max_depth:
                max_depth = depth - root_depth
            item = item.next()
        return max_depth
    
    def hasAncestor(self, ancestor: AbstractTreeItem) -> bool:
        item: AbstractTreeItem = self
        while item is not None:
            if item is ancestor:
                return True
            item = item.parent
        return False
    
    # debugging --------------------------------------------------------------
    
    def dump(self, indent: int = 0):
        print(' ' * indent + self.__repr__())
        for child in self.children:
            child.dump(indent + 4)


def test_tree():
    root = AbstractTreeItem()
    root.insertChildren(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].insertChildren(0, [AbstractTreeItem(), AbstractTreeItem(), AbstractTreeItem()])
    root.children[-1].children[0].insertChildren(0, [AbstractTreeItem(), AbstractTreeItem()])
    root.dump()


if __name__ == '__main__':
    test_tree()
