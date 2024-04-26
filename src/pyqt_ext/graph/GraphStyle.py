""" Widget for editing the style of graph data.

Style is stored in hashable dict.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.utils import ColorType, toQColor, toColorStr
from pyqt_ext.widgets import ColorButton, CollapsibleSection


class GraphStyle(dict):
    """ Hashable style dict for graph data.

    'color': str
    'linestyle': str
    'linewidth': float
    'marker': str
    'markersize': float
    'markeredgestyle': str
    'markeredgewidth': float
    'markeredgecolor': str
    'markerfacecolor': str
    """

    linestyles = ['none', '-', '--', ':', '-.', '-..']
    penstyles = [Qt.PenStyle.NoPen, Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine, Qt.PenStyle.DotLine, Qt.PenStyle.DashDotLine, Qt.PenStyle.DashDotDotLine]

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        # alternate key names
        self._keymap = {
            'c': 'color',
            'ls': 'linestyle',
            'lw': 'linewidth',
            'symbol': 'marker',
            's': 'marker',
            'm': 'marker',
            'ms': 'markersize',
            'mes': 'markeredgestyle',
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
            'markeredgestyle': '-',
            'markeredgewidth': 1,
        }
    
    
    def __getitem__(self, key: str):
        key = key.lower()
        if key in self._keymap:
            key = self._keymap[key]
        if key in self:
            return dict.__getitem__(self, key)
        # key not found...
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
            if value is not None:
                value = toColorStr(value)
        elif key in ['linestyle', 'markeredgestyle']:
            if value is None:
                value = 'none'
            elif isinstance(value, int):
                value = GraphStyle.linestyles[value]
            elif isinstance(value, Qt.PenStyle):
                value = GraphStyle.linestyles[GraphStyle.penstyles.index(value)]
            elif isinstance(value, str):
                if value == '.-':
                    value = '-.'
                elif value == '..-' or value == '.-.':
                    value = '-..'
        elif key == 'linewidth':
            if value is not None:
                value = max(0, value)
        elif key == 'marker':
            if value is None:
                value = 'none'
        elif key == 'markersize':
            if value is not None:
                value = max(0, value)
        elif key == 'markeredgewidth':
            if value is not None:
                value = max(0, value)
        if value is None:
            del self[key]
            return
        dict.__setitem__(self, key, value)
    
    def __delitem__(self, key: str):
        key = key.lower()
        if key in self._keymap:
            key = self._keymap[key]
        if key in self:
            dict.__delitem__(self, key)
    
    def color(self) -> str | None:
        return self['color']
    
    def setColor(self, value: ColorType | None):
        self['color'] = value
    
    def lineStyle(self) -> str:
        return self['linestyle']
    
    def setLineStyle(self, value: str | int | Qt.PenStyle | None):
        self['linestyle'] = value
    
    def lineWidth(self) -> float:
        return self['linewidth']
    
    def setLineWidth(self, value: float):
        self['linewidth'] = value
    
    def marker(self) -> str:
        return self['marker']
    
    def setMarker(self, value: str | None):
        self['marker'] = value
    
    def markerSize(self) -> float:
        return self['markersize']
    
    def setMarkerSize(self, value: float):
        self['markersize'] = value
    
    def markerEdgeStyle(self) -> str:
        return self['markeredgestyle']
    
    def setMarkerEdgeStyle(self, value: str | int | Qt.PenStyle | None):
        self['markeredgestyle'] = value
    
    def markerEdgeWidth(self) -> float:
        return self['markeredgewidth']
    
    def setMarkerEdgeWidth(self, value: float):
        self['markeredgewidth'] = value
    
    def markerEdgeColor(self) -> str:
        return self['markeredgecolor']
    
    def setMarkerEdgeColor(self, value: ColorType | None):
        self['markeredgecolor'] = value
    
    def markerFaceColor(self) -> str:
        return self['markerfacecolor']
    
    def setMarkerFaceColor(self, value: ColorType | None):
        self['markerfacecolor'] = value


class GraphStylePanel(QWidget):

    def __init__(self, styles: list[str] = None, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        if styles is None:
            styles = ['color', 'linestyle', 'linewidth', 'marker', 'markersize', 'markeredgestyle', 'markeredgewidth', 'markeredgecolor', 'markerfacecolor']
        self.styles = [style.lower() for style in styles]

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(10)

        # line
        if set(['color', 'linestyle', 'linewidth']).intersection(self.styles):
            self.lineSection = CollapsibleSection(title='Line')
            form = QFormLayout()
            form.setContentsMargins(10, 10, 10, 10)
            form.setSpacing(10)
            if 'color' in self.styles:
                self.colorButton = ColorButton()
                form.addRow('Color', self.colorButton)
            if 'linestyle' in self.styles:
                self.lineStyleComboBox = QComboBox()
                self._lineStyles = {
                    'No Line': 'none',
                    'Solid Line': '-',
                    'Dash Line': '--',
                    'Dot Line': ':',
                    'Dash Dot Line': '-.',
                    'Dash Dot Dot Line': '-..',
                }
                self.lineStyleComboBox.addItems(list(self._lineStyles.keys()))
                self.lineStyleComboBox.setCurrentIndex(1)
                form.addRow('Style', self.lineStyleComboBox)
            if 'linewidth' in self.styles:
                self.lineWidthSpinBox = QDoubleSpinBox()
                self.lineWidthSpinBox.setMinimum(0)
                self.lineWidthSpinBox.setValue(1)
                form.addRow('Width', self.lineWidthSpinBox)
            self.lineSection.setContentLayout(form)
            vbox.addWidget(self.lineSection)
        
        # marker
        if set(['marker', 'markersize', 'markeredgestyle', 'markeredgewidth', 'markeredgecolor', 'markerfacecolor']).intersection(self.styles):
            self.markerSection = CollapsibleSection(title='Marker')
            form = QFormLayout()
            form.setContentsMargins(10, 10, 10, 10)
            form.setSpacing(10)
            if 'marker' in self.styles:
                self.markerComboBox = QComboBox()
                # pyqtgraph default markers
                self.markerComboBox.addItems(['None', 'Circle', 'Triangle Down', 'Triangle Up', 'Triangle Right', 'Triangle Left', 'Square', 'Diamond', 'Pentagon', 'Hexagon', 'Star', 'Plus', 'Cross'])
                self.markerComboBox.setCurrentIndex(0)
                form.addRow('Symbol', self.markerComboBox)
            if 'markersize' in self.styles:
                self.markerSizeSpinBox = QDoubleSpinBox()
                self.markerSizeSpinBox.setMinimum(0)
                self.markerSizeSpinBox.setValue(10)
                form.addRow('Size', self.markerSizeSpinBox)
            if 'markeredgestyle' in self.styles:
                self.markerEdgeStyleComboBox = QComboBox()
                self._markerEdgeStyles = {
                    'No Line': 'none',
                    'Solid Line': '-',
                    'Dash Line': '--',
                    'Dot Line': ':',
                    'Dash Dot Line': '-.',
                    'Dash Dot Dot Line': '-..',
                }
                self.markerEdgeStyleComboBox.addItems(list(self._markerEdgeStyles.keys()))
                self.markerEdgeStyleComboBox.setCurrentIndex(1)
                form.addRow('Edge Style', self.markerEdgeStyleComboBox)
            if 'markeredgewidth' in self.styles:
                self.markerEdgeWidthSpinBox = QDoubleSpinBox()
                self.markerEdgeWidthSpinBox.setMinimum(0)
                self.markerEdgeWidthSpinBox.setValue(1)
                form.addRow('Edge Width', self.markerEdgeWidthSpinBox)
            if 'markeredgecolor' in self.styles:
                self.markerEdgeColorButton = ColorButton()
                form.addRow('Edge Color', self.markerEdgeColorButton)
            if 'markerfacecolor' in self.styles:
                self.markerFaceColorButton = ColorButton()
                form.addRow('Face Color', self.markerFaceColorButton)
            self.markerSection.setContentLayout(form)
            vbox.addWidget(self.markerSection)
        
        # expand 1st section
        if vbox.count() > 0:
            vbox.itemAt(0).widget().expand()
        
        vbox.addStretch()
    
    def graphStyle(self) -> GraphStyle:
        graphStyle = GraphStyle()
        for style in self.styles:
            if style == 'color':
                color = self.colorButton.color()
                if color is not None:
                    graphStyle.setColor(color)
            elif style == 'linestyle':
                key = self.lineStyleComboBox.currentText()
                lineStyle = self._lineStyles[key]
                graphStyle.setLineStyle(lineStyle)
            elif style == 'linewidth':
                lineWidth = self.lineWidthSpinBox.value()
                graphStyle.setLineWidth(lineWidth)
            elif style == 'marker':
                marker = self.markerComboBox.currentText().lower()
                graphStyle.setMarker(marker)
            elif style == 'markersize':
                markerSize = self.markerSizeSpinBox.value()
                graphStyle.setMarkerSize(markerSize)
            elif style == 'markeredgestyle':
                key = self.markerEdgeStyleComboBox.currentText()
                markerEdgeStyle = self._markerEdgeStyles[key]
                graphStyle.setMarkerEdgeStyle(markerEdgeStyle)
            elif style == 'markeredgewidth':
                markerEdgeWidth = self.markerEdgeWidthSpinBox.value()
                graphStyle.setMarkerEdgeWidth(markerEdgeWidth)
            elif style == 'markeredgecolor':
                markerEdgeColor = self.markerEdgeColorButton.color()
                if markerEdgeColor is not None:
                    graphStyle.setMarkerEdgeColor(markerEdgeColor)
            elif style == 'markerfacecolor':
                markerFaceColor = self.markerFaceColorButton.color()
                if markerFaceColor is not None:
                    graphStyle.setMarkerFaceColor(markerFaceColor)
        return graphStyle
    
    def setGraphStyle(self, graphStyle: GraphStyle):
        for style in self.styles:
            if style == 'color':
                try:
                    color = graphStyle.color()
                    self.colorButton.setColor(color)
                except Exception:
                    pass
            elif style == 'linestyle':
                try:
                    lineStyle = graphStyle.lineStyle()
                    for key, value in self._lineStyles.items():
                        if value.lower() == lineStyle.lower() or key.lower() == lineStyle.lower():
                            lineStyle = key
                            break
                    self.lineStyleComboBox.setCurrentText(lineStyle)
                except Exception:
                    pass
            elif style == 'linewidth':
                try:
                    lineWidth = graphStyle.lineWidth()
                    self.lineWidthSpinBox.setValue(lineWidth)
                except Exception:
                    pass
            elif style == 'marker':
                try:
                    marker = graphStyle.marker()
                    for i, item in enumerate(self.markerComboBox.items()):
                        if item.text().lower() == marker.lower():
                            self.markerComboBox.setCurrentIndex(i)
                            break
                except Exception:
                    pass
            elif style == 'markersize':
                try:
                    markerSize = graphStyle.markerSize()
                    self.markerSizeSpinBox.setValue(markerSize)
                except Exception:
                    pass
            elif style == 'markeredgestyle':
                try:
                    markerEdgeStyle = graphStyle.markerEdgeStyle()
                    for key, value in self._markerEdgeStyles.items():
                        if value.lower() == markerEdgeStyle.lower() or key.lower() == markerEdgeStyle.lower():
                            markerEdgeStyle = key
                            break
                    self.markerEdgeStyleComboBox.setCurrentText(markerEdgeStyle)
                except Exception:
                    pass
            elif style == 'markeredgewidth':
                try:
                    markerEdgeWidth = graphStyle.setMarkerEdgeWidth()
                    self.markerEdgeWidthSpinBox.setValue(markerEdgeWidth)
                except Exception:
                    pass
            elif style == 'markeredgecolor':
                try:
                    markerEdgeColor = graphStyle.markerEdgeColor()
                    self.markerEdgeColorButton.setColor(markerEdgeColor)
                except Exception:
                    pass
            elif style == 'markerfacecolor':
                try:
                    markerFaceColor = graphStyle.markerFaceColor()
                    self.markerFaceColorButton.setColor(markerFaceColor)
                except Exception:
                    pass


def editGraphStyle(graphStyle: GraphStyle, styles: list[str] = None, parent: QWidget = None, title: str = None) -> GraphStyle | None:
    panel = GraphStylePanel(styles)
    panel.layout().setContentsMargins(0, 0, 0, 0)
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
    # QTimer.singleShot(1000, lambda: print(editGraphStyle(GraphStyle())))
    app.exec()


if __name__ == '__main__':
    test_live()
