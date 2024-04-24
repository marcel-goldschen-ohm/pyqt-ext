""" PySide/PyQt expandable/collapsible section.
"""

from qtpy.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QAbstractAnimation
from qtpy.QtWidgets import QWidget, QToolButton, QFrame, QScrollArea, QPushButton, QLineEdit, QSizePolicy, QLayout, QFormLayout, QVBoxLayout, QGridLayout
import qtawesome as qta


class CollapsibleSection(QWidget):
    def __init__(self, parent: QWidget = None, title: str = '', animationDuration: int = 250) -> None:
        """
        References:
            https://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
            # Adapted from PyQt4 version
            https://stackoverflow.com/a/37927256/386398
            # Adapted from c++ version
            https://stackoverflow.com/a/37119983/386398
        """
        QWidget.__init__(self, parent=parent)

        # toggle button
        self.toggleButton = QToolButton()
        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # self.toggleButton.setArrowType(Qt.RightArrow)
        # Use font awesome icons because default arrow icons on MacOS look terrible
        self.toggleButton.setIcon(qta.icon('fa.angle-right'))
        self.toggleButton.setText(str(title))
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        # header line
        self.headerLine = QFrame()
        self.headerLine.setFrameShape(QFrame.HLine)
        self.headerLine.setFrameShadow(QFrame.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # content area
        self.contentArea = QScrollArea()
        self.contentArea.setStyleSheet("QScrollArea { border: none; }")
        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        
        # layout
        self.mainLayout = QGridLayout()
        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        row = 0
        self.mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        row = 1
        self.mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)
        
        # toggle animation
        self.animationDuration = animationDuration
        self.toggleAnimation = QParallelAnimationGroup()
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        self.toggleButton.clicked.connect(self.setIsExpanded)

    def setTitle(self, title: str) -> None:
        self.toggleButton.setText(title)
    
    def setContentLayout(self, contentLayout: QLayout) -> None:
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)

        # update animations
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()

        minimumHeightAnimation = self.toggleAnimation.animationAt(0)
        maximumHeightAnimation = self.toggleAnimation.animationAt(1)
        for anim in [minimumHeightAnimation, maximumHeightAnimation]:
            anim.setDuration(self.animationDuration)
            anim.setStartValue(collapsedHeight)
            anim.setEndValue(collapsedHeight + contentHeight)

        contentAreaMaximumHeightAnimation = self.toggleAnimation.animationAt(2)
        contentAreaMaximumHeightAnimation.setDuration(self.animationDuration)
        contentAreaMaximumHeightAnimation.setStartValue(0)
        contentAreaMaximumHeightAnimation.setEndValue(contentHeight)
    
    def isExpanded(self) -> bool:
        return self.toggleButton.isChecked()
    
    def setIsExpanded(self, expanded: bool) -> None:
        if self.toggleButton.isChecked() != expanded:
            self.toggleButton.setChecked(expanded)
        # arrow_type = Qt.DownArrow if expanded else Qt.RightArrow
        icon = qta.icon('fa.angle-down') if expanded else qta.icon('fa.angle-right')
        direction = QAbstractAnimation.Direction.Forward if expanded else QAbstractAnimation.Direction.Backward
        # toggleButton.setArrowType(arrow_type)
        self.toggleButton.setIcon(icon)
        self.toggleAnimation.setDirection(direction)
        self.toggleAnimation.start()
    
    def expand(self) -> None:
        self.setIsExpanded(True)
    
    def collapse(self) -> None:
        self.setIsExpanded(False)


def test_live():
    from qtpy.QtCore import QTimer
    from qtpy.QtWidgets import QApplication

    app = QApplication()

    ui = QWidget()
    vbox = QVBoxLayout(ui)

    details = CollapsibleSection(title='Details')

    form = QFormLayout()
    form.addRow('Red', QPushButton('Red'))
    form.addRow('Name', QLineEdit('Bob'))

    details.setTitle('Stuff')
    details.setContentLayout(form)

    vbox.addWidget(details)
    ui.show()

    QTimer.singleShot(1000, lambda: details.expand())
    QTimer.singleShot(2000, lambda: details.collapse())

    app.exec()


if __name__ == '__main__':
    test_live()
