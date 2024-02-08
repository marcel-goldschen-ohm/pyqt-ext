""" Base class for a tree of items to be used as a data interface with QAbstractItemModel.
"""

from __future__ import annotations
from collections.abc import Iterator
# from qtpy.QtCore import *
# from qtpy.QtGui import *
# from qtpy.QtWidgets import *


class AbstractTreeItem():
    """ Base class for a tree of items to be used as a data interface with QAbstractItemModel.
    
    !!! This only implements the tree structure. You must define any data variables in a derived class.

    In a derived class:
        1. Add attributes to store/interface with your data.
        2. Minimally reimplement data() and set_data() methods.
        3. For nice printout, you may want to reimplement __repr__() method.
        3. For special linkage rules you may need to reimplement parent.setter and insert_child().
    """
    
    def __init__(self, parent: AbstractTreeItem | None = None):
        self._parent: AbstractTreeItem | None = None
        self._children: list[AbstractTreeItem] = []
       
        # handle linkage
        self.parent = parent
    
    def __repr__(self):
        # Return a single line string representation of this item.
        # See __str__ for a multi-line representation of the tree.
        # raise NotImplementedError
        return self.__class__.__name__ + ' at ' + str(id(self))  # for debugging
    
    def __str__(self):
        # returns a multi-line string representation of this item's tree branch
        items: list[AbstractTreeItem] = list(self.depth_first())
        lines: list[str] = [repr(item) for item in items]
        for i, item in enumerate(items):
            if item is self:
                continue
            if item is item.parent.last_child:
                lines[i] = '\u2514' + '\u2500'*2 + lines[i]
            else:
                lines[i] = '\u251C' + '\u2500'*2 + lines[i]
            parent = item.parent
            while parent is not self:
                if i < items.index(parent.last_sibling):
                    lines[i] = '\u2502  ' + lines[i]
                else:
                    lines[i] = '   ' + lines[i]
                parent = parent.parent
        return '\n'.join(lines)
    
    @property
    def parent(self) -> AbstractTreeItem | None:
        return self._parent
    
    @parent.setter
    def parent(self, parent: AbstractTreeItem | None) -> None:
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
        self._parent = parent
    
    @property
    def children(self) -> list[AbstractTreeItem]:
        return self._children
    
    @property
    def root(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.parent is not None:
            item = item.parent
        return item
    
    @property
    def first_child(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[0]

    @property
    def last_child(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[-1]

    @property
    def first_sibling(self) -> AbstractTreeItem:
        if self.parent is not None:
            return self.parent.first_child
        return self

    @property
    def last_sibling(self) -> AbstractTreeItem:
        if self.parent is not None:
            return self.parent.last_child
        return self

    @property
    def siblings(self) -> list[AbstractTreeItem]:
        if self.parent is not None:
            return self.parent.children.copy()
        return [self]
    
    @property
    def next_sibling(self) -> AbstractTreeItem | None:
        siblings: list[AbstractTreeItem] = self.siblings
        if siblings:
            i: int = siblings.index(self)
            if i+1 < len(siblings):
                return siblings[i+1]

    @property
    def prev_sibling(self) -> AbstractTreeItem | None:
        siblings: list[AbstractTreeItem] = self.siblings
        if siblings:
            i: int = siblings.index(self)
            if i-1 >= 0:
                return siblings[i-1]

    @property
    def sibling_index(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.children.index(self)
    
    def depth(self, root: AbstractTreeItem = None) -> int:
        depth: int = 0
        item: AbstractTreeItem = self
        while (item.parent is not None) and (item is not root):
            depth += 1
            item = item.parent
        return depth
    
    def branch_max_depth(self) -> int:
        max_depth: int = 0
        for item in self.depth_first():
            depth: int = item.depth(self)
            if depth > max_depth:
                max_depth = depth
        return max_depth
    
    def is_root(self) -> bool:
        return self.parent is None
    
    def is_leaf(self) -> bool:
        return not self.children
    
    def has_ancestor(self, ancestor: AbstractTreeItem) -> bool:
        item: AbstractTreeItem = self
        while item is not None:
            if item is ancestor:
                return True
            item = item.parent
        return False
    
    def append_child(self, item: AbstractTreeItem) -> None:
        item.parent = self
    
    def insert_child(self, index: int, item: AbstractTreeItem) -> None:
        item.parent = self
        # move item to index
        pos = self.children.index(item)
        if pos != index:
            self.children.insert(index, self.children.pop(pos))
    
    def remove_child(self, item: AbstractTreeItem) -> None:
        if item.parent is not self:
            return
        item.parent = None
    
    # depth-first iteration --------------------------------------------------
    
    def depth_first(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self
        while item is not None:
            yield item
            item = item._next_depth_first()
    
    def depth_first_reversed(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self._last_depth_first()
        while item is not None:
            yield item
            if item is self:
                break
            item = item._prev_depth_first()
    
    def _next_depth_first(self) -> AbstractTreeItem | None:
        if self.children:
            return self.first_child
        next_sibling: AbstractTreeItem = self.next_sibling
        if next_sibling is not None:
            return next_sibling
        item: AbstractTreeItem = self.parent
        while item is not None:
            next_sibling: AbstractTreeItem = item.next_sibling
            if next_sibling is not None:
                return next_sibling
            item = item.parent

    def _prev_depth_first(self) -> AbstractTreeItem | None:
        prev_sibling: AbstractTreeItem = self.prev_sibling
        if prev_sibling is not None:
            return prev_sibling._last_depth_first()
        if self.parent is not None:
            return self.parent
    
    def _last_depth_first(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.last_child
        return item

    # interface for QAbstractItemModel ----------------------------------------
    
    def data(self, column: int):
        # raise NotImplementedError
        return repr(self)  # for debugging
    
    def set_data(self, column: int, value) -> bool:
        # raise NotImplementedError
        return False


def test_tree():
    root = AbstractTreeItem()
    root.append_child(AbstractTreeItem())
    root.append_child(AbstractTreeItem())
    root.append_child(AbstractTreeItem())
    root.children[-1].append_child(AbstractTreeItem())
    root.children[-1].append_child(AbstractTreeItem())
    root.children[-1].append_child(AbstractTreeItem())
    root.children[-1].children[0].append_child(AbstractTreeItem())
    root.children[-1].children[0].append_child(AbstractTreeItem())
    print(root)


if __name__ == '__main__':
    test_tree()
