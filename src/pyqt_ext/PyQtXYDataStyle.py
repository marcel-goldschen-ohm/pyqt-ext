""" Widget for editing the style of (x,y) data.

Style is stored in hashable dict.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext import ColorButton


ColorType = str | tuple[int | float] | list[int | float] | QColor


class XYDataStyleDict(dict):
    """ Hashable style dict for (x,y) data.

    'Color': str
    'LineStyle': str
    'LineWidth': float
    'Marker': str
    'MarkerSize': float
    'MarkerEdgeWidth': float
    'MarkerEdgeColor': str
    'MarkerFaceColor': str
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        # Qt.PenStyle.NoPen = 0
        # Qt.PenStyle.SolidLine = 1
        # Qt.PenStyle.DashLine = 2
        # Qt.PenStyle.DotLine = 3
        # Qt.PenStyle.DashDotLine = 4
        self.penStyles = [Qt.PenStyle.NoPen, Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine, Qt.PenStyle.DotLine, Qt.PenStyle.DashDotLine]
        self.lineStyles = ['none', '-', '--', ':', '-.']

        # Default markers supported by pyqtgraph.
        # Change these to whatever you want.
        self.markers = ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
    
    def color(self) -> str:
        return self.get('Color', 'auto')
    
    def setColor(self, value: ColorType):
        self['Color'] = XYDataStyleDict.toColorStr(value)
    
    def qcolor(self) -> QColor:
        return XYDataStyleDict.toQColor(self.color())
    
    def lineStyle(self) -> str:
        return self.get('LineStyle', '-')
    
    def setLineStyle(self, value: str | int | Qt.PenStyle | None):
        if value is None:
            value = 'none'
        elif isinstance(value, int):
            value = self.lineStyles[value]
        elif isinstance(value, Qt.PenStyle):
            index = self.penStyles.index(value)
            value = self.lineStyles[index]
        self['LineStyle'] = value
    
    def lineQtPenStyle(self) -> Qt.PenStyle:
        return Qt.PenStyle(self.lineStyles.index(self.lineStyle()))
    
    def lineWidth(self) -> float:
        return self.get('LineWidth', 1)
    
    def setLineWidth(self, value: float):
        self['LineWidth'] = value
    
    def marker(self) -> str:
        return self.get('Marker', 'none')
    
    def setMarker(self, value: str | None):
        if value is None:
            value = 'none'
        self['Marker'] = value
    
    def markerSize(self) -> float:
        return self.get('MarkerSize', 10)
    
    def setMarkerSize(self, value: float):
        self['MarkerSize'] = value
    
    def markerEdgeWidth(self) -> float:
        return self.get('MarkerEdgeWidth', self.lineWidth())
    
    def setMarkerEdgeWidth(self, value: float):
        self['MarkerEdgeWidth'] = value
    
    def markerEdgeColor(self) -> str:
        return self.get('MarkerEdgeColor', 'auto')
    
    def setMarkerEdgeColor(self, value: ColorType):
        self['MarkerEdgeColor'] = XYDataStyleDict.toColorStr(value)
    
    def markerEdgeQColor(self) -> QColor:
        return XYDataStyleDict.toQColor(self.markerEdgeColor())
    
    def markerFaceColor(self) -> str:
        return self.get('MarkerFaceColor', 'auto')
    
    def setMarkerFaceColor(self, value: ColorType):
        self['MarkerFaceColor'] = XYDataStyleDict.toColorStr(value)
    
    def markerFaceQColor(self) -> QColor:
        return XYDataStyleDict.toQColor(self.markerFaceColor())
    
    @staticmethod
    def toQColor(color: ColorType) -> QColor:
        if isinstance(color, QColor):
            return color
        if isinstance(color, str):
            color = color.strip()
            if color.lower() in ['auto', 'none']:
                return QColor('transparent')
            elif QColor.isValidColorName(color):
                return QColor(color)
            else:
                # (r,g,b) or (r,g,b,a)
                color = color.lstrip('(').rstrip(')').split(',')
                for i, part in enumerate(color):
                    try:
                        color[i] = int(part)
                    except:
                        color = [float(part) for part in color]
                        break
        # (r,g,b) or (r,g,b,a)
        if isinstance(color[0], float):
            return QColor.fromRgbF(*color)
        return QColor(*color)
    
    @staticmethod
    def toColorStr(color: ColorType) -> str:
        if isinstance(color, QColor):
            # (r,g,b,a) in [0,255]
            return f'({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})'
        if isinstance(color, str):
            if ',' in color:
                # (r,g,b) or (r,g,b,a)
                qcolor = XYDataStyleDict.toQColor(color)
                return XYDataStyleDict.toColorStr(qcolor)
            # TODO: sanity check?
            return color
        if isinstance(color, tuple) or isinstance(color, list):
            # (r,g,b) or (r,g,b,a)
            return '(' + ', '.join([str(part) for part in color]) + ')'


