""" Widget for editing the style of (x,y) data.

Style is stored in hashable dict.
"""

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_tools import ColorButton


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
        self.line_styles = ['none', '-', '--', ':', '-.']

        # Default markers supported by pyqtgraph.
        # Change these to whatever you want.
        self.markers = ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
    
    @property
    def color(self) -> str:
        return self.get('Color', 'auto')
    
    @color.setter
    def color(self, value: ColorType):
        self['Color'] = XYDataStyleDict.color_to_str(value)
    
    @property
    def line_style(self) -> str:
        return self.get('LineStyle', '-')
    
    @line_style.setter
    def line_style(self, value: str | None):
        if value is None:
            value = 'none'
        self['LineStyle'] = value
    
    @property
    def line_width(self) -> float:
        return self.get('LineWidth', 1)
    
    @line_width.setter
    def line_width(self, value: float):
        self['LineWidth'] = value
    
    @property
    def marker(self) -> str:
        return self.get('Marker', 'none')
    
    @marker.setter
    def marker(self, value: str | None):
        if value is None:
            value = 'none'
        self['Marker'] = value
    
    @property
    def marker_size(self) -> float:
        return self.get('MarkerSize', 10)
    
    @marker_size.setter
    def marker_size(self, value: float):
        self['MarkerSize'] = value
    
    @property
    def marker_edge_width(self) -> float:
        return self.get('MarkerEdgeWidth', self.line_width)
    
    @marker_edge_width.setter
    def marker_edge_width(self, value: float):
        self['MarkerEdgeWidth'] = value
    
    @property
    def marker_edge_color(self) -> str:
        return self.get('MarkerEdgeColor', 'auto')
    
    @marker_edge_color.setter
    def marker_edge_color(self, value: ColorType):
        self['MarkerEdgeColor'] = XYDataStyleDict.color_to_str(value)
    
    @property
    def marker_face_color(self) -> str:
        return self.get('MarkerFaceColor', 'auto')
    
    @marker_face_color.setter
    def marker_face_color(self, value: ColorType):
        self['MarkerFaceColor'] = XYDataStyleDict.color_to_str(value)
    
    @property
    def qcolor(self) -> QColor:
        return XYDataStyleDict.to_qcolor(self.color)
    
    @property
    def marker_edge_qcolor(self) -> QColor:
        return XYDataStyleDict.to_qcolor(self.marker_edge_color)
    
    @property
    def marker_face_qcolor(self) -> QColor:
        return XYDataStyleDict.to_qcolor(self.marker_face_color)
    
    @staticmethod
    def color_to_qcolor(color: ColorType) -> QColor:
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
    def color_to_str(color: ColorType) -> str:
        if isinstance(color, QColor):
            # (r,g,b,a) in [0,1]
            return f'({color.redF()}, {color.greenF()}, {color.blueF()}, {color.alphaF()})'
        if isinstance(color, str):
            # TODO: check for validity of color str?
            return color.strip()
        if isinstance(color, tuple) or isinstance(color, list):
            # (r,g,b) or (r,g,b,a)
            return '(' + ', '.join([str(part) for part in color]) + ')'


