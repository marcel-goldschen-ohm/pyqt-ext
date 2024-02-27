# Color utils for PyQt
Utils for working with colors in PyQt.

# Table of contents
- [Install](#install)
- [Quick start example](#quick-start-example)

# Install
Should work with PySide6, PyQt6, or PyQt5.
```shell
pip install PySide6 pyqt-ext
```

# Quick start example
```python
from qtpy.QtGui import QColor
from pyqt_ext.utils import toQColor, toColorStr

# convert a color representation (e.g., str, tuple, list) into a QColor
red: QColor = toQColor('red')
green: QColor = toQColor('(0, 255, 0)')
transparent_green: QColor = toQColor([0, 1, 0, 0.5])

# convert a color representation (e.g., QColor, tuple, list) into a str
toColorStr('red')  # 'red'
toColorStr(green)  # '(0, 255, 0, 255)'
toColorStr([0, 1, 0, 0.5])  # '(0, 255, 0, 128)'
```