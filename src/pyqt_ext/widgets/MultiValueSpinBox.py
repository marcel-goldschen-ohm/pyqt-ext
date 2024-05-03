""" PySide/PyQt multi-value spin box.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import re
import numpy as np


class MultiValueSpinBox(QAbstractSpinBox):
    """ Spinbox allowing multiple values or value ranges.

    - Specify allowed values as a list or numpy array.
    - Select multiple space or comma-separated values or value ranges.
    - Value ranges can be specified as first-last or start:stop[:step].
    """

    indicesChanged = Signal()

    def __init__(self, *args, **kwargs):
        QAbstractSpinBox.__init__(self, *args, **kwargs)

        # possible values to select from
        self._indexed_values: np.ndarray = np.arange(100)

        # indices of selected values in self._indexed_values
        # i.e., selected values are self._indexed_values[self._indices]
        self._indices: np.ndarray[int] = np.array([0], dtype=int)

        # initialize with default values
        self.setIndices(self._indices)

        self.setSizePolicy(QSizePolicy.Expanding, self.sizePolicy().verticalPolicy())

        self.editingFinished.connect(self.onTextEdited)

        self.setToolTip('index/slice (+Shift: page up/down)')

        self.lineEdit().setPlaceholderText(self.textFromValues(self._indexed_values))
    
    def indices(self) -> np.ndarray[int]:
        mask = (0 <= self._indices) & (self._indices < len(self._indexed_values))
        return self._indices[mask]
    
    def setIndices(self, indices: list[int] | np.ndarray[int]):
        # print('set_indices:', indices, 'into', self._indexed_values)
        if not isinstance(indices, np.ndarray):
            indices = np.array(indices, dtype=int)
        elif not np.issubdtype(indices.dtype, np.integer):
            indices = indices.astype(int)
        mask = (0 <= indices) & (indices < len(self._indexed_values))
        if np.any(mask):
            self._indices = indices[mask]
        else:
            # default to first index if input indices are invalid
            self._indices = np.array([0], dtype=int)
        text = self.textFromValues(self.selectedValues())
        self.lineEdit().setText(text)
        self.indicesChanged.emit()
    
    def indexedValues(self) -> np.ndarray:
        return self._indexed_values
    
    def setIndexedValues(self, values: list | np.ndarray):
        if not isinstance(values, np.ndarray):
            dtype = type(values[0])
            values = np.array(values, dtype=dtype)
        self._indexed_values = values
        self.setIndices(self.indices())
        self.lineEdit().setPlaceholderText(self.textFromValues(self._indexed_values))
    
    def selectedValues(self) -> np.ndarray:
        return self._indexed_values[self.indices()]
    
    def setSelectedValues(self, values: list | np.ndarray):
        indices = self.indicesFromValues(values)
        self.setIndices(indices)
    
    def indicesFromValues(self, values: list | np.ndarray, tol: float | None = None) -> np.ndarray[int]:
        if not isinstance(values, np.ndarray):
            values = np.array(values, dtype=self._indexed_values.dtype)
        if np.issubdtype(self._indexed_values.dtype, np.floating):
            indices = np.searchsorted(self._indexed_values, values, side='left')
            for i, index in enumerate(indices):
                if index > 0:
                    # check if previous value is closer
                    if np.abs(values[i] - self._indexed_values[index-1]) < np.abs(values[i] - self._indexed_values[index]):
                        indices[i] = index - 1
            if tol is not None:
                # only accept values within a tolerance, otherwise return all the closest indexed values
                mask = np.abs(values - self._indexed_values[indices]) <= tol
                indices = indices[mask]
        else:
            # exact matches only for non-floating point types
            if np.issubdtype(self._indexed_values.dtype, np.integer):
                values = np.intersect1d(self._indexed_values, values)
                indices = np.searchsorted(self._indexed_values, values)
            else:
                # do not assume values are ordered if not integer or floating point
                indices = []
                for value in values:
                    try:
                        i = np.where(self._indexed_values == value)[0][0]
                        indices.append(i)
                    except:
                        pass
                indices = np.array(indices, dtype=int)
        return indices
    
    def valuesFromText(self, text: str, validate: bool = False) -> list:
        text = text.strip()
        if text == '':
            return np.array([0])
        if text == ':':
            return self._indexed_values
        fields = re.split(r'[,\s]+', text)
        values = []
        dtype = self._indexed_values.dtype.type
        for field in fields:
            try:
                field = field.strip()
                if field == '':
                    continue
                if field == ':':
                    return self._indexed_values
                if ':' in field:
                    # first:last inclusive
                    first, last = [dtype(arg) if len(arg.strip()) else None for arg in field.split(':')]
                    if first is None:
                        start_index: int = 0
                    else:
                        start_index: int = self.indicesFromValues([first])[0]
                    if last is None:
                        stop_index: int = len(self._indexed_values)
                    else:
                        stop_index: int = self.indicesFromValues([last])[0] + 1
                    if stop_index > start_index:
                        values.extend(self._indexed_values[start_index:stop_index].tolist())
                else:
                    value = dtype(field)
                    values.append(value)
            except:
                if validate:
                    raise ValueError(f'Invalid text: {field}')
                else:
                    continue
        values = np.array(values, dtype=dtype)
        return values
    
    def textFromValues(self, values: list | np.ndarray):
        indices = self.indicesFromValues(values)
        index_ranges = []
        for index in indices:
            if (len(index_ranges) == 0) or (index != index_ranges[-1][-1] + 1):
                index_ranges.append([index])
            else:
                index_ranges[-1].append(index)
        texts = []
        for index_range in index_ranges:
            if len(index_range) == 1:
                value = self._indexed_values[index_range[0]]
                if np.issubdtype(self._indexed_values.dtype, np.floating):
                    value_text = f'{value:.6f}'.rstrip('0').rstrip('.')
                else:
                    value_text = str(value)
                texts.append(value_text)
            else:
                first_value = self._indexed_values[index_range[0]]
                last_value = self._indexed_values[index_range[-1]]
                if np.issubdtype(self._indexed_values.dtype, np.floating):
                    first_value_text = f'{first_value:.6f}'.rstrip('0').rstrip('.')
                    last_value_text = f'{last_value:.6f}'.rstrip('0').rstrip('.')
                else:
                    first_value_text = str(first_value)
                    last_value_text = str(last_value)
                texts.append(first_value_text + ':' + last_value_text)
        text = ','.join(texts)
        return text
    
    @Slot()
    def onTextEdited(self):
        text = self.lineEdit().text()
        try:
            values = self.valuesFromText(self.lineEdit().text(), validate=True)
            self.setSelectedValues(values)
        except:
            # do not overwrite text if invalid
            text = self.textFromValues(self.selectedValues())
            self.lineEdit().setText(text)
    
    def stepEnabled(self):
        indices = self.indices()
        min_index = 0
        max_index = len(self._indexed_values) - 1
        if len(indices) == 1:
            if indices[0] == min_index:
                return QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
            if indices[0] == max_index:
                return QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        return QAbstractSpinBox.StepEnabledFlag.StepUpEnabled | QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
    
    def stepBy(self, steps: int):
        indices = self.indices()
        min_index = 0
        max_index = len(self._indexed_values) - 1
        if len(indices) == 0:
            index = min_index if steps >= 0 else max_index
            indices = [index]
        elif len(indices) == 1:
            index = min(max(min_index, indices[0] + steps), max_index)
            indices = [index]
        else:
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ShiftModifier:
                # page up/down
                num_indices = len(indices)
                if steps >= 0:
                    last = min(indices[-1] + num_indices, max_index)
                    first = max(min_index, last - num_indices + 1)
                else:
                    first = max(min_index, indices[0] - num_indices)
                    last = min(first + num_indices - 1, max_index)
                indices = list(range(first, last + 1))
            else:
                # step to end of current selected range 
                index = indices[0] if steps >= 0 else indices[-1]
                indices = [index]
        self.setIndices(indices)
    
    def validate(self, text, pos):
        # try:
        #     self.values_from_text(self.lineEdit().text(), validate=True)
        # except:
        #     return QValidator.Intermediate, text, pos
        return QValidator.Acceptable, text, pos

    
def test_live():
    app = QApplication()

    def print_indices_and_values(spinbox: MultiValueSpinBox):
        print('indices:', spinbox.indices())
        print('selected_values:', spinbox.selectedValues())

    ui = QWidget()
    vbox = QVBoxLayout(ui)

    vbox.addWidget(QLabel('Try selecting multiple space- or comma-separated values.'))
    vbox.addWidget(QLabel('Try selecting value ranges as first-last.'))
    vbox.addStretch()

    spinbox = MultiValueSpinBox()
    spinbox.setIndexedValues(list(range(10)))
    spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
    vbox.addWidget(QLabel('0-9'))
    vbox.addWidget(spinbox)
    vbox.addStretch()

    spinbox = MultiValueSpinBox()
    spinbox.setIndexedValues([5,8,15,20])
    spinbox.setIndices([1,2])
    spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
    vbox.addWidget(QLabel('5,8,15,20'))
    vbox.addWidget(spinbox)
    vbox.addStretch()

    spinbox = MultiValueSpinBox()
    spinbox.setIndexedValues(np.linspace(0,1,11))
    spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
    vbox.addWidget(QLabel('0.0-1.0'))
    vbox.addWidget(spinbox)
    vbox.addStretch()

    spinbox = MultiValueSpinBox()
    spinbox.setIndexedValues(['a','b','c','d','e','f'])
    spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
    vbox.addWidget(QLabel('a-f'))
    vbox.addWidget(spinbox)
    vbox.addStretch()

    spinbox = MultiValueSpinBox()
    spinbox.setIndexedValues(['cat','mouse','dog','house','car','truck'])
    spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
    vbox.addWidget(QLabel('cat, mouse, dog, house, car, truck'))
    vbox.addWidget(spinbox)
    vbox.addStretch()

    ui.show()
    app.exec()


if __name__ == '__main__':
    test_live()
