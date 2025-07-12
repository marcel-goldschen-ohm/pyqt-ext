""" Data interface for a tree of key:value pairs.

e.g., Any level of nesting of dict and list objects.
"""

from __future__ import annotations
from warnings import warn
from typing import Any
from pyqt_ext.tree import AbstractTreeItem


class KeyValueTreeItem(AbstractTreeItem):
    
    def __init__(self, key: str | None = None, value: Any = None, parent: KeyValueTreeItem | None = None) -> None:
        self._key = key
        self._value = value
        AbstractTreeItem.__init__(self, parent=parent)
        self.setupSubtree()
    
    def key(self) -> str | int | None:
        # if parent is a list, return this item's sibling index
        parent: KeyValueTreeItem = self.parent()
        if parent is not None:
            parent_map: dict | list = parent.value()
            if isinstance(parent_map, list):
                return self.siblingIndex()
        
        # otherwise, return the stored key
        return self._key
    
    def setKey(self, key: str) -> None:
        # if parent is a dict, update the parent dict to reflect the key change
        parent: KeyValueTreeItem = self.parent()
        if parent is not None:
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
                if key == self._key:
                    return
                # make sure key is unique
                if key in parent_map:
                    warn(f'Key {key} already exists.')
                    # key = self.uniqueName(key, list(parent_map.keys()))
                    return
                # swap keys in map
                parent_map[key] = parent_map.pop(self._key)
        
        # set the stored key
        self._key = key
    
    def value(self) -> Any:
        return self._value
    
    def setValue(self, value: Any) -> None:
        self._value = value

        # update the parent key:value map to reflect the value change
        parent: KeyValueTreeItem = self.parent()
        if parent is not None:
            parent_map: dict | list = parent.value()
            parent_map[self.key()] = value
        
        # reset this item's subtree
        for child in self.children:
            child._parent = None
        self.children = []
        self.setupSubtree()
    
    def setupSubtree(self):
        """ Recursively build subtree if value is itself a container with key:value access.
        """
        value = self.value()
        if isinstance(value, dict):
            for key, val in value.items():
                KeyValueTreeItem(key, val, parent=self)
        elif isinstance(value, list):
            for val in value:
                # list keys are not explicitly set, they will default to the list index
                KeyValueTreeItem(None, val, parent=self)
    
    def name(self) -> str:
        """ name <==> key
        """
        key = self.key()
        return str(key) if key is not None else None
    
    def setName(self, name: str) -> None:
        """ name <==> key
        """
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
        
        if old_parent is not None:
            # remove from old parent mapping
            old_parent_map: dict | list = old_parent.value()
            # detach from old parent item
            old_parent_map.pop(self.key())
            old_parent.children.remove(self)
        
        if new_parent is not None:
            # attach to new parent item (appends as last child)
            new_parent.children.append(self)
            self._parent = new_parent
            # add to new parent mapping (unless it already exists such as when building an item tree for an existing data tree)
            new_parent_map: dict | list = new_parent.value()
            if isinstance(new_parent_map, dict):
                key = self.key()
                value = self.value()
                # ensure valid dict key
                if (key is None) or (key == ''):
                    sibling_keys = [sibling.key() for sibling in self.siblings()]
                    key = self.uniqueName('?', sibling_keys)
                if key not in new_parent_map:
                    new_parent_map[key] = value
                    self._key = key
                else:
                    # data at key already exists
                    # if it's the same as this item's value, do nothing -> building an item tree for an existing data tree
                    # otherwise, update the parent map's value
                    existing_value = new_parent_map[key]
                    if isinstance(existing_value, dict) or isinstance(existing_value, list):
                        if existing_value is not value:
                            self.setValue(value)
                    elif existing_value != value:
                        self.setValue(value)
            elif isinstance(new_parent_map, list):
                index: int = self.siblingIndex()
                value = self.value()
                while len(new_parent_map) < index:
                    # should not happen
                    new_parent_map.append(None)
                if len(new_parent_map) == index:
                    new_parent_map.append(value)
                else:
                    # data at index already exists
                    # if it's the same as this item's value, do nothing -> building an item tree for an existing data tree
                    # otherwise, update the parent map's value
                    existing_value = new_parent_map[index]
                    if isinstance(existing_value, dict) or isinstance(existing_value, list):
                        if existing_value is not value:
                            self.setValue(value)
                    elif existing_value != value:
                        self.setValue(value)
    
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
                # reorder key:value map
                this_map: dict | list = self.value()
                if isinstance(this_map, dict):
                    pass  # TODO... reorder dict? Not absolutely necessary.
                elif isinstance(this_map, list):
                    this_map.insert(index, this_map.pop(pos))
                # reorder child items
                self.children.insert(index, self.children.pop(pos))


def test_tree():
    tree = {
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
    root = KeyValueTreeItem(None, tree)
    print('-'*82)
    print(root)
    import json
    print(json.dumps(tree, indent='    '))

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

    print('-'*82)
    print('move /b/1 to first child of /c')
    c.insertChild(0, b['1'])
    print(root)

    print('-'*82)
    print('/c -> 82')
    c.setValue(82)
    print(root)

    print('-'*82)
    print('/c -> {a:1, b:2}')
    c.setValue({'a': 1, 'b': 2})
    print(root)


if __name__ == '__main__':
    test_tree()
