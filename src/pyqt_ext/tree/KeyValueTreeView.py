""" Tree view for a KeyValueTreeModel with context menu and mouse wheel expand/collapse.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.tree import TreeView, KeyValueTreeItem, KeyValueTreeModel


class KeyValueTreeView(TreeView):

    def __init__(self, parent: QObject = None) -> None:
        TreeView.__init__(self, parent)

        # delegate
        self.setItemDelegate(KeyValueTreeViewDelegate(self))
    
    def contextMenu(self, index: QModelIndex = QModelIndex()) -> QMenu:
        menu: QMenu = TreeView.contextMenu(self, index)
       
        model: KeyValueTreeModel = self.model()
        if model is None:
            return menu
        
        if not index.isValid():
            if model.root() is not None:
                menu.addSeparator()
                menu.addAction('Add item', lambda model=model, row=len(model.root().children), item=KeyValueTreeItem('New item', ''), parentIndex=QModelIndex(): model.insertItems(row, [item], parentIndex))
            return menu
        
        item: KeyValueTreeItem = model.itemFromIndex(index)
        menu.addSeparator()
        menu.addAction('Insert before', lambda model=model, row=item.sibling_index, item=KeyValueTreeItem('New item', ''), parentIndex=model.parent(index): model.insertItems(row, [item], parentIndex))
        menu.addAction('Insert after', lambda model=model, row=item.sibling_index + 1, item=KeyValueTreeItem('New item', ''), parentIndex=model.parent(index): model.insertItems(row, [item], parentIndex))
        if item.is_container():
            menu.addAction('Append child', lambda model=model, row=len(item.children), item=KeyValueTreeItem('New item', ''), parentIndex=index: model.insertItems(row, [item], parentIndex))
        
        return menu


class KeyValueTreeViewDelegate(QStyledItemDelegate):
    """ Delegate for editing values.

    Provides checkbox for bool values.
    """
    def __init__(self, parent: QObject = None):
        QStyledItemDelegate.__init__(self, parent)
    
    def createEditor(self, parent, option, index):
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

    def paint(self, painter, option, index):
        data = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if type(data) in [tuple, list, bool]:
            if isinstance(data, tuple):
                text = '(' + ', '.join(str(value) for value in data) + ')'
            elif isinstance(data, list):
                text = '[' + ', '.join(str(value) for value in data) + ']'
            elif isinstance(data, bool):
                text = ' ' + str(data)
            if option.state & QStyle.State_Selected:
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

    def editorEvent(self, event, model, option, index):
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

    def setModelData(self, editor, model, index):
        data = index.model().data(index, Qt.ItemDataRole.EditRole)
        if type(data) in [dict, list] and len(data) > 0:
            answer = QMessageBox.question(self.parent(), 'Overwrite?', 'Overwrite non-empty container?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.No:
                return
        if isinstance(editor, QLineEdit):
            value = str_to_value(editor.text())
            model.setData(index, value, Qt.ItemDataRole.EditRole)
            if type(value) in [dict, list] or type(data) in [dict, list]:
                view: KeyValueTreeView = self.parent()
                view.resetModel()
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


def unique_name(name: str, names: list[str]) -> str:
    if name not in names:
        return name
    i: int = 1
    uname = f'{name}_{i}'
    while uname in names:
        i += 1
        uname = f'{name}_{i}'
    return uname


def test_live():
    from pyqt_ext.tree import KeyValueDndTreeModel
    
    app = QApplication()

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
    root = KeyValueTreeItem('/', data)
    model = KeyValueDndTreeModel(root)
    view = KeyValueTreeView()
    view.setSelectionMode(QAbstractItemView.ExtendedSelection)
    view.setModel(model)
    view.show()
    view.resize(QSize(400, 400))

    app.exec()

if __name__ == '__main__':
    test_live()
