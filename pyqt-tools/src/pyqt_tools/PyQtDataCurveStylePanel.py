""" Widget for editing the style of a data curve.
"""

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_tools import ColorButton


class DataCurveStylePanel(QWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.transparent = QColor('transparent')
        self.defaultColor = QColor(0, 114, 189)

        form = QFormLayout(self)

        self.lineStyleComboBox = QComboBox()
        # Qt.PenStyle.NoPen = 0
        # Qt.PenStyle.SolidLine = 1
        # Qt.PenStyle.DashLine = 2
        # Qt.PenStyle.DotLine = 3
        # Qt.PenStyle.DashDotLine = 4
        self.lineStyleComboBox.addItems(['No Line', 'Solid Line', 'Dash Line', 'Dot Line', 'Dash Dot Line'])
        self.lineStyleComboBox.setCurrentIndex(1)
        self.lineStyles = ['none', '-', '--', ':', '-.']
        form.addRow('Line Style', self.lineStyleComboBox)

        self.lineWidthSpinBox = QDoubleSpinBox()
        self.lineWidthSpinBox.setMinimum(0)
        self.lineWidthSpinBox.setValue(1)
        form.addRow('Line Width', self.lineWidthSpinBox)

        self.colorButton = ColorButton(self.defaultColor)
        self.autoColorCheckBox = QCheckBox('Auto')
        self.autoColorCheckBox.stateChanged.connect(lambda isChecked: self.colorButton.setVisible(not isChecked))
        colorLayout = QHBoxLayout()
        colorLayout.setContentsMargins(0, 0, 0, 0)
        colorLayout.setSpacing(5)
        colorLayout.addWidget(self.colorButton)
        colorLayout.addWidget(self.autoColorCheckBox)
        form.addRow('Color', colorLayout)

        self.markerComboBox = QComboBox()
        self.markerComboBox.addItems([
            'None', 'Circle', 'Triangle Down', 'Triangle Up', 'Triangle Right', 'Triangle Left', 'Square', 
            'Pentagon', 'Hexagon', 'Star', 'Plus', 'Prism', 'Cross'])
        self.markerComboBox.setCurrentIndex(0)
        self.markers = [None, 'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'x']
        form.addRow('Marker', self.markerComboBox)

        self.markerSizeSpinBox = QDoubleSpinBox()
        self.markerSizeSpinBox.setMinimum(0)
        self.markerSizeSpinBox.setValue(10)
        form.addRow('Marker Size', self.markerSizeSpinBox)

        self.markerEdgeWidthSpinBox = QDoubleSpinBox()
        self.markerEdgeWidthSpinBox.setMinimum(0)
        self.markerEdgeWidthSpinBox.setValue(1)
        form.addRow('Marker Edge Width', self.markerEdgeWidthSpinBox)

        self.markerEdgeColorButton = ColorButton(self.defaultColor)
        self.autoMarkerEdgeColorCheckBox = QCheckBox('Auto')
        self.autoMarkerEdgeColorCheckBox.stateChanged.connect(lambda isChecked: self.markerEdgeColorButton.setVisible(not isChecked))
        markerEdgeColorLayout = QHBoxLayout()
        markerEdgeColorLayout.setContentsMargins(0, 0, 0, 0)
        markerEdgeColorLayout.setSpacing(5)
        markerEdgeColorLayout.addWidget(self.markerEdgeColorButton)
        markerEdgeColorLayout.addWidget(self.autoMarkerEdgeColorCheckBox)
        form.addRow('Marker Edge Color', markerEdgeColorLayout)

        self.markerFaceColorButton = ColorButton(self.defaultColor)
        self.autoMarkerFaceColorCheckBox = QCheckBox('Auto')
        self.autoMarkerFaceColorCheckBox.stateChanged.connect(lambda isChecked: self.markerFaceColorButton.setVisible(not isChecked))
        markerFaceColorLayout = QHBoxLayout()
        markerFaceColorLayout.setContentsMargins(0, 0, 0, 0)
        markerFaceColorLayout.setSpacing(5)
        markerFaceColorLayout.addWidget(self.markerFaceColorButton)
        markerFaceColorLayout.addWidget(self.autoMarkerFaceColorCheckBox)
        form.addRow('Marker Face Color', markerFaceColorLayout)
    
    def style(self) -> dict:
        style = {}
        style['LineStyle'] = self.lineStyles[self.lineStyleComboBox.currentIndex()]
        style['LineWidth'] = self.lineWidthSpinBox.value()

        if self.autoColorCheckBox.isChecked():
            style['Color'] = 'auto'
        else:
            color = self.colorButton.color()
            style['Color'] = DataCurveStylePanel.qcolor_to_str(color)
        
        style['Marker'] = self.markers[self.markerComboBox.currentIndex()]
        style['MarkerSize'] = self.markerSizeSpinBox.value()
        style['MarkerEdgeWidth'] = self.markerEdgeWidthSpinBox.value()

        if self.autoMarkerEdgeColorCheckBox.isChecked():
            style['MarkerEdgeColor'] = 'auto'
        else:
            markerEdgeColor = self.markerEdgeColorButton.color()
            style['MarkerEdgeColor'] = DataCurveStylePanel.qcolor_to_str(markerEdgeColor)

        if self.autoMarkerFaceColorCheckBox.isChecked():
            style['MarkerFaceColor'] = 'auto'
        else:
            markerFaceColor = self.markerFaceColorButton.color()
            style['MarkerFaceColor'] = DataCurveStylePanel.qcolor_to_str(markerFaceColor)

        return style
    
    def setStyle(self, style: dict):
        lineStyle = style['LineStyle'] if 'LineStyle' in style else '-'
        self.lineStyleComboBox.setCurrentIndex(self.lineStyles.index(lineStyle))

        lineWidth = style['LineWidth'] if 'LineWidth' in style else 1
        self.lineWidthSpinBox.setValue(lineWidth)

        color = style['Color'] if 'Color' in style else 'auto'
        if color == 'auto':
            self.autoColorCheckBox.setChecked(True)
        else:
            color = DataCurveStylePanel.to_qcolor(color)
            self.colorButton.setColor(color)
            self.autoColorCheckBox.setChecked(False)

        marker = style['Marker'] if 'Marker' in style else None
        self.markerComboBox.setCurrentIndex(self.markers.index(marker))

        markerSize = style['MarkerSize'] if 'MarkerSize' in style else 10
        self.markerSizeSpinBox.setValue(markerSize)

        markerEdgeWidth = style['MarkerEdgeWidth'] if 'MarkerEdgeWidth' in style else lineWidth
        self.markerEdgeWidthSpinBox.setValue(markerEdgeWidth)

        markerEdgeColor = style['MarkerEdgeColor'] if 'MarkerEdgeColor' in style else 'auto'
        if markerEdgeColor == 'auto':
            self.autoMarkerEdgeColorCheckBox.setChecked(True)
        else:
            markerEdgeColor = DataCurveStylePanel.to_qcolor(markerEdgeColor)
            self.markerEdgeColorButton.setColor(markerEdgeColor)
            self.autoMarkerEdgeColorCheckBox.setChecked(False)

        markerFaceColor = style['MarkerFaceColor'] if 'MarkerFaceColor' in style else 'auto'
        if markerFaceColor == 'auto':
            self.autoMarkerFaceColorCheckBox.setChecked(True)
        else:
            markerFaceColor = DataCurveStylePanel.to_qcolor(markerFaceColor)
            self.markerFaceColorButton.setColor(markerFaceColor)
            self.autoMarkerFaceColorCheckBox.setChecked(False)
    
    @staticmethod
    def to_qcolor(color: str | tuple[int | float] | list[int | float]) -> QColor:
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
    def qcolor_to_str(color: QColor) -> str:
        return f'({color.redF()}, {color.greenF()}, {color.blueF()}, {color.alphaF()})'
    
    @staticmethod
    def editStyle(style: dict, parent: QWidget = None, title: str = None) -> dict | None:
        panel = DataCurveStylePanel()
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
    ui = DataCurveStylePanel()
    ui.show()
    status = app.exec()
    sys.exit(status)


if __name__ == '__main__':
    test_live()
