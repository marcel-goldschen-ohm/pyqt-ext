""" PlotDataItem with custom context menu and style dialog.
"""

from __future__ import annotations
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from pyqt_ext.utils import toQColor
from pyqt_ext.widgets import TableWidgetWithCopyPaste
import pyqtgraph as pg
from pyqt_ext.pyqtgraph_ext import GraphStyle, editGraphStyle


class Graph(pg.PlotDataItem):
    """ PlotDataItem with custom context menu and style dialog. """

    sigNameChanged = Signal(str)

    def __init__(self, *args, **kwargs):
        # default style is first MATLAB line color
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(QColor(0, 114, 189), width=1)
        if 'symbolPen' not in kwargs:
            kwargs['symbolPen'] = pg.mkPen(QColor(0, 114, 189), width=1)
        if 'symbolBrush' not in kwargs:
            kwargs['symbolBrush'] = pg.mkBrush(QColor(0, 114, 189, 0))
        if 'symbol' not in kwargs:
            kwargs['symbol'] = None
        pg.PlotDataItem.__init__(self, *args, **kwargs)

        self.setZValue(1)

        self.contextMenu = QMenu()
        # self.contextMenu.addAction('Rename')
        # self.contextMenu.addSeparator()
        self.contextMenu.addAction('Data table', self.dataDialog)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction('Style', self.styleDialog)
        # self.contextMenu.addSeparator()
        # self.contextMenu.addAction('Hide', lambda: self.setVisible(False))
        # self.contextMenu.addSeparator()
        # self.contextMenu.addAction('Delete', lambda: self.getViewBox().deleteItem(self))
    
    def hasCurve(self):
        pen = pg.mkPen(self.opts['pen'])
        return pen.style() != Qt.PenStyle.NoPen
    
    def hasSymbol(self):
        return 'symbol' in self.opts and self.opts['symbol'] is not None
    
    def shape(self) -> QPainterPath:
        if self.hasCurve():
            return self.curve.shape()
        elif self.hasSymbol():
            return self.scatter.shape()

    def boundingRect(self):
        return self.shape().boundingRect()
    
    def mouseClickEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.hasCurve():
                if self.curve.mouseShape().contains(event.pos()):
                    if self.raiseContextMenu(event):
                        event.accept()
                        return
            if self.hasSymbol():
                if len(self.scatter.pointsAt(event.pos())) > 0:
                    if self.raiseContextMenu(event):
                        event.accept()
                        return
    
    def raiseContextMenu(self, event):
        menu = self.getContextMenus(event)
        pos = event.screenPos()
        menu.popup(QPoint(int(pos.x()), int(pos.y())))
        return True
    
    def getContextMenus(self, event=None):
        name = self.name()
        if name is None:
            name = self.__class__.__name__
        self.contextMenu.setTitle(name)

        self.menu = QMenu()
        self.menu.addMenu(self.contextMenu)

        # Let the scene add on to the end of our context menu (this is optional)
        self.menu.addSection('View')
        self.menu = self.scene().addParentContextMenus(self, self.menu, event)
        return self.menu
    
    def name(self):
        return self.opts.get('Name', None)
    
    def setName(self, name):
        if name is None:
            del self.opts['Name']
        else:
            self.opts['Name'] = name
        self.sigNameChanged.emit(self.name())
    
    def graphStyle(self) -> GraphStyle:
        style = GraphStyle()

        pen = pg.mkPen(self.opts['pen'])
        symbolPen = pg.mkPen(self.opts['symbolPen'])
        symbolBrush = pg.mkBrush(self.opts['symbolBrush'])

        style['color'] = pen.color()
        style['linestyle'] = pen.style()
        style['linewidth'] = pen.widthF()
        style['marker'] = self.opts.get('symbol', None)
        style['markersize'] = self.opts.get('symbolSize', 10)
        style['markeredgestyle'] = symbolPen.style()
        style['markeredgewidth'] = symbolPen.widthF()
        if symbolPen.color() != pen.color():
            style['markeredgecolor'] = symbolPen.color()
        if symbolBrush.color() != symbolPen.color():
            style['markerfacecolor'] = symbolBrush.color()

        return style
    
    def setGraphStyle(self, style: GraphStyle, colorIndex: int | None = None) -> int | None:
        # color
        color = style['color']
        if color is None:
            if colorIndex is not None:
                try:
                    axes = self.getViewBox()
                    colormap = axes.colormap()
                    color = colormap[colorIndex % len(colormap)]
                    color = toQColor(color)
                    colorIndex += 1
                except:
                    oldStyle = self.graphStyle()
                    color = toQColor(oldStyle['color'])
            else:
                oldStyle = self.graphStyle()
                color = toQColor(oldStyle['color'])
        else:
            color = toQColor(color)

        # line
        lineStyle: str = style['linestyle']
        linePenStyle: Qt.PenStyle = GraphStyle.penStyles[GraphStyle.lineStyles.index(lineStyle)]
        lineWidth = style['linewidth']
        linePen = pg.mkPen(color=color, width=lineWidth, style=linePenStyle)
        self.setPen(linePen)

        # marker
        marker = style['marker']
        if isinstance(marker, str) and marker.lower() == 'none':
            marker = None
        marker_labels = list(GraphStyle.pyqtgraphMarkers.keys())
        marker_keys = list(GraphStyle.pyqtgraphMarkers.values())
        if marker in marker_labels:
            marker = marker_keys[marker_labels.index(marker)]
        self.setSymbol(marker)
        
        markerSize = style['markersize']
        self.setSymbolSize(markerSize)

        markerEdgeStyle = style['markeredgestyle']
        markerEdgePenStyle: Qt.PenStyle = GraphStyle.penStyles[GraphStyle.lineStyles.index(markerEdgeStyle)]
        markerEdgeWidth = style['markeredgewidth']
        markerEdgeColor = style['markeredgecolor']
        if markerEdgeColor is None:
            markerEdgeColor = color
        else:
            markerEdgeColor = toQColor(markerEdgeColor)
        symbolPen = pg.mkPen(color=markerEdgeColor, width=markerEdgeWidth, style=markerEdgePenStyle)
        self.setSymbolPen(symbolPen)

        markerFaceColor = style['markerfacecolor']
        if markerFaceColor is None:
            markerFaceColor = markerEdgeColor
        else:
            markerFaceColor = toQColor(markerFaceColor)
        self.setSymbolBrush(markerFaceColor)
        
        return colorIndex
    
    def styleDialog(self):
        name = self.name()
        if name is None:
            name = self.__class__.__name__
        old_style: GraphStyle = self.graphStyle()
        new_style: GraphStyle | None = editGraphStyle(old_style, parent = self.getViewBox().getViewWidget(), title = name)
        if new_style is None:
            return
        self.setGraphStyle(new_style)
    
    def dataDialog(self):
        dlg = QDialog()
        dlg.setWindowTitle(self.name())
        vbox = QVBoxLayout(dlg)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        
        xdata, ydata = self.getOriginalDataset()
        n_rows = len(ydata)
        n_cols = 2
        table = TableWidgetWithCopyPaste(n_rows, n_cols)
        for row in range(n_rows):
            table.setItem(row, 0, QTableWidgetItem(str(xdata[row])))
            table.setItem(row, 1, QTableWidgetItem(str(ydata[row])))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        xlabel = getattr(self, '_xlabel', None)
        xunits = getattr(self, '_xunits', None)
        ylabel = getattr(self, '_ylabel', None)
        yunits = getattr(self, '_yunits', None)
        
        view: pg.ViewBox = self.getViewBox()
        plot: pg.PlotItem = view.parentWidget()

        if (xlabel is None) or (xunits is None):
            # try and get label and units from plot axis
            xaxis = plot.getAxis('bottom')
            if xlabel is None:
                xlabel = xaxis.labelText
            if not xlabel:
                # check linked views for valid axis label
                linked_views = view.getState()['linkedViews'][0]
                if linked_views is not None:
                    for linked_view in linked_views:
                        linked_plot: pg.PlotItem = linked_view.parentWidget()
                        linked_xaxis = linked_plot.getAxis('bottom')
                        if linked_xaxis.labelText:
                            xaxis = linked_xaxis
                            xlabel = xaxis.labelText
                            break
            if xunits is None:
                xunits = xaxis.labelUnits
        if xunits:
            xlabel += f' ({xunits})'
        
        if (ylabel is None) or (yunits is None):
            # try and get label and units from plot axis
            yaxis = plot.getAxis('left')
            if ylabel is None:
                ylabel = yaxis.labelText
            if not ylabel:
                # check linked views for valid axis label
                linked_views = view.getState()['linkedViews'][1]
                if linked_views is not None:
                    for linked_view in linked_views:
                        linked_plot: pg.PlotItem = linked_view.parentWidget()
                        linked_yaxis = linked_plot.getAxis('left')
                        if linked_yaxis.labelText:
                            yaxis = linked_yaxis
                            ylabel = yaxis.labelText
                            break
            if yunits is None:
                yunits = yaxis.labelUnits
        if yunits:
            ylabel += f' ({yunits})'
        
        table.setHorizontalHeaderLabels([xlabel, ylabel])
        for col in range(n_cols):
            table.resizeColumnToContents(col)
        table.resizeRowsToContents()
        vbox.addWidget(table)
        dlg.exec()
