""" Base class for a tree of items to be used as a data interface with AbstractTreeModel(QAbstractItemModel).
"""

from __future__ import annotations
from warnings import warn
from typing import Callable
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
            - Depth-first, leaves, and ancestors iteration.
            - String representation of the tree.
            - And more...
        - An interface that is designed to work with AbstractTreeModel (i.e., QAbstractItemModel).

    In a derived class:
        1. Add attributes to store/interface with your data.
        2. Minimally reimplement `data` and `setData` methods (used by AbstractTreeModel).
        3. For nice printout, you may want to reimplement `__repr__`.
        4. For special linkage rules you may need to reimplement `setParent` and `insertChild`.
    """
    
    def __init__(self, name: str | None = None, parent: AbstractTreeItem | None = None) -> None:
        self._name: str | None = name
        self._parent: AbstractTreeItem | None = None
        self.children: list[AbstractTreeItem] = []
        if parent is not None:
            # properly handle parent linkage
            self.setParent(parent)
    
    def __repr__(self) -> str:
        """ Return a single line string representation of this item.
        
        See __str__ for a multi-line representation of the tree.
        """
        name: str = self.name()
        parent_name: str = self.parent().name() if self.parent() else '/'
        child_names: str = ','.join([child.name() for child in self.children])
        return f'name: {name}; parent: {parent_name}; children: {child_names}'
    
    def __str__(self) -> str:
        """ Returns a multi-line string representation of this item's tree branch.

        Each item is described by its name.
        """
        return self._tree_repr(lambda item: item.name())
    
    def __getitem__(self, path: str) -> AbstractTreeItem:
        """ Return subtree item at path starting from this item.

        !! For unique item access, all paths in the tree must be unique.
           Unique paths are not a requirement, it is up to you to enforce this if you want it.
           If the path is not unique, the first item with path is returned.
        """
        item: AbstractTreeItem = self
        path_parts = path.strip('/').split('/')
        for name in path_parts:
            try:
                child_names = [child.name() for child in item.children]
                child_index = child_names.index(name)
                item = item.children[child_index]
                if child_names.count(name) > 1:
                    warn('Path is not unique.')
            except Exception as error:
                warn(str(error))
                return None
        return item
    
    def __setitem__(self, path: str, new_item: AbstractTreeItem) -> None:
        """ Set subtree item at path starting from this item.

        !! For unique item access, all paths in the tree must be unique.
           Unique paths are not a requirement, it is up to you to enforce this if you want it.
           If the path is not unique, the first item with path will be set to the new item.
        """
        item: AbstractTreeItem = self
        path_parts = path.strip('/').split('/')
        if len(path_parts) == 0:
            raise ValueError('An item cannot set itself to a new item.')
        for name in path_parts[:-1]:
            try:
                child_names = [child.name() for child in item.children]
                child_index = child_names.index(name)
                item = item.children[child_index]
                if child_names.count(name) > 1:
                    warn('Path is not unique.')
            except Exception as error:
                # create new tree item to ensure validity of path
                item = AbstractTreeItem(name=name, parent=item)
        # set new_item at path
        new_item_name = path_parts[-1]
        child_names = [child.name for child in item.children]
        if new_item_name in child_names:
            # replace item at path with new_item
            child_index = child_names.index(new_item_name)
            item.children[child_index].setParent(None)  # remove current item at path
            item.insertChild(child_index, new_item)  # insert new_item at path
        else:
            # add new_item at path
            new_item.setParent(item)
        # name new_item according to path (ignore's new_item's current name)
        new_item.setName(new_item_name)
    
    def dumps(self) -> str:
        """ Returns a multi-line string representation of this item's tree branch.

        Each item is described by its repr.
        """
        return self._tree_repr(lambda item: repr(item))
    
    def _tree_repr(self, func: Callable[[AbstractTreeItem], str]) -> str:
        """ Returns a multi-line string representation of this item's tree branch.

        Each item is described by the single line str returned by func(item).
        See __str__ and dumps for examples.
        """
        items: list[AbstractTreeItem] = list(self.depthFirst())
        lines: list[str] = [func(item) for item in items]
        for i, item in enumerate(items):
            if item is self:
                continue
            if item is item.parent().lastChild():
                lines[i] = '\u2514' + '\u2500'*2 + ' ' + lines[i]
            else:
                lines[i] = '\u251C' + '\u2500'*2 + ' ' + lines[i]
            parent = item.parent()
            while parent is not self:
                if i < items.index(parent.parent().lastChild()):
                    lines[i] = '\u2502' + ' '*3 + lines[i]
                else:
                    lines[i] = ' '*4 + lines[i]
                parent = parent.parent()
        return '\n'.join(lines)
    
    def name(self) -> str:
        """ Retun this item's name, or the item's sibling index (or '' if root) if name is not defined.
        """
        if (self._name is None) or (self._name == ''):
            # return f'{self.__class__.__name__}@{id(self)}'
            row = self.siblingIndex()
            if row is None:
                return ''
            return f'{row}'
        return self._name
    
    def setName(self, name: str) -> None:
        self._name = name
    
    # tree linkage --------------------------------------------------

    def parent(self) -> AbstractTreeItem | None:
        return self._parent
    
    def setParent(self, parent: AbstractTreeItem | None) -> None:
        """ This is the primary method for restructuring the tree.

        This method restructures the AbstractTreeItem interface only,
        not any data associated with the AbstractTreeItems.

        Derived classes that need to mirror changes in the tree structure to their data 
        should reimplement parent.setter.
        
        Note: Together, setParent and insertChild cover all needed tree restructuring.
        See appendChild, insertChild, and removeChild.
        """
        if self.parent() is parent:
            # nothing to do
            return
        if (parent is not None) and parent.hasAncestor(self):
            raise ValueError('Cannot set parent to a descendant.')
        
        if self.parent() is not None:
            # detach from old parent
            if self in self.parent().children:
                self.parent().children.remove(self)
        if parent is not None:
            # attach to new parent (appends as last child)
            if self not in parent.children:
                parent.children.append(self)
        self._parent = parent
    
    def path(self) -> str:
        """ Return the /path/to/this/item from the root item.

        Path is constructed from item names separated by /.
        """
        item: AbstractTreeItem = self
        path = []
        while not item.isRoot():
            path.insert(0, item.name())
            item = item.parent()
        return '/' + '/'.join(path)
    
    def root(self) -> AbstractTreeItem:
        """ Return the root item of this item's branch. """
        item: AbstractTreeItem = self
        while item.parent() is not None:
            item = item.parent()
        return item
    
    def firstChild(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[0]

    def lastChild(self) -> AbstractTreeItem | None:
        if self.children:
            return self.children[-1]

    def siblings(self) -> list[AbstractTreeItem]:
        """ Return a list of this item's siblings (inclusive of this item).
        """
        if self.parent() is not None:
            return self.parent().children.copy()
        return [self]
    
    def firstSibling(self) -> AbstractTreeItem:
        """ Note: Can be this item.
        """
        if self.parent() is not None:
            return self.parent().firstChild()
        return self

    def lastSibling(self) -> AbstractTreeItem:
        """ Note: Can be this item.
        """
        if self.parent() is not None:
            return self.parent().lastChild()
        return self

    def nextSibling(self) -> AbstractTreeItem | None:
        if self.parent() is not None:
            siblings: list[AbstractTreeItem] = self.parent().children
            i: int = siblings.index(self)
            if i+1 < len(siblings):
                return siblings[i+1]

    def prevSibling(self) -> AbstractTreeItem | None:
        if self.parent() is not None:
            siblings: list[AbstractTreeItem] = self.parent().children
            i: int = siblings.index(self)
            if i-1 >= 0:
                return siblings[i-1]

    def siblingIndex(self) -> int | None:
        if self.parent() is not None:
            return self.parent().children.index(self)
    
    def isRoot(self) -> bool:
        return self.parent() is None
    
    def isLeaf(self) -> bool:
        return not self.children
    
    def hasAncestor(self, ancestor: AbstractTreeItem) -> bool:
        item: AbstractTreeItem = self.parent()
        while item is not None:
            if item is ancestor:
                return True
            item = item.parent()
        return False
    
    # tree mutation --------------------------------------------------

    def appendChild(self, child: AbstractTreeItem) -> None:
        child.setParent(self)
    
    def insertChild(self, index: int, child: AbstractTreeItem) -> None:
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
                self.children.insert(index, self.children.pop(pos))
    
    def removeChild(self, child: AbstractTreeItem) -> None:
        if child.parent() is not self:
            raise ValueError('Item is not a child of this item.')
        child.setParent(None)
    
    # ancestors iteration --------------------------------------------------

    def parents(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem | None = self.parent()
        end_item = None
        while item is not end_item:
            yield item
            item = item.parent()
    
    # depth-first iteration --------------------------------------------------
    
    def depthFirst(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self
        end_item: AbstractTreeItem | None = self.lastDepthFirst().nextDepthFirst()
        while item is not end_item:
            yield item
            item = item.nextDepthFirst()
    
    def reverseDepthFirst(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self.lastDepthFirst()
        end_item: AbstractTreeItem | None = self.prevDepthFirst()
        while item is not end_item:
            yield item
            item = item.prevDepthFirst()
    
    def nextDepthFirst(self) -> AbstractTreeItem | None:
        if self.children:
            return self.firstChild()
        next_sibling: AbstractTreeItem = self.nextSibling()
        if next_sibling is not None:
            return next_sibling
        item: AbstractTreeItem = self.parent()
        while item is not None:
            next_sibling: AbstractTreeItem = item.nextSibling()
            if next_sibling is not None:
                return next_sibling
            item = item.parent()
        return None

    def prevDepthFirst(self) -> AbstractTreeItem | None:
        prev_sibling: AbstractTreeItem = self.prevSibling()
        if prev_sibling is not None:
            return prev_sibling.lastDepthFirst()
        if self.parent() is not None:
            return self.parent()
        return None
    
    def lastDepthFirst(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.lastChild()
        return item
    
    # leaf iteration --------------------------------------------------
    
    def leaves(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self.firstLeaf()
        end_item: AbstractTreeItem | None = self.lastLeaf().nextLeaf()
        while item is not end_item:
            yield item
            item = item.nextLeaf()
    
    def reverseLeaves(self) -> Iterator[AbstractTreeItem]:
        item: AbstractTreeItem = self.lastLeaf()
        end_item: AbstractTreeItem | None = self.firstLeaf().prevLeaf()
        while item is not end_item:
            yield item
            item = item.prevLeaf()
    
    def nextLeaf(self) -> AbstractTreeItem | None:
        try:
            return self.nextDepthFirst().firstLeaf()
        except Exception:
            return None

    def prevLeaf(self) -> AbstractTreeItem | None:
        item: AbstractTreeItem | None = self.prevDepthFirst()
        while (item is not None) and item.children:
            item = item.prevDepthFirst()
        return item
    
    def firstLeaf(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.firstChild()
        return item
    
    def lastLeaf(self) -> AbstractTreeItem:
        item: AbstractTreeItem = self
        while item.children:
            item = item.lastChild()
        return item

    # misc --------------------------------------------------

    def depth(self, root: AbstractTreeItem = None) -> int:
        # Return depth of this item in the branch starting at root (or entire tree if root is None).
        depth: int = 0
        item: AbstractTreeItem = self
        while (item.parent() is not None) and (item is not root):
            depth += 1
            item = item.parent()
        return depth
    
    def maxDepthBelow(self) -> int:
        # Return the maximum depth within this item's branch.
        max_depth: int = 0
        for item in self.leaves():
            depth: int = item.depth(self)
            if depth > max_depth:
                max_depth = depth
        return max_depth
    
    @staticmethod
    def uniqueName(name: str, names: list[str], unique_counter_start: int = 2) -> str:
        """ May be useful for trees that require unique paths (i.e., sibling names).
        """
        if name not in names:
            return name
        base_name = name
        i = unique_counter_start
        name = f'{base_name}_{i}'
        while name in names:
            i += 1
            name = f'{base_name}_{i}'
        return name


def test_tree():
    root = AbstractTreeItem()
    AbstractTreeItem(parent=root)
    root.appendChild(AbstractTreeItem(name='child2'))
    root.insertChild(1, AbstractTreeItem(name='child3'))
    root.children[1].appendChild(AbstractTreeItem())
    root.children[1].appendChild(AbstractTreeItem())
    root.children[1].appendChild(AbstractTreeItem())
    grandchild2 = AbstractTreeItem(name='grandchild2')
    grandchild2.setParent(root['child2'])
    AbstractTreeItem(name='greatgrandchild', parent=root['child2/grandchild2'])
    
    print('\nInitial tree...')
    print(root)

    print('\nDepth first iteration...')
    for item in root.depthFirst():
        print(item.name())

    print('\nRemove grandchild2...')
    grandchild2.setParent(None)
    print(root)

    print('\nInsert grandchild2...')
    grandchild2.setParent(root['child2'])
    print(root)


if __name__ == '__main__':
    test_tree()
