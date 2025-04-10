""" Plot annotation.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.utils import toColorStr, toQColor
from pyqt_ext.widgets import ColorButton
import warnings
try:
    import pyqtgraph as pg
except ImportError:
    warnings.warn("Requires pyqtgraph")


class Annotation(pg.GraphicsWidget):
    """ Plot annotation.

    - Text label
    - Arrow pointing to a position on the plot
    - 
    """

    def __init__(self, *args, **kwargs):
        pass