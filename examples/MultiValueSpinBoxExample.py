from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCheckBox
from pyqt_ext.widgets import MultiValueSpinBox
import numpy as np

# Create the application
app = QApplication()

# Create a panel of multi-value spinboxes
ui = QWidget()
vbox = QVBoxLayout(ui)
vbox.addWidget(QLabel('Try selecting multiple space- or comma-separated values.'))
vbox.addWidget(QLabel('Try selecting value ranges as first:last.'))
vbox.addWidget(QLabel('Selected values (and their indices) will be printed.'))
vbox.addWidget(QLabel('With multiple values selected, try stepping with Shift pressed.'))
cbox = QCheckBox('Show value ranges when possible')
cbox.setChecked(True)
cbox.setToolTip('Change this and see how contiguous selected values are displayed.')
vbox.addWidget(cbox)
vbox.addStretch()

# Callback to print the selected indices and values
def print_indices_and_values(spinbox: MultiValueSpinBox):
    print('indices:', spinbox.indices())
    print('selected_values:', spinbox.selectedValues())

# Create a few multi-value spinboxes and insert them into the panel
spinboxes = []

spinbox = MultiValueSpinBox()
spinbox.setIndexedValues(list(range(10)))
spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
spinboxes.append(spinbox)
vbox.addWidget(QLabel('0,1,2,3,4,5,6,7,8,9'))
vbox.addWidget(spinbox)
vbox.addStretch()

spinbox = MultiValueSpinBox()
spinbox.setIndexedValues([5,8,15,20])
spinbox.setIndices([1,2])
spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
spinboxes.append(spinbox)
vbox.addWidget(QLabel('5,8,15,20'))
vbox.addWidget(spinbox)
vbox.addStretch()

spinbox = MultiValueSpinBox()
spinbox.setIndexedValues(np.linspace(0,1,11))
spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
spinboxes.append(spinbox)
vbox.addWidget(QLabel('0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1'))
vbox.addWidget(spinbox)
vbox.addStretch()

spinbox = MultiValueSpinBox()
spinbox.setIndexedValues(['a','b','c','d','e','f'])
spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
spinboxes.append(spinbox)
vbox.addWidget(QLabel('a,b,c,d,e,f'))
vbox.addWidget(spinbox)
vbox.addStretch()

spinbox = MultiValueSpinBox()
spinbox.setIndexedValues(['cat','mouse','dog','house','car','truck'])
spinbox.indicesChanged.connect(lambda obj=spinbox: print_indices_and_values(obj))
spinboxes.append(spinbox)
vbox.addWidget(QLabel('cat, mouse, dog, house, car, truck'))
vbox.addWidget(spinbox)
vbox.addStretch()

# Update spinbox behavior to reflect panel settings
for spinbox in spinboxes:
    spinbox.setDisplayValueRangesWhenPossible(cbox.isChecked())

# Callback to update spinbox behavior based on panel checkbox
def on_cbox_changed(checked):
    for spinbox in spinboxes:
        spinbox.setDisplayValueRangesWhenPossible(checked)

cbox.stateChanged.connect(on_cbox_changed)

# Run the application
ui.show()
app.exec()