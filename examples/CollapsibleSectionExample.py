from qtpy.QtWidgets import QApplication, QFormLayout, QPushButton, QLineEdit
from pyqt_ext.widgets import CollapsibleSection

# Create the application
app = QApplication()

# Collapsible content
form = QFormLayout()
form.addRow('Red', QPushButton('Red'))
form.addRow('Name', QLineEdit('Bob'))

# Collapsible section
details = CollapsibleSection(title='Details')
details.setContentLayout(form)
details.expand()
details.show()

# Run the application
app.exec()