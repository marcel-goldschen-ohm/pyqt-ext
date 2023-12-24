""" PySide/PyQt button for selecting and displaying a color.
"""


from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class ColorButton(QToolButton):
    """ Button for selecting and displaying a color.
    """

    colorChanged = Signal(QColor)
    
    def __init__(self, color = QColor('transparent')):
        QToolButton.__init__(self)
        self.setColor(color)
        self.clicked.connect(self.pickColor)
    
    def color(self) -> QColor:
        return self._color

    def setColor(self, color: QColor):
        self.setStyleSheet(f'background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()}); border: 1px solid black;')
        self._color = color
        self.colorChanged.emit(color)
    
    def pickColor(self):
        color = QColorDialog.getColor(self.color(), None, "Select Color", options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.setColor(color)


def test_live():
    import sys
    app = QApplication(sys.argv)
    ui = ColorButton()
    ui.show()
    status = app.exec()
    sys.exit(status)


if __name__ == '__main__':
    test_live()
