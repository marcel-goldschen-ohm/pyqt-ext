""" Widget for editing the style of (x,y) data.

Style is stored in hashable dict.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.color import ColorType, toQColor, toColorStr
from pyqt_ext.widgets import ColorButton


class GraphStyle(dict):
    """ Hashable style dict for (x,y) data.

    'Color': str
    'LineStyle': ['none', '-', '--', ':', '-.']
    'LineWidth': float
    'Marker': ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
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
        self._penstyles = [Qt.PenStyle.NoPen, Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine, Qt.PenStyle.DotLine, Qt.PenStyle.DashDotLine]
        self._linestyles = ['none', '-', '--', ':', '-.']

        # Default markers supported by pyqtgraph.
        # Change these to whatever you want.
        self._markers = ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']

        # Special color names
        self._special_colors: dict[str, QColor] = {
            'none': QColor('transparent'),
            'auto': QColor('transparent'),
        }

        # alternate key names
        self._keymap = {
            'c': 'color',
            'ls': 'linestyle',
            'lw': 'linewidth',
            'symbol': 'marker',
            'm': 'marker',
            'ms': 'markersize',
            'mew': 'markeredgewidth',
            'mec': 'markeredgecolor',
            'mfc': 'markerfacecolor',
        }

        # default values
        self._defaults = {
            'color': 'auto',
            'linestyle': '-',
            'linewidth': 1,
            'marker': 'none',
            'markersize': 10,
            'markeredgewidth': 1,
            'markeredgecolor': 'auto',
            'markerfacecolor': 'auto',
        }
    
    def __getitem__(self, key: str):
        key = key.lower()
        if key in self._keymap:
            key = self._keymap[key]
        if key in self:
            return dict.__getitem__(self, key)
        if key == 'markeredgewidth':
            if 'linewidth' in self:
                return self['linewidth']
        elif key == 'markeredgecolor':
            if 'color' in self:
                return self['color']
        elif key == 'markerfacecolor':
            if 'markeredgecolor' in self:
                return self['markeredgecolor']
            elif 'color' in self:
                return self['color']
        elif key == 'qcolor':
            pass
        if key in self._defaults:
            return self._defaults[key]
    
    def __setitem__(self, key: str, value):
        key = key.lower()
        if key in self._keymap:
            key = self._keymap[key]
        if key.endswith('color'):
            value = toColorStr(value)
        elif key == 'linestyle':
            if value is None:
                value = 'none'
            elif isinstance(value, int):
                value = self._linestyles[value]
            elif isinstance(value, Qt.PenStyle):
                index = self._penstyles.index(value)
                value = self._linestyles[index]
        elif key == 'marker':
            if value is None:
                value = 'none'
        dict.__setitem__(self, key, value)
    
    def __delitem__(self, key: str):
        key = key.lower()
        if key in self._keymap:
            key = self._keymap[key]
        if key in self:
            dict.__delitem__(self, key)
    
    def color(self) -> str:
        return self.get('Color', 'auto')
    
    def setColor(self, value: ColorType):
        self['Color'] = toColorStr(value)
    
    def qcolor(self) -> QColor:
        return toQColor(self.color(), self._special_colors)
    
    def lineStyle(self) -> str:
        return self.get('LineStyle', '-')
    
    def setLineStyle(self, value: str | int | Qt.PenStyle | None):
        if value is None:
            value = 'none'
        elif isinstance(value, int):
            value = self._linestyles[value]
        elif isinstance(value, Qt.PenStyle):
            index = self._penstyles.index(value)
            value = self._linestyles[index]
        self['LineStyle'] = value
    
    def lineQtPenStyle(self) -> Qt.PenStyle:
        return Qt.PenStyle(self._linestyles.index(self.lineStyle()))
    
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
        self['MarkerEdgeColor'] = GraphStyle.toColorStr(value)
    
    def markerEdgeQColor(self) -> QColor:
        return toQColor(self.markerEdgeColor(), self._special_colors)
    
    def markerFaceColor(self) -> str:
        return self.get('MarkerFaceColor', 'auto')
    
    def setMarkerFaceColor(self, value: ColorType):
        self['MarkerFaceColor'] = GraphStyle.toColorStr(value)
    
    def markerFaceQColor(self) -> QColor:
        return toQColor(self.markerFaceColor(), self._special_colors)


class GraphStylePanel(QWidget):

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
    
    def graphStyle(self) -> GraphStyle:
        style = GraphStyle()
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
    
    def setGraphStyle(self, style: GraphStyle):
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
    

def editGraphStyle(style: GraphStyle, parent: QWidget = None, title: str = None) -> GraphStyle | None:
    panel = GraphStylePanel()
    panel.setGraphStyle(style)

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
        return panel.graphStyle()


def test_live():
    import sys 
    app = QApplication(sys.argv)
    ui = GraphStylePanel()
    ui.show()
    status = app.exec()
    sys.exit(status)


if __name__ == '__main__':
    test_live()
