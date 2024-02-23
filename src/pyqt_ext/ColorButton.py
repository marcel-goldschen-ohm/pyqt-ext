""" PySide/PyQt button for selecting and displaying a color.
"""

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import qtawesome as qta
from pyqt_ext import ColorType, toQColor



class ColorButton(QToolButton):
    """ Button for selecting and displaying a color.
    """

    colorChanged = Signal(QColor)
    
    def __init__(self, color = None):
        QToolButton.__init__(self)
        self.setColor(color)
        self.clicked.connect(self.pickColor)
    
    def color(self) -> QColor:
        return self._color

    def setColor(self, color: ColorType):
        if color is None:
            color: QColor = QColor('transparent')
            self.setStyleSheet(f'background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()}); border: 1px solid black;')
            self.setIcon(qta.icon('ri.question-mark'))
            self._color = None
            return
        color: QColor = toQColor(color)
        self.setStyleSheet(f'background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()}); border: 1px solid black;')
        self.setIcon(QIcon())
        self._color = color
        self.colorChanged.emit(color)
    
    def pickColor(self):
        color: QColor = QColorDialog.getColor(self.color(), None, "Select Color", options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.setColor(color)


def test_live():
    app = QApplication()
    ui = ColorButton()
    ui.setColor("magenta")
    ui.setColor(None)
    ui.show()
    app.exec()


if __name__ == '__main__':
    test_live()
