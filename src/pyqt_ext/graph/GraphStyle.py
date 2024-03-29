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
    'markeredgewidth': float
    'markeredgecolor': str
    'markerfacecolor': str
    """

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
            if value is not None:
                value = toColorStr(value)
        elif key == 'linestyle':
            if value is None:
                value = 'none'
            elif isinstance(value, int) or isinstance(value, Qt.PenStyle):
                linestyles = ['none', '-', '--', ':', '.-']
                value = linestyles[value]
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
    
    def qcolor(self) -> QColor | None:
        color = self.color()
        if color is not None:
            return toQColor(color)
    
    def lineStyle(self) -> str:
        return self['linestyle']
    
    def setLineStyle(self, value: str | int | Qt.PenStyle | None):
        self['linestyle'] = value
    
    def penStyle(self) -> Qt.PenStyle:
        linestyle = self.lineStyle()
        linestyles = ['none', '-', '--', ':', '.-']
        return Qt.PenStyle(linestyles.index(linestyle))
    
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
    
    def markerEdgeWidth(self) -> float:
        return self['markeredgewidth']
    
    def setMarkerEdgeWidth(self, value: float):
        self['markeredgewidth'] = value
    
    def markerEdgeColor(self) -> str:
        return self['markeredgecolor']
    
    def setMarkerEdgeColor(self, value: ColorType | None):
        self['markeredgecolor'] = value
    
    def markerEdgeQColor(self) -> QColor | None:
        color = self.markerEdgeColor()
        if color is not None:
            return toQColor(color)
    
    def markerFaceColor(self) -> str:
        return self['markerfacecolor']
    
    def setMarkerFaceColor(self, value: ColorType | None):
        self['markerfacecolor'] = value
    
    def markerFaceQColor(self) -> QColor | None:
        color = self.markerFaceColor()
        if color is not None:
            return toQColor(color)


class GraphStylePanel(QWidget):

    def __init__(self, styles: list[str] = None, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        if styles is None:
            styles = ['color', 'linestyle', 'linewidth', 'marker', 'markersize', 'markeredgewidth', 'markeredgecolor', 'markerfacecolor']
        self.styles = [style.lower() for style in styles]

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(10)

        # line styles
        if set(['color', 'linestyle', 'linewidth']).intersection(self.styles):
            self.lineSection = CollapsibleSection(title='Line')
            form = QFormLayout()
            form.setContentsMargins(10, 10, 10, 10)
            form.setSpacing(10)
            if 'color' in self.styles:
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
            if 'linestyle' in self.styles:
                self.lineStyleComboBox = QComboBox()
                self._lineStyles = {
                    'No Line': 'none',
                    'Solid Line': '-',
                    'Dash Line': '--',
                    'Dot Line': ':',
                    'Dash Dot Line': '.-',
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
        
        # marker styles
        if set(['color', 'linestyle', 'linewidth']).intersection(self.styles):
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
            if 'markeredgewidth' in self.styles:
                self.markerEdgeWidthSpinBox = QDoubleSpinBox()
                self.markerEdgeWidthSpinBox.setMinimum(0)
                if hasattr(self, 'lineWidthSpinBox'):
                    markerEdgeWidth = self.lineWidthSpinBox.value()
                else:
                    markerEdgeWidth = 1
                self.markerEdgeWidthSpinBox.setValue(markerEdgeWidth)
                form.addRow('Edge Width', self.markerEdgeWidthSpinBox)
            if 'markeredgecolor' in self.styles:
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
                form.addRow('Edge Color', markerEdgeColorLayout)
            if 'markerfacecolor' in self.styles:
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
                form.addRow('Face Color', markerFaceColorLayout)
            self.markerSection.setContentLayout(form)
            vbox.addWidget(self.markerSection)
        
        vbox.addStretch()
    
    def graphStyle(self) -> GraphStyle:
        graphStyle = GraphStyle()
        for style in self.styles:
            if style == 'color':
                if not self.autoColorCheckBox.isChecked():
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
            elif style == 'markeredgewidth':
                markerEdgeWidth = self.markerEdgeWidthSpinBox.value()
                graphStyle.setMarkerEdgeWidth(markerEdgeWidth)
            elif style == 'markeredgecolor':
                if not self.autoMarkerEdgeColorCheckBox.isChecked():
                    markerEdgeColor = self.markerEdgeColorButton.color()
                    if markerEdgeColor is not None:
                        graphStyle.setMarkerEdgeColor(markerEdgeColor)
            elif style == 'markerfacecolor':
                if not self.autoMarkerFaceColorCheckBox.isChecked():
                    markerFaceColor = self.markerFaceColorButton.color()
                    if markerFaceColor is not None:
                        graphStyle.setMarkerFaceColor(markerFaceColor)
        return graphStyle
    
    def setGraphStyle(self, graphStyle: GraphStyle):
        for style in self.styles:
            if style == 'color':
                try:
                    color = graphStyle.color()
                    self.autoColorCheckBox.setChecked(color is None)
                    if self.autoColorCheckBox.isChecked():
                        self.colorButton.hide()
                    else:
                        self.colorButton.show()
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
            elif style == 'markeredgewidth':
                try:
                    markerEdgeWidth = graphStyle.setMarkerEdgeWidth()
                    self.markerEdgeWidthSpinBox.setValue(markerEdgeWidth)
                except Exception:
                    pass
            elif style == 'markeredgecolor':
                try:
                    markerEdgeColor = graphStyle.markerEdgeColor()
                    self.autoMarkerEdgeColorCheckBox.setChecked(markerEdgeColor is None)
                    if self.autoMarkerEdgeColorCheckBox.isChecked():
                        self.markerEdgeColorButton.hide()
                    else:
                        self.markerEdgeColorButton.show()
                        self.markerEdgeColorButton.setColor(markerEdgeColor)
                except Exception:
                    pass
            elif style == 'markerfacecolor':
                try:
                    markerFaceColor = graphStyle.markerFaceColor()
                    self.autoMarkerFaceColorCheckBox.setChecked(markerFaceColor is None)
                    if self.autoMarkerFaceColorCheckBox.isChecked():
                        self.markerFaceColorButton.hide()
                    else:
                        self.markerFaceColorButton.show()
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
