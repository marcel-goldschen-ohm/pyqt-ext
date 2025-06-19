""" ViewBox with matlab color scheme and context menu for drawing ROIs and events.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import numpy as np
import pyqtgraph as pg
from pyqt_ext.pyqtgraph_ext import XAxisRegion, YAxisRegion, Graph


class View(pg.ViewBox):
    """ ViewBox with functionality for drawing ROIs.
    """

    sigStartedDrawingItems = Signal()
    sigItemAdded = Signal(QGraphicsObject)  # emits the newly added QGraphicsObject item
    sigFinishedDrawingItems = Signal()

    def __init__(self, *args, **kwargs):
        pg.ViewBox.__init__(self, *args, **kwargs)

        self._lastMousePressPosInAxesCoords = {}  # dict keys are mouse buttons
        self._drawingItemsOfType = None
        self._itemBeingDrawn = None

        # MATLAB color scheme
        self.setBackgroundColor(QColor(255, 255, 255))

        # colormap (MATLAB lines)
        # rows are colors
        self._colormap = [
            (  0, 114, 189),
            (217,  83,  25),
            (237, 177,  32),
            (126,  47, 142),
            (119, 172,  48),
            ( 77, 190, 238),
            (162,  20,  47),
        ]

        # selected color (row) in colormap
        self._colorIndex = 0

        # ROI styles
        self._ROI_pen = pg.mkPen(QColor(237, 135, 131), width=1)
        self._ROI_hoverPen = pg.mkPen(QColor(255, 0, 0), width=2)
        self._ROI_handlePen = self._ROI_pen
        self._ROI_handleHoverPen = self._ROI_hoverPen
        self._ROI_brush = pg.mkBrush(QColor(237, 135, 131, 51))
        self._ROI_hoverBrush = pg.mkBrush(QColor(237, 135, 131, 128))
    
    def colormap(self):
        return self._colormap
    
    def setColormap(self, colormap) -> None:
        self._colormap = colormap
        self._colorIndex = self._colorIndex % len(self._colormap)
    
    def colorAtIndex(self, colorIndex) -> QColor:
        ncolors = len(self._colormap)
        color = self._colormap[colorIndex % ncolors]
        return QColor(*color)
    
    def nextColor(self) -> QColor:
        ncolors = len(self._colormap)
        color = self._colormap[self._colorIndex % ncolors]
        self._colorIndex = (self._colorIndex + 1) % ncolors
        return QColor(*color)
    
    def colorIndex(self) -> int:
        return self._colorIndex
    
    def setColorIndex(self, colorIndex: int) -> None:
        ncolors = len(self._colormap)
        self._colorIndex = colorIndex % ncolors
    
    def mousePressEvent(self, event):
        # store mouse press position in axes coords
        posInAxesCoords = self.mapSceneToView(self.mapToScene(event.pos()))
        self._lastMousePressPosInAxesCoords[event.button()] = posInAxesCoords

        if event.button() == Qt.LeftButton:
            # start drawing a new item?
            newItem = None
            if self._drawingItemsOfType is not None:
                if self._drawingItemsOfType == XAxisRegion:
                    limits = [posInAxesCoords.x(), posInAxesCoords.x()]
                    newItem = XAxisRegion(values=limits, pen=self._ROI_pen, hoverPen=self._ROI_hoverPen, brush=self._ROI_brush, hoverBrush=self._ROI_hoverBrush)
                elif self._drawingItemsOfType == YAxisRegion:
                    limits = [posInAxesCoords.y(), posInAxesCoords.y()]
                    newItem = YAxisRegion(values=limits, pen=self._ROI_pen, hoverPen=self._ROI_hoverPen, brush=self._ROI_brush, hoverBrush=self._ROI_hoverBrush)
                elif self._drawingItemsOfType in [pg.RectROI, pg.EllipseROI, pg.CircleROI, pg.LineSegmentROI]:
                    newItem = self._drawingItemsOfType(pos=posInAxesCoords, size=[0, 0], invertible=True, pen=self._ROI_pen, hoverPen=self._ROI_hoverPen, handlePen=self._ROI_handlePen, handleHoverPen=self._ROI_handleHoverPen)
                elif issubclass(self._drawingItemsOfType, pg.PlotDataItem):
                    if isinstance(self._itemBeingDrawn, pg.PlotDataItem):
                        # add point to existing Graph
                        x, y = self._itemBeingDrawn.getOriginalDataset()
                        x = np.append(x, posInAxesCoords.x())
                        y = np.append(y, posInAxesCoords.y())
                        self._itemBeingDrawn.setData(x, y)
                        event.accept()
                        return
                    else:
                        newItem = Graph(pen=self._ROI_pen, symbol='o', symbolPen=self._ROI_pen, symbolBrush=self._ROI_brush)
                        newItem.setData([posInAxesCoords.x()], [posInAxesCoords.y()])
                if newItem is not None:
                    self._itemBeingDrawn = newItem
                    self.addItem(self._itemBeingDrawn)
                    event.accept()
                    return
        
        # default if event was not handled above
        pg.ViewBox.mousePressEvent(self, event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # finished drawing region/event?
            if  self._itemBeingDrawn is not None:
                if type(self._itemBeingDrawn) in [XAxisRegion, YAxisRegion, pg.RectROI, pg.EllipseROI, pg.CircleROI, pg.LineSegmentROI]:
                    self.sigItemAdded.emit(self._itemBeingDrawn)
                    self._itemBeingDrawn = None
                event.accept()
                return
        
        # default if event was not handled above
        pg.ViewBox.mouseReleaseEvent(self, event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # drawing region?
            if self._itemBeingDrawn is not None:
                startPosInAxesCoords = self._lastMousePressPosInAxesCoords[Qt.LeftButton]
                posInAxesCoords = self.mapSceneToView(self.mapToScene(event.pos()))
                if isinstance(self._itemBeingDrawn, XAxisRegion):
                    limits = sorted([startPosInAxesCoords.x(), posInAxesCoords.x()])
                    self._itemBeingDrawn.setRegion(limits)
                elif isinstance(self._itemBeingDrawn, YAxisRegion):
                    limits = sorted([startPosInAxesCoords.y(), posInAxesCoords.y()])
                    self._itemBeingDrawn.setRegion(limits)
                elif type(self._itemBeingDrawn) in [pg.RectROI, pg.EllipseROI, pg.CircleROI]:
                    self._itemBeingDrawn.setSize(posInAxesCoords - self._itemBeingDrawn.pos())
                elif isinstance(self._itemBeingDrawn, pg.LineSegmentROI):
                    state = self._itemBeingDrawn.getState()
                    state['points'] = [pg.Point(startPosInAxesCoords), pg.Point(posInAxesCoords)]
                    self._itemBeingDrawn.setState(state)
                event.accept()
                return
        
        # default if event was not handled above
        pg.ViewBox.mouseMoveEvent(self, event)
    
    def startDrawingItemsOfType(self, itemType):
        self._itemBeingDrawn = None
        self._drawingItemsOfType = itemType
        self.sigStartedDrawingItems.emit()
    
    def stopDrawingItems(self):
        self._drawingItemsOfType = None
        self._itemBeingDrawn = None
        self.sigFinishedDrawingItems.emit()
    
    def listItemsOfType(self, itemType):
        return [item for item in self.allChildren() if isinstance(item, itemType)]


def test_live():
    import numpy as np
    from pyqt_ext.pyqtgraph_ext import Figure, Graph
    app = QApplication()

    plot = Figure(viewBox=View())
    # !!! MUST get view ref after plot creation, WTF!?
    view = plot.getViewBox()
    line = Graph(y=np.random.randn(1000))
    plot.addItem(line)
    plot.setWindowTitle('pyqtgraph-tools')
    plot.show()

    view.startDrawingItemsOfType(Graph)
    QTimer.singleShot(2500, lambda: view.stopDrawingItems())
    QTimer.singleShot(2600, lambda: view.startDrawingItemsOfType(XAxisRegion))
    QTimer.singleShot(5000, lambda: view.stopDrawingItems())

    app.exec()


if __name__ == '__main__':
    test_live()
