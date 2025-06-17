""" Tree view for a `KeyValueTreeModel` with drag-and-drop, context menu, and mouse wheel expand/collapse.
"""

from __future__ import annotations
from typing import Callable
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import TreeView, KeyValueTreeItem, KeyValueTreeModel


class KeyValueTreeView(TreeView):

    def __init__(self, *args, **kwargs) -> None:
        TreeView.__init__(self, *args, **kwargs)

        # delegate
        self.setItemDelegate(KeyValueTreeViewDelegate(self))
    
    def customContextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu | None:
        model: KeyValueTreeModel = self.model()
        if model is None:
            return
        
        menu = QMenu(self)

        # context menu for item that was clicked on
        if index.isValid():
            item: KeyValueTreeItem = model.itemFromIndex(index)
            item_label = self.truncateLabel(item.path())
            menu.addAction(f'Insert New Item Before', lambda item=item: self.insertNewSiblingBefore(item))
            menu.addAction(f'Insert New Item After', lambda item=item: self.insertNewSiblingAfter(item))
            if not item.isLeaf():
                menu.addAction(f'Add New Child Item', lambda item=item: self.appendNewChild(item))
            menu.addSeparator()
            menu.addAction(f'Remove {item_label}', lambda item=item: self.askToRemoveItems([item]))
            menu.addSeparator()
        else:
            item: KeyValueTreeItem = model.root()
            menu.addAction(f'Add New Item', lambda item=item: self.appendNewChild(item))
            menu.addSeparator()
        
        self.appendDefaultContextMenu(menu)
        return menu
    
    def insertNewItem(self, parent_item: KeyValueTreeItem, row: int = -1) -> None:
        model: KeyValueTreeModel = self.model()
        if model is None:
            return
        
        parent_map: dict | list = parent_item.value()
        if isinstance(parent_map, dict):
            key = parent_item.uniqueName('New', list(parent_map.keys()))
        else:
            key = None
        if row == -1:
            row = len(parent_item.children)
        new_item = KeyValueTreeItem(key)
        model.insertItems(row, [new_item], parent_item)
    
    def insertNewSiblingBefore(self, item: KeyValueTreeItem) -> None:
        parent_item: KeyValueTreeItem = item.parent()
        row: int = item.siblingIndex()
        self.insertNewItem(parent_item, row)
    
    def insertNewSiblingAfter(self, item: KeyValueTreeItem) -> None:
        parent_item: KeyValueTreeItem = item.parent()
        row: int = item.siblingIndex() + 1
        self.insertNewItem(parent_item, row)
    
    def appendNewChild(self, parent_item: KeyValueTreeItem) -> None:
        row: int = -1
        self.insertNewItem(parent_item, row)


