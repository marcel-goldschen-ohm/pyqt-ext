""" Base class for a tree of items to be used as a data interface with AbstractTreeModel(QAbstractItemModel).
"""

from __future__ import annotations
from collections.abc import Iterator


class AbstractTreeItem():
    """ Base class for a tree of items to be used as a data interface with AbstractTreeModel(QAbstractItemModel).
    
    !!! This only implements the tree structure.
        You must define any data variables in a derived class.
    
    What you get out-of-the-box:
        - A host of methods for navigating and manipulating the tree structure:
            - Parent/child linkage.
            - Host of other linkage properties: siblings, first/last child, first/last sibling, etc.
            - Path-based item access based on item names.
            - Depth-first iteration.
            - String representation of the tree.
            - And more...
        - An interface that is designed to work with AbstractTreeModel (i.e., QAbstractItemModel).

    In a derived class:
        1. Add attributes to store/interface with your data.
        2. Minimally reimplement `get_data` and `set_data` methods (used by AbstractTreeModel).
        3. For nice printout, you may want to reimplement `__repr__`.
        4. For special linkage rules you may need to reimplement `parent.setter` and `insert_child`.
    """
    
    def __init__(self, name: str | None = None, parent: AbstractTreeItem | None = None):
        self.name: str | None = name
        self.parent: AbstractTreeItem | None = parent
        self.children: list[AbstractTreeItem] = []
    
    def __repr__(self):
        # Return a single line string representation of this item.
        # See __str__ for a multi-line representation of the tree.
        return self.name
    
    def __str__(self):
        # returns a multi-line string representation of this item's tree branch
        items: list[AbstractTreeItem] = list(self.depth_first())
        lines: list[str] = [repr(item) for item in items]
        for i, item in enumerate(items):
            if item is self:
                continue
            if item is item.parent.last_child:
                lines[i] = '\u2514' + '\u2500'*2 + ' ' + lines[i]
            else:
                lines[i] = '\u251C' + '\u2500'*2 + ' ' + lines[i]
            parent = item.parent
            while parent is not self:
                if i < items.index(parent.last_sibling):
                    lines[i] = '\u2502' + ' '*3 + lines[i]
                else:
                    lines[i] = ' '*4 + lines[i]
                parent = parent.parent
        return '\n'.join(lines)
    
    def __getitem__(self, path: str) -> AbstractTreeItem:
        """ Return item at path either from the root item (if path starts with /) or otherwise from this item. """
        if path.startswith('/'):
            # path from root item (first name in path must be a child of the root item)
            item: AbstractTreeItem = self.root
        else:
            # path from this item (first name in path must be a child of this item)
            item: AbstractTreeItem = self
        path = path.strip('/').split('/')
        for name in path:
            try:
                child_names = [child.name for child in item.children]
                child_index = child_names.index(name)
                item = item.children[child_index]
            except:
                return None
        return item
    
    @property
    def parent(self) -> AbstractTreeItem | None:
        return getattr(self, '_parent', None)
    
    @parent.setter
    def parent(self, parent: AbstractTreeItem | None) -> None:
        if self.parent is parent:
            return
        if parent.has_ancestor(self):
            raise ValueError('Cannot set parent to a descendant.')
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
    def name(self) -> str:
        name: str | None = getattr(self, '_name', None)
        if name is None:
            return self.__class__.__name__ + '@' + str(id(self))
        return name
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name
    
    @property
    def path(self) -> str:
        item: AbstractTreeItem = self
        path = []
        while not item.is_root():
            path.insert(0, item.name)
            item = item.parent
        return '/' + '/'.join(path)
    
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

    def set_parent(self, parent: AbstractTreeItem) -> bool:
        try:
            self.parent = parent
            return True
        except:
            return False
    
    def append_child(self, child: AbstractTreeItem) -> bool:
        try:
            child.parent = self
            return True
        except:
            return False
    
    def insert_child(self, index: int, child: AbstractTreeItem) -> bool:
        if not (0 <= index <= len(self.children)):
            return False
        try:
            child.parent = self
            # move item to index
            pos = self.children.index(child)
            if pos != index:
                self.children.insert(index, self.children.pop(pos))
            return True
        except:
            return False
    
    def remove_child(self, child: AbstractTreeItem) -> bool:
        if child.parent is not self:
            return False
        try:
            child.parent = None
            return True
        except:
            return False
    
    # depth-first iteration --------------------------------------------------
    
    def depth_first(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self
        end_item: AbstractTreeItem | None = self._last_depth_first()._next_depth_first()
        while item is not end_item:
            yield item
            item = item._next_depth_first()
    
    def reverse_depth_first(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self._last_depth_first()
        end_item: AbstractTreeItem | None = self._prev_depth_first()
        while item is not end_item:
            yield item
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
    
    # leaf iteration --------------------------------------------------
    
    def leaves(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self._first_leaf()
        end_item: AbstractTreeItem | None = self._last_leaf()._next_leaf()
        while item is not end_item:
            yield item
            item = item._next_leaf()
    
    def reverse_leaves(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self._last_leaf()
        end_item: AbstractTreeItem | None = self._first_leaf()._prev_leaf()
        while item is not end_item:
            yield item
            item = item._prev_leaf()
    
    def _next_leaf(self) -> AbstractTreeItem | None:
        try:
            return self._next_depth_first()._first_leaf()
        except:
            return None

    def _prev_leaf(self) -> AbstractTreeItem | None:
        item: AbstractTreeItem | None = self._prev_depth_first()
        while (item is not None) and item.children:
            item = item._prev_depth_first()
        return item
    
    def _first_leaf(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.first_child
        return item
    
    def _last_leaf(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.last_child
        return item

    # interface for QAbstractItemModel ----------------------------------------
    
    def get_data(self, column: int):
        # raise NotImplementedError
        if column == 0:
            # for debugging
            return repr(self)
    
    def set_data(self, column: int, value) -> bool:
        # raise NotImplementedError
        return False


def test_tree():
    root = AbstractTreeItem()
    AbstractTreeItem(parent=root)
    root.append_child(AbstractTreeItem(name='child2'))
    root.insert_child(1, AbstractTreeItem(name='child3'))
    root.children[1].append_child(AbstractTreeItem())
    grandchild2 = AbstractTreeItem(name='grandchild2')
    grandchild2.parent = root['child2']
    AbstractTreeItem(name='greatgrandchild', parent=root['/child2/grandchild2'])
    print(root)

    print('Depth first iteration...')
    for item in root.depth_first():
        print(item.name)


if __name__ == '__main__':
    test_tree()