class XYDataStylePanel(QWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        form = QFormLayout(self)

        # color
        self.colorButton = ColorButton(QColor(0, 114, 189))
        self.autoColorCheckBox = QCheckBox('Auto')
        self.autoColorCheckBox.setChecked(False)
        self.autoColorCheckBox.stateChanged.connect(lambda isChecked: self.colorButton.setVisible(not isChecked))
        colorLayout = QHBoxLayout()
        colorLayout.setContentsMargins(0, 0, 0, 0)
        colorLayout.setSpacing(5)
        colorLayout.addWidget(self.colorButton)
        colorLayout.addWidget(self.autoColorCheckBox)
        self.colorButton.setVisible(not self.autoColorCheckBox.isChecked())
        form.addRow('Color', colorLayout)

        # line
        # Qt.PenStyle.NoPen = 0
        # Qt.PenStyle.SolidLine = 1
        # Qt.PenStyle.DashLine = 2
        # Qt.PenStyle.DotLine = 3
        # Qt.PenStyle.DashDotLine = 4
        self.lineStyles = ['none', '-', '--', ':', '-.']
        self.lineStyleComboBox = QComboBox()
        self.lineStyleComboBox.addItems(['No Line', 'Solid Line', 'Dash Line', 'Dot Line', 'Dash Dot Line'])
        self.lineStyleComboBox.setCurrentIndex(1)
        form.addRow('Line Style', self.lineStyleComboBox)
        
        self.lineWidthSpinBox = QDoubleSpinBox()
        self.lineWidthSpinBox.setMinimum(0)
        self.lineWidthSpinBox.setValue(1)
        form.addRow('Line Width', self.lineWidthSpinBox)

        # marker
        # pyqtgraph default markers
        self.markers = ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
        self.markerComboBox = QComboBox()
        self.markerComboBox.addItems([
            'None', 'Circle', 'Triangle Down', 'Triangle Up', 'Triangle Right', 'Triangle Left', 'Square', 
            'Pentagon', 'Hexagon', 'Star', 'Plus', 'Prism', 'Cross'])
        self.markerComboBox.setCurrentIndex(0)
        form.addRow('Marker', self.markerComboBox)

        self.markerSizeSpinBox = QDoubleSpinBox()
        self.markerSizeSpinBox.setMinimum(0)
        self.markerSizeSpinBox.setValue(10)
        form.addRow('Marker Size', self.markerSizeSpinBox)

        self.markerEdgeWidthSpinBox = QDoubleSpinBox()
        self.markerEdgeWidthSpinBox.setMinimum(0)
        self.markerEdgeWidthSpinBox.setValue(self.lineWidthSpinBox.value())
        form.addRow('Marker Edge Width', self.markerEdgeWidthSpinBox)

        self.markerEdgeColorButton = ColorButton(self.colorButton.color())
        self.autoMarkerEdgeColorCheckBox = QCheckBox('Auto')
        self.autoMarkerEdgeColorCheckBox.setChecked(True)
        self.autoMarkerEdgeColorCheckBox.stateChanged.connect(lambda isChecked: self.markerEdgeColorButton.setVisible(not isChecked))
        markerEdgeColorLayout = QHBoxLayout()
        markerEdgeColorLayout.setContentsMargins(0, 0, 0, 0)
        markerEdgeColorLayout.setSpacing(5)
        markerEdgeColorLayout.addWidget(self.markerEdgeColorButton)
        markerEdgeColorLayout.addWidget(self.autoMarkerEdgeColorCheckBox)
        self.markerEdgeColorButton.setVisible(not self.autoMarkerEdgeColorCheckBox.isChecked())
        form.addRow('Marker Edge Color', markerEdgeColorLayout)

        self.markerFaceColorButton = ColorButton(self.markerEdgeColorButton.color())
        self.autoMarkerFaceColorCheckBox = QCheckBox('Auto')
        self.autoMarkerFaceColorCheckBox.setChecked(True)
        self.autoMarkerFaceColorCheckBox.stateChanged.connect(lambda isChecked: self.markerFaceColorButton.setVisible(not isChecked))
        markerFaceColorLayout = QHBoxLayout()
        markerFaceColorLayout.setContentsMargins(0, 0, 0, 0)
        markerFaceColorLayout.setSpacing(5)
        markerFaceColorLayout.addWidget(self.markerFaceColorButton)
        markerFaceColorLayout.addWidget(self.autoMarkerFaceColorCheckBox)
        self.markerFaceColorButton.setVisible(not self.autoMarkerFaceColorCheckBox.isChecked())
        form.addRow('Marker Face Color', markerFaceColorLayout)
    
    def styleDict(self) -> XYDataStyleDict:
        style = XYDataStyleDict()
        if self.autoColorCheckBox.isChecked():
            style.setColor('auto')
        else:
            style.setColor(self.colorButton.color())
        style.setLineStyle(self.lineStyles[self.lineStyleComboBox.currentIndex()])
        style.setLineWidth(self.lineWidthSpinBox.value())
        style.setMarker(self.markers[self.markerComboBox.currentIndex()])
        style.setMarkerSize(self.markerSizeSpinBox.value())
        style.setMarkerEdgeWidth(self.markerEdgeWidthSpinBox.value())
        if self.autoMarkerEdgeColorCheckBox.isChecked():
            style.setMarkerEdgeColor('auto')
        else:
            style.setMarkerEdgeColor(self.markerEdgeColorButton.color())
        if self.autoMarkerFaceColorCheckBox.isChecked():
            style.setMarkerFaceColor('auto')
        else:
            style.setMarkerFaceColor(self.markerFaceColorButton.color())
        return style
    
    def setStyleDict(self, style: XYDataStyleDict):
        # color
        self.autoColorCheckBox.setChecked(style.color() == 'auto')
        if self.autoColorCheckBox.isChecked():
            self.colorButton.hide()
        else:
            self.colorButton.show()
            self.colorButton.setColor(style.qcolor())

        # line
        try:
            self.lineStyleComboBox.setCurrentIndex(self.lineStyles.index(style.lineStyle()))
        except:
            self.lineStyleComboBox.setCurrentIndex(1)
        self.lineWidthSpinBox.setValue(style.lineWidth())

        # marker
        try:
            self.markerComboBox.setCurrentIndex(self.markers.index(style.marker()))
        except:
            self.markerComboBox.setCurrentIndex(0)
        self.markerSizeSpinBox.setValue(style.markerSize())
        self.markerEdgeWidthSpinBox.setValue(style.markerEdgeWidth())
        self.autoMarkerEdgeColorCheckBox.setChecked(style.markerEdgeColor() == 'auto')
        if self.autoMarkerEdgeColorCheckBox.isChecked():
            self.markerEdgeColorButton.hide()
        else:
            self.markerEdgeColorButton.show()
            self.markerEdgeColorButton.setColor(style.markerEdgeQColor())
        self.autoMarkerFaceColorCheckBox.setChecked(style.markerFaceColor() == 'auto')
        if self.autoMarkerFaceColorCheckBox.isChecked():
            self.markerFaceColorButton.hide()
        else:
            self.markerFaceColorButton.show()
            self.markerFaceColorButton.setColor(style.markerFaceQColor())
    

def editXYDataStyle(style: XYDataStyleDict, parent: QWidget = None, title: str = None) -> XYDataStyleDict | None:
    panel = XYDataStylePanel()
    panel.setStyleDict(style)

    dlg = QDialog(parent)
    vbox = QVBoxLayout(dlg)
    vbox.addWidget(panel)

    btns = QDialogButtonBox()
    btns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    vbox.addWidget(btns)
    vbox.addStretch()

    if title is not None:
        dlg.setWindowTitle(title)
    dlg.setWindowModality(Qt.ApplicationModal)
    if dlg.exec() == QDialog.Accepted:
        return panel.styleDict()


def test_live():
    import sys 
    app = QApplication(sys.argv)
    ui = XYDataStylePanel()
    ui.show()
    status = app.exec()
    sys.exit(status)


if __name__ == '__main__':
    test_live()