class KeyValueTreeViewDelegate(QStyledItemDelegate):
    """ Delegate for editing values.

    Provides checkbox for bool values.
    """
    def __init__(self, parent: QObject = None):
        QStyledItemDelegate.__init__(self, parent)
    
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        data = index.model().data(index, Qt.ItemDataRole.EditRole)
        if type(data) in [int, float, bool, str]:
            editor = QLineEdit(parent)
            editor.setText(str(data))
            return editor
        elif isinstance(data, tuple):
            editor = QLineEdit(parent)
            text = '(' + ', '.join(str(value) for value in data) + ')'
            editor.setText(text)
            return editor
        elif isinstance(data, list):
            editor = QLineEdit(parent)
            text = '[' + ', '.join(str(value) for value in data) + ']'
            editor.setText(text)
            return editor
        # elif isinstance(data, bool):
        #     # will handle with paint(), editorEvent(), and setModelData()
        #     return None
        return QStyledItemDelegate.createEditor(self, parent, option, index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        data = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if type(data) in [tuple, list, bool]:
            if isinstance(data, tuple):
                text = '(' + ', '.join(str(value) for value in data) + ')'
            elif isinstance(data, list):
                text = '[' + ', '.join(str(value) for value in data) + ']'
            elif isinstance(data, bool):
                text = ' ' + str(data)
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setPen(option.palette.highlightedText().color())
            else:
                painter.setPen(option.palette.text().color())
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            return
        # elif isinstance(data, bool):
        #     # paint checkbox without label
        #     checked = data
        #     opts = QStyleOptionButton()
        #     opts.state |= QStyle.State_Active
        #     if index.flags() & Qt.ItemFlag.ItemIsEditable:
        #         opts.state |= QStyle.State_Enabled
        #     else:
        #         opts.state |= QStyle.State_ReadOnly
        #     if checked:
        #         opts.state |= QStyle.State_On
        #     else:
        #         opts.state |= QStyle.State_Off
        #     opts.rect = self.getCheckBoxRect(option)
        #     QApplication.style().drawControl(QStyle.CE_CheckBox, opts, painter)
        #     return
        return QStyledItemDelegate.paint(self, painter, option, index)

    def editorEvent(self, event: QEvent, model: KeyValueTreeModel, option: QStyleOptionViewItem, index: QModelIndex):
        # data = index.model().data(index, Qt.ItemDataRole.EditRole)
        # if isinstance(data, bool):
        #     # handle checkbox events
        #     if not (index.flags() & Qt.ItemFlag.ItemIsEditable):
        #         return False
        #     if event.button() == Qt.MouseButton.LeftButton:
        #         if event.type() == QEvent.MouseButtonRelease:
        #             if self.getCheckBoxRect(option).contains(event.pos()):
        #                 self.setModelData(None, model, index)
        #                 return True
        #         elif event.type() == QEvent.MouseButtonDblClick:
        #             if self.getCheckBoxRect(option).contains(event.pos()):
        #                 return True
        #     return False
        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def setModelData(self, editor: QWidget, model: KeyValueTreeModel, index: QModelIndex):
        item: KeyValueTreeItem = model.itemFromIndex(index)
        old_value = item.value()
        if type(old_value) in [dict, list] and len(old_value) > 0:
            answer = QMessageBox.question(self.parent(), 'Overwrite?', 'Overwrite non-empty key:value map?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.No:
                return
        if isinstance(editor, QLineEdit):
            new_value = str_to_value(editor.text())
            # did change involves a key:value map?
            mapping_changed = (type(old_value) in [dict, list]) or (type(new_value) in [dict, list])
            if mapping_changed:
                view: KeyValueTreeView = self.parent()
                view.storeState()
            model.setData(index, new_value, Qt.ItemDataRole.EditRole)
            if mapping_changed:
                view.restoreState()
            return
        # elif isinstance(data, bool):
        #     checked = not data
        #     model.setData(index, checked, Qt.ItemDataRole.EditRole)
        #     return
        return QStyledItemDelegate.setModelData(self, editor, model, index)

    def getCheckBoxRect(self, option: QStyleOptionViewItem):
        """ Get rect for checkbox positioned in option.rect.
        """
        # Get size of a standard checkbox
        opts = QStyleOptionButton()
        checkBoxRect = QApplication.style().subElementRect(QStyle.SE_CheckBoxIndicator, opts, None)
        # Position checkbox in option.rect
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()
        # checkBoxTopLeftCorner = QPoint(x + w / 2 - checkBoxRect.width() / 2, y + h / 2 - checkBoxRect.height() / 2)  # horizontal center, vertical center
        checkBoxTopLeftCorner = QPoint(x, y + h / 2 - checkBoxRect.height() / 2)  # horizontal left, vertical center
        return QRect(checkBoxTopLeftCorner, checkBoxRect.size())


def str_to_value(text: str) -> bool | int | float | str | tuple | list | dict:
    if text.lower().strip() == 'true':
        return True
    if text.lower().strip() == 'false':
        return False
    if text.lstrip().startswith('(') and text.rstrip().endswith(')'):
        return tuple([str_to_value(item.strip()) for item in text.strip()[1:-1].split(',') if item.strip() != ''])
    if text.lstrip().startswith('[') and text.rstrip().endswith(']'):
        return [str_to_value(item.strip()) for item in text.strip()[1:-1].split(',') if item.strip() != '']
    if text.lstrip().startswith('{') and text.rstrip().endswith('}'):
        values = {}
        for field in [item for item in text.strip()[1:-1].split(',') if ':' in item]:
            key, value = field.split(':')
            values[key.strip()] = str_to_value(value.strip())
        return values
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def test_live():
    data = {
        'a': 1,
        'b': [4, 8, (1, 5.5, True, 'good'), 5, 7, 99, True, False, 'hi', 'bye'],
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

    app = QApplication()
    # root = KeyValueTreeItem(data)
    model = KeyValueTreeModel(data)
    view = KeyValueTreeView()
    view.setModel(model)
    view.show()
    view.resize(QSize(800, 600))
    view.showAll()
    # model.keyChanged.connect(lambda: print(model.root()))
    # model.valueChanged.connect(lambda: print(model.root()))
    app.exec()

    import json
    print(json.dumps(data, indent='    '))

if __name__ == '__main__':
    test_live()