class XYDataStylePanel(QWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self._style = XYDataStyleDict()

        self.vboxLayout = QVBoxLayout(self)

        # color
        self.colorGroupBox = QGroupBox('Color')
        self.colorFormLayout = QFormLayout(self.colorGroupBox)

        color = self._style.color
        if color == 'auto':
            qcolor = QColor(0, 114, 189)
        else:
            qcolor = XYDataStyleDict.color_to_qcolor(color)
        self.colorButton = ColorButton(qcolor)
        self.colorButton.colorChanged.connect(self.onColorChanged)
        self.autoColorCheckBox = QCheckBox('Auto')
        self.autoColorCheckBox.setChecked(color == 'auto')
        self.autoColorCheckBox.stateChanged.connect(self.onColorChanged)
        colorLayout = QHBoxLayout()
        colorLayout.setContentsMargins(0, 0, 0, 0)
        colorLayout.setSpacing(5)
        colorLayout.addWidget(self.colorButton)
        colorLayout.addWidget(self.autoColorCheckBox)
        self.colorFormLayout.addRow('Color', colorLayout)
        self.colorButton.setVisible(not self.autoColorCheckBox.isChecked())

        self.vboxLayout.addWidget(self.colorGroupBox)

        # line
        self.lineGroupBox = QGroupBox('Line')
        self.lineFormLayout = QFormLayout(self.lineGroupBox)
        
        # Qt.PenStyle.NoPen = 0
        # Qt.PenStyle.SolidLine = 1
        # Qt.PenStyle.DashLine = 2
        # Qt.PenStyle.DotLine = 3
        # Qt.PenStyle.DashDotLine = 4
        self.lineStyles = ['none', '-', '--', ':', '-.']
        self.lineStyleComboBox = QComboBox()
        self.lineStyleComboBox.addItems(['No Line', 'Solid Line', 'Dash Line', 'Dot Line', 'Dash Dot Line'])
        try:
            self.lineStyleComboBox.setCurrentIndex(self.lineStyles.index(self._style.line_style))
        except:
            self.lineStyleComboBox.setCurrentIndex(1)
        self.lineStyleComboBox.currentIndexChanged.connect(self.onLineStyleChanged)
        self.lineFormLayout.addRow('Style', self.lineStyleComboBox)
        
        self.lineWidthSpinBox = QDoubleSpinBox()
        self.lineWidthSpinBox.setMinimum(0)
        self.lineWidthSpinBox.setValue(self._style.line_width)
        self.lineWidthSpinBox.valueChanged.connect(self.onLineWidthChanged)
        self.lineFormLayout.addRow('Width', self.lineWidthSpinBox)

        self.vboxLayout.addWidget(self.lineGroupBox)
        self.onLineStyleChanged()

        # marker
        self.markerGroupBox = QGroupBox('Marker')
        self.markerFormLayout = QFormLayout(self.markerGroupBox)

        # pyqtgraph default markers
        self.markers = ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
        self.markerComboBox = QComboBox()
        self.markerComboBox.addItems([
            'None', 'Circle', 'Triangle Down', 'Triangle Up', 'Triangle Right', 'Triangle Left', 'Square', 
            'Pentagon', 'Hexagon', 'Star', 'Plus', 'Prism', 'Cross'])
        try:
            self.markerComboBox.setCurrentIndex(self.markers.index(self._style.marker))
        except:
            self.markerComboBox.setCurrentIndex(0)
        self.markerComboBox.currentIndexChanged.connect(self.onMarkerChanged)
        self.markerFormLayout.addRow('Marker', self.markerComboBox)

        self.markerSizeSpinBox = QDoubleSpinBox()
        self.markerSizeSpinBox.setMinimum(0)
        self.markerSizeSpinBox.setValue(self._style.marker_size)
        self.markerSizeSpinBox.valueChanged.connect(self.onMarkerSizeChanged)
        self.markerFormLayout.addRow('Size', self.markerSizeSpinBox)

        self.markerEdgeWidthSpinBox = QDoubleSpinBox()
        self.markerEdgeWidthSpinBox.setMinimum(0)
        self.markerEdgeWidthSpinBox.setValue(self._style.marker_edge_width)
        self.markerEdgeWidthSpinBox.valueChanged.connect(self.onMarkerEdgeWidthChanged)
        self.markerFormLayout.addRow('Edge Width', self.markerEdgeWidthSpinBox)

        markerEdgeColor = self._style.marker_edge_color
        if markerEdgeColor == 'auto':
            markerEdgeQColor = qcolor
        else:
            markerEdgeQColor = XYDataStyleDict.color_to_qcolor(markerEdgeColor)
        self.markerEdgeColorButton = ColorButton(markerEdgeQColor)
        self.markerEdgeColorButton.colorChanged.connect(self.onMarkerEdgeColorChanged)
        self.autoMarkerEdgeColorCheckBox = QCheckBox('Auto')
        self.autoMarkerEdgeColorCheckBox.setChecked(markerEdgeColor == 'auto')
        self.autoMarkerEdgeColorCheckBox.stateChanged.connect(lambda isChecked: self.markerEdgeColorButton.setVisible(not isChecked))
        markerEdgeColorLayout = QHBoxLayout()
        markerEdgeColorLayout.setContentsMargins(0, 0, 0, 0)
        markerEdgeColorLayout.setSpacing(5)
        markerEdgeColorLayout.addWidget(self.markerEdgeColorButton)
        markerEdgeColorLayout.addWidget(self.autoMarkerEdgeColorCheckBox)
        self.markerFormLayout.addRow('Edge Color', markerEdgeColorLayout)
        self.markerEdgeColorButton.setVisible(not self.autoMarkerEdgeColorCheckBox.isChecked())

        markerFaceColor = self._style.marker_face_color
        if markerFaceColor == 'auto':
            markerFaceQColor = markerEdgeQColor
        else:
            markerFaceQColor = XYDataStyleDict.color_to_qcolor(markerFaceColor)
        self.markerFaceColorButton = ColorButton(markerFaceQColor)
        self.markerFaceColorButton.colorChanged.connect(self.onMarkerFaceColorChanged)
        self.autoMarkerFaceColorCheckBox = QCheckBox('Auto')
        self.autoMarkerFaceColorCheckBox.setChecked(markerFaceColor == 'auto')
        self.autoMarkerFaceColorCheckBox.stateChanged.connect(lambda isChecked: self.markerFaceColorButton.setVisible(not isChecked))
        markerFaceColorLayout = QHBoxLayout()
        markerFaceColorLayout.setContentsMargins(0, 0, 0, 0)
        markerFaceColorLayout.setSpacing(5)
        markerFaceColorLayout.addWidget(self.markerFaceColorButton)
        markerFaceColorLayout.addWidget(self.autoMarkerFaceColorCheckBox)
        self.markerFormLayout.addRow('Face Color', markerFaceColorLayout)
        self.markerFaceColorButton.setVisible(not self.autoMarkerFaceColorCheckBox.isChecked())

        self.vboxLayout.addWidget(self.markerGroupBox)
        self.onMarkerChanged()

        self.vboxLayout.addStretch()
    
    def style(self) -> XYDataStyleDict:
        return self._style
    
    def setStyle(self, style: XYDataStyleDict):
        self._style = style
        
        try:
            self.lineStyleComboBox.setCurrentIndex(self.lineStyles.index(self._style.line_style))
        except:
            self.lineStyleComboBox.setCurrentIndex(1)
        self.onLineStyleChanged()
        
        self.lineWidthSpinBox.setValue(self._style.line_width)

        color = self._style.color
        qcolor = XYDataStyleDict.color_to_qcolor(color)
        self.colorButton.setColor(qcolor)
        self.autoColorCheckBox.setChecked(color == 'auto')
        self.onColorChanged()

        try:
            self.markerComboBox.setCurrentIndex(self.markers.index(self._style.marker))
        except:
            self.markerComboBox.setCurrentIndex(0)
        self.onMarkerChanged()
        
        self.markerSizeSpinBox.setValue(self._style.marker_size)

        self.markerEdgeWidthSpinBox.setValue(self._style.marker_edge_width)

        markerEdgeColor = self._style.marker_edge_color
        markerEdgeQColor = XYDataStyleDict.color_to_qcolor(markerEdgeColor)
        self.markerEdgeColorButton.setColor(markerEdgeQColor)
        self.autoMarkerEdgeColorCheckBox.setChecked(markerEdgeColor == 'auto')
        self.onMarkerEdgeColorChanged()

        markerFaceColor = self._style.marker_face_color
        markerFaceQColor = XYDataStyleDict.color_to_qcolor(markerFaceColor)
        self.markerFaceColorButton.setColor(markerFaceQColor)
        self.autoMarkerFaceColorCheckBox.setChecked(markerFaceColor == 'auto')
        self.onMarkerFaceColorChanged()
    
    @Slot()
    def onLineStyleChanged(self):
        self._style.line_style = self.lineStyles[self.lineStyleComboBox.currentIndex()]
        try:
            isLine: bool = not (self._style.line_style == 'none')
            self.lineFormLayout.setRowVisible(1, isLine)
        except:
            # above only works in PyQt6
            pass
    
    @Slot()
    def onLineWidthChanged(self):
        self._style.line_width = self.lineWidthSpinBox.value()
    
    @Slot()
    def onColorChanged(self):
        if self.autoColorCheckBox.isChecked():
            self._style.color = 'auto'
            self.colorButton.hide()
        else:
            qcolor: QColor = self.colorButton.color()
            self._style.color = XYDataStyleDict.color_to_str(qcolor)
            self.colorButton.show()
    
    @Slot()
    def onMarkerChanged(self):
        self._style.marker = self.markers[self.markerComboBox.currentIndex()]
        try:
            isMarker: bool = not (self._style.marker == 'none')
            for row in range(1, self.markerFormLayout.rowCount()):
                self.markerFormLayout.setRowVisible(row, isMarker)
        except:
            # above only works in PyQt6
            pass
        self.markerEdgeColorButton.setVisible(not self.autoMarkerEdgeColorCheckBox.isChecked())
        self.markerFaceColorButton.setVisible(not self.autoMarkerFaceColorCheckBox.isChecked())
    
    @Slot()
    def onMarkerSizeChanged(self):
        self._style.marker_size = self.markerSizeSpinBox.value()
    
    @Slot()
    def onMarkerEdgeWidthChanged(self):
        self._style.marker_edge_width = self.markerEdgeWidthSpinBox.value()
    
    @Slot()
    def onMarkerEdgeColorChanged(self):
        if self.autoMarkerEdgeColorCheckBox.isChecked():
            self._style.color = 'auto'
            self.markerEdgeColorButton.hide()
        else:
            qcolor: QColor = self.markerEdgeColorButton.color()
            self._style.marker_edge_color = XYDataStyleDict.color_to_str(qcolor)
            self.markerEdgeColorButton.show()
    
    @Slot()
    def onMarkerFaceColorChanged(self):
        if self.autoMarkerFaceColorCheckBox.isChecked():
            self._style.color = 'auto'
            self.markerFaceColorButton.hide()
        else:
            qcolor: QColor = self.markerFaceColorButton.color()
            self._style.marker_face_color = XYDataStyleD.color_to_str(qcolor)
            self.markerFaceColorButton.show()
    

def editXYDataStyle(style: XYDataStyleDict, parent: QWidget = None, title: str = None) -> XYDataStyleDict | None:
    panel = XYDataStylePanel()
    panel.setStyle(style)

    dlg = QDialog(parent)
    vbox = QVBoxLayout(dlg)
    vbox.addWidget(panel)

    btns = QDialogButtonBox()
    btns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    vbox.addWidget(btns)

    if title is not None:
        dlg.setWindowTitle(title)
    dlg.setWindowModality(Qt.ApplicationModal)
    if dlg.exec() == QDialog.Accepted:
        return panel.style()


def test_live():
    import sys 
    app = QApplication(sys.argv)
    ui = XYDataStylePanel()
    ui.show()
    status = app.exec()
    sys.exit(status)


if __name__ == '__main__':
    test_live()
