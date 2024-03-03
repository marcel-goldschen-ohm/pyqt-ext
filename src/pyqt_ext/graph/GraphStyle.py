""" Widget for editing the style of graph data.

Style is stored in hashable dict.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.utils import ColorType, toQColor, toColorStr
from pyqt_ext.widgets import ColorButton


class GraphStyle(dict):
    """ Hashable style dict for graph data.

    'Color': str
    'LineStyle': str in ['none', '-', '--', ':', '-.']
    'LineWidth': float
    'Marker': str in ['none', 'circle', 'triangle down', 'triangle up', 'triangle right', 'triangle left', 'square', 'pentagon', 'hexagon', 'star', 'plus', 'diamond', 'cross']
    'MarkerSize': float
    'MarkerEdgeWidth': float
    'MarkerEdgeColor': str
    'MarkerFaceColor': str

    Note: Above markers are default markers supported by pyqtgraph: ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
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

        # alternate key names
        self._keymap = {
            'c': 'color',
            'ls': 'linestyle',
            'lw': 'linewidth',
            'symbol': 'marker',
            's': 'marker',
            'm': 'marker',
            'ms': 'markersize',
            'mew': 'markeredgewidth',
            'mec': 'markeredgecolor',
            'mfc': 'markerfacecolor',
        }

        # default values
        self._defaults = {
            'linestyle': '-',
            'linewidth': 1,
            'marker': 'none',
            'markersize': 10,
            'markeredgewidth': 1,
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
    
    def color(self) -> str | None:
        return self.get('color', None)
    
    def setColor(self, value: ColorType | None):
        if value is None:
            if 'color' in self:
                del self['color']
            return
        self['color'] = toColorStr(value)
    
    def qcolor(self) -> QColor | None:
        color = self.color()
        if color is not None:
            return toQColor(color)
        return color
    
    def lineStyle(self) -> str:
        return self.get('linestyle', '-')
    
    def setLineStyle(self, value: str | int | Qt.PenStyle | None):
        if value is None:
            value = 'none'
        elif isinstance(value, int):
            value = self._linestyles[value]
        elif isinstance(value, Qt.PenStyle):
            index = self._penstyles.index(value)
            value = self._linestyles[index]
        self['linestyle'] = value
    
    def penStyle(self) -> Qt.PenStyle:
        return Qt.PenStyle(self._linestyles.index(self.lineStyle()))
    
    def lineWidth(self) -> float:
        return self.get('lLinewidth', 1)
    
    def setLineWidth(self, value: float):
        self['linewidth'] = max(0, value)
    
    def marker(self) -> str:
        return self.get('marker', None)
    
    def setMarker(self, value: str | None):
        if value is None:
            if 'marker' in self:
                del self['marker']
            return
        self['marker'] = value
    
    def markerSize(self) -> float:
        return self.get('markersize', 10)
    
    def setMarkerSize(self, value: float):
        self['markersize'] = max(0, value)
    
    def markerEdgeWidth(self) -> float:
        return self.get('markeredgewidth', self.lineWidth())
    
    def setMarkerEdgeWidth(self, value: float):
        self['markeredgewidth'] = max(0, value)
    
    def markerEdgeColor(self) -> str:
        return self.get('markeredgecolor', None)
    
    def setMarkerEdgeColor(self, value: ColorType | None):
        if value is None:
            if 'markeredgecolor' in self:
                del self['markeredgecolor']
            return
        self['markeredgecolor'] = toColorStr(value)
    
    def markerEdgeQColor(self) -> QColor | None:
        color = self.markerEdgeColor()
        if color is not None:
            return toQColor(color)
        return color
    
    def markerFaceColor(self) -> str:
        return self.get('markerfacecolor', None)
    
    def setMarkerFaceColor(self, value: ColorType | None):
        if value is None:
            if 'markerfacecolor' in self:
                del self['markerfacecolor']
            return
        self['markerfacecolor'] = toColorStr(value)
    
    def markerFaceQColor(self) -> QColor | None:
        color = self.markerFaceColor()
        if color is not None:
            return toQColor(color)
        return color


class GraphStylePanel(QWidget):

    def __init__(self, styles: list[str] = None, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        if styles is None:
            styles = ['color', 'linestyle', 'linewidth', 'marker', 'markersize', 'markeredgewidth', 'markeredgecolor', 'markerfacecolor']
        self.styles = styles

        form = QFormLayout(self)

        for style in self.styles:
            if style == 'color':
                self.colorButton = ColorButton()
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
            elif style == 'linestyle':
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
            elif style == 'linewidth':
                self.lineWidthSpinBox = QDoubleSpinBox()
                self.lineWidthSpinBox.setMinimum(0)
                self.lineWidthSpinBox.setValue(1)
                form.addRow('Line Width', self.lineWidthSpinBox)
            elif style == 'marker':
                # pyqtgraph default markers
                # self.markers = ['none', 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
                self.markerComboBox = QComboBox()
                self.markerComboBox.addItems([
                    'None', 'Circle', 'Triangle Down', 'Triangle Up', 'Triangle Right', 'Triangle Left', 'Square', 
                    'Pentagon', 'Hexagon', 'Star', 'Plus', 'Prism', 'Cross'])
                self.markerComboBox.setCurrentIndex(0)
                form.addRow('Marker', self.markerComboBox)
            elif style == 'markersize':
                self.markerSizeSpinBox = QDoubleSpinBox()
                self.markerSizeSpinBox.setMinimum(0)
                self.markerSizeSpinBox.setValue(10)
                form.addRow('Marker Size', self.markerSizeSpinBox)
            elif style == 'markeredgewidth':
                self.markerEdgeWidthSpinBox = QDoubleSpinBox()
                self.markerEdgeWidthSpinBox.setMinimum(0)
                self.markerEdgeWidthSpinBox.setValue(self.lineWidthSpinBox.value())
                form.addRow('Marker Edge Width', self.markerEdgeWidthSpinBox)
            elif style == 'markeredgecolor':
                self.markerEdgeColorButton = ColorButton()
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
            elif style == 'markerfacecolor':
                self.markerFaceColorButton = ColorButton()
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
        graphStyle = GraphStyle()
        for style in self.styles:
            if style == 'color':
                if not self.autoColorCheckBox.isChecked():
                    color = self.colorButton.color()
                    if color is not None:
                        graphStyle['color'] = toColorStr(color)
            elif style == 'linestyle':
                graphStyle['linestyle'] = self.lineStyles[self.lineStyleComboBox.currentIndex()]
            elif style == 'linewidth':
                graphStyle['linewidth'] = self.lineWidthSpinBox.value()
            elif style == 'marker':
                graphStyle['marker'] = self.markerComboBox.currentText().lower()
            elif style == 'markersize':
                graphStyle['markersize'] = self.markerSizeSpinBox.value()
            elif style == 'markeredgewidth':
                graphStyle['markeredgewidth'] = self.markerEdgeWidthSpinBox.value()
            elif style == 'markeredgecolor':
                if not self.autoMarkerEdgeColorCheckBox.isChecked():
                    markeredgecolor = self.markerEdgeColorButton.color()
                    if markeredgecolor is not None:
                        graphStyle['markeredgecolor'] = toColorStr(markeredgecolor)
            elif style == 'markerfacecolor':
                if not self.autoMarkerFaceColorCheckBox.isChecked():
                    markerfacecolor = self.markerFaceColorButton.color()
                    if markerfacecolor is not None:
                        graphStyle['markerfacecolor'] = toColorStr(markerfacecolor)
        return graphStyle
    
    def setGraphStyle(self, graphStyle: GraphStyle):
        for style in self.styles:
            if style == 'color':
                try:
                    color = graphStyle['color']
                    self.autoColorCheckBox.setChecked(color is None)
                    if self.autoColorCheckBox.isChecked():
                        self.colorButton.hide()
                    else:
                        self.colorButton.show()
                        self.colorButton.setColor(color)
                except:
                    pass
            elif style == 'linestyle':
                try:
                    linestyle = graphStyle['linestyle']
                    self.lineStyleComboBox.setCurrentIndex(self.lineStyles.index(linestyle))
                except:
                    pass
            elif style == 'linewidth':
                try:
                    linewidth = graphStyle['linewidth']
                    self.lineWidthSpinBox.setValue(linewidth)
                except:
                    pass
            elif style == 'marker':
                try:
                    marker = graphStyle['marker']
                    self.markerComboBox.setCurrentIndex(self.markers.index(marker))
                except:
                    pass
            elif style == 'markersize':
                try:
                    markersize = graphStyle['markersize']
                    self.markerSizeSpinBox.setValue(markersize)
                except:
                    pass
            elif style == 'markeredgewidth':
                try:
                    markeredgewidth = graphStyle['markeredgewidth']
                    self.markerEdgeWidthSpinBox.setValue(markeredgewidth)
                except:
                    pass
            elif style == 'markeredgecolor':
                try:
                    markeredgecolor = graphStyle['markeredgecolor']
                    self.autoMarkerEdgeColorCheckBox.setChecked(markeredgecolor is None)
                    if self.autoMarkerEdgeColorCheckBox.isChecked():
                        self.markerEdgeColorButton.hide()
                    else:
                        self.markerEdgeColorButton.show()
                        self.markerEdgeColorButton.setColor(markeredgecolor)
                except:
                    pass
            elif style == 'markerfacecolor':
                try:
                    markerfacecolor = graphStyle['markerfacecolor']
                    self.autoMarkerFaceColorCheckBox.setChecked(markerfacecolor is None)
                    if self.autoMarkerFaceColorCheckBox.isChecked():
                        self.markerFaceColorButton.hide()
                    else:
                        self.markerFaceColorButton.show()
                        self.markerFaceColorButton.setColor(markerfacecolor)
                except:
                    pass


def editGraphStyle(graphStyle: GraphStyle, parent: QWidget = None, title: str = None) -> GraphStyle | None:
    panel = GraphStylePanel()
    panel.setGraphStyle(graphStyle)

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
    app = QApplication()
    ui = GraphStylePanel()
    ui.show()
    QTimer.singleShot(1000, lambda: print(editGraphStyle(GraphStyle())))
    app.exec()


if __name__ == '__main__':
    test_live()
