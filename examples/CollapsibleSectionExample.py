from __future__ import annotations
from qtpy.QtWidgets import QApplication, QFormLayout, QPushButton, QLineEdit
from pyqt_ext.widgets import CollapsibleSection


def example():
    # Create the application
    app = QApplication()

    # Create the collapsible section
    details = CollapsibleSection(title='Details')

    # Collapsible content
    form = QFormLayout()
    form.addRow('Red', QPushButton('Red'))
    form.addRow('Name', QLineEdit('Bob'))
    details.setContentLayout(form)

    details.expand()
    details.show()

    # Run the application
    app.exec()


if __name__ == '__main__':
    example()
