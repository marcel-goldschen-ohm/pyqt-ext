from __future__ import annotations

"""Port of the widgets/layouts/flowlayout example from Qt v6.x"""

import sys
from qtpy.QtCore import Qt, QMargins, QPoint, QRect, QSize
from qtpy.QtWidgets import QLayout, QPushButton, QSizePolicy, QWidget


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        next_items = self._item_list[1:] + self._item_list[-1:]
        for item, next_item in zip(self._item_list, next_items):
            style: QStyle = item.widget().style()
            control_type = item.widget().sizePolicy().controlType()
            next_control_type = next_item.widget().sizePolicy().controlType()
            layout_spacing_x = style.layoutSpacing(control_type, next_control_type, Qt.Orientation.Horizontal)
            layout_spacing_y = style.layoutSpacing(control_type, next_control_type, Qt.Orientation.Vertical)
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


if __name__ == "__main__":
    from qtpy.QtWidgets import *
    app = QApplication(sys.argv)
    ui = QWidget()
    flow = FlowLayout(ui)
    flow.setContentsMargins(0, 0, 0, 0)
    flow.setSpacing(0)
    flow.addWidget(QPushButton("Short"))
    flow.addWidget(QPushButton("Longer"))
    flow.addWidget(QPushButton("Different text"))
    flow.addWidget(QPushButton("More text"))
    flow.addWidget(QPushButton("Even longer button text"))
    flow.addWidget(QLabel("hi-ya!"))
    flow.addWidget(QLabel("text"))
    flow.addWidget(QCheckBox("cbox"))
    flow.addWidget(QRadioButton("radio"))
    flow.addWidget(QToolButton())
    flow.addWidget(QToolButton())
    flow.addWidget(QToolButton())
    flow.addWidget(QLineEdit())
    ui.show()
    sys.exit(app.exec())
