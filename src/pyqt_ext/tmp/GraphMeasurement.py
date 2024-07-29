
from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class GraphMeasurementPanel(QWidget):

    measureTypeChanged = Signal(str)
    requestPreview = Signal()
    requestMeasure = Signal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self._measureTypeCombobox = QComboBox()
        self._measureTypeCombobox.addItems(['Mean', 'Median'])
        self._measureTypeCombobox.insertSeparator(self._measureTypeCombobox.count())
        self._measureTypeCombobox.addItems(['Min', 'Max', 'AbsMax'])
        self._measureTypeCombobox.insertSeparator(self._measureTypeCombobox.count())
        self._measureTypeCombobox.addItems(['Peaks'])
        self._measureTypeCombobox.insertSeparator(self._measureTypeCombobox.count())
        self._measureTypeCombobox.addItems(['Standard Deviation', 'Variance'])
        self._measureTypeCombobox.currentIndexChanged.connect(lambda index: self._onMeasureTypeChanged())

        self._measureWithinSelectedRegionsCheckbox = QCheckBox('Measure within selected regions')
        self._measureWithinSelectedRegionsCheckbox.setChecked(True)
        self._measureWithinSelectedRegionsCheckbox.stateChanged.connect(lambda state: self._preview())

        self._measurePerSelectedRegionCheckbox = QCheckBox('Measure for each selected region')
        self._measurePerSelectedRegionCheckbox.setChecked(True)
        self._measureWithinSelectedRegionsCheckbox.setEnabled(not self._measurePerSelectedRegionCheckbox.isChecked)
        self._measurePerSelectedRegionCheckbox.stateChanged.connect(lambda state: self._measureWithinSelectedRegionsCheckbox.setEnabled(Qt.CheckState(state) == Qt.CheckState.Unchecked))
        self._measurePerSelectedRegionCheckbox.stateChanged.connect(lambda state: self._preview())

        self._resultNameEdit = QLineEdit()

        self._previewCheckbox = QCheckBox('Preview')
        self._previewCheckbox.setChecked(True)
        self._previewCheckbox.stateChanged.connect(lambda state: self._preview())

        self._measureButton = QPushButton('Measure')
        self._measureButton.pressed.connect(self._measure)

        self._peakTypeCombobox = QComboBox()
        self._peakTypeCombobox.addItems(['Min', 'Max'])
        self._peakTypeCombobox.setCurrentText('Max')
        self._peakTypeCombobox.currentIndexChanged.connect(lambda index: self._preview())

        self._peakAvgHalfWidthSpinbox = QSpinBox()
        self._peakAvgHalfWidthSpinbox.setValue(0)
        self._peakAvgHalfWidthSpinbox.valueChanged.connect(lambda value: self._preview())

        self._peakThresholdEdit = QLineEdit('0')
        self._peakThresholdEdit.editingFinished.connect(self._preview)

        self._peakWidthGroup = QGroupBox()
        form = QFormLayout(self._peakWidthGroup)
        form.setContentsMargins(3, 3, 3, 3)
        form.setSpacing(3)
        form.setHorizontalSpacing(5)
        form.addRow('Average +/- samples', self._peakAvgHalfWidthSpinbox)

        self._peakGroup = QGroupBox()
        form = QFormLayout(self._peakGroup)
        form.setContentsMargins(3, 3, 3, 3)
        form.setSpacing(3)
        form.setHorizontalSpacing(5)
        form.addRow('Peak type', self._peakTypeCombobox)
        form.addRow('Peak threshold', self._peakThresholdEdit)

        self._resultNameWidget = QWidget()
        form = QFormLayout(self._resultNameWidget)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(0)
        form.setHorizontalSpacing(5)
        form.addRow('Result name', self._resultNameEdit)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(3, 3, 3, 3)
        vbox.setSpacing(5)
        vbox.addWidget(self._measureTypeCombobox)
        vbox.addWidget(self._peakGroup)
        vbox.addWidget(self._peakWidthGroup)
        vbox.addWidget(self._measureWithinSelectedRegionsCheckbox)
        vbox.addWidget(self._measurePerSelectedRegionCheckbox)
        # vbox.addWidget(self._resultNameWidget)
        vbox.addWidget(self._previewCheckbox)
        vbox.addWidget(self._measureButton)
        vbox.addStretch()
        
        self._onMeasureTypeChanged()
    
    def _onMeasureTypeChanged(self):
        measureType = self._measureTypeCombobox.currentText()
        self._peakGroup.setVisible(measureType == 'Peaks')
        self._peakWidthGroup.setVisible(measureType in ['Min', 'Max', 'AbsMax', 'Peaks'])
        self._resultNameEdit.setPlaceholderText(measureType)
        self.measureTypeChanged.emit(measureType)
        # self._preview()
    
    def _preview(self):
        self.requestPreview.emit()
    
    def _measure(self):
        self.requestMeasure.emit()


def test_live():
    app = QApplication()
    ui = GraphMeasurementPanel()
    ui.setWindowTitle(ui.__class__.__name__)
    ui.show()
    app.exec()


if __name__ == '__main__':
    test_live()