""" PySide/PyQt 2-D plot.
"""

# from qtpy.QtCore import *
# from qtpy.QtGui import *
# from qtpy.QtWidgets import *
# from qtpy.QtCharts import *
# import numpy as np
# import platform

# # See https://github.com/PlotPyStack/PythonQwt/blob/master/qwt/plot_curve.py#L63
# import os
# try:
#     QT_API = os.environ["QT_API"].lower()
# except:
#     from qtpy import API_NAME
#     QT_API = API_NAME.lower()
# if QT_API == "pyside6":
#     import shiboken6 as shiboken
#     import ctypes


# class Plot(QChartView):
#     """ PySide/PyQt 2-D plot.
#     """
    
#     def __init__(self, *args, **kwargs):
#         QChartView.__init__(self, *args, **kwargs)

#         self._chart: QChart = QChart()
#         # self._chart.createDefaultAxes()
#         self._xaxis: QValueAxis = QValueAxis()
#         self._yaxis: QValueAxis = QValueAxis()
#         self._chart.addAxis(self._xaxis, Qt.AlignmentFlag.AlignBottom)
#         self._chart.addAxis(self._yaxis, Qt.AlignmentFlag.AlignLeft)
#         self.setChart(self._chart)

#         if platform.system() == 'Darwin':
#             # Fix error message due to touch events on MacOS trackpad.
#             # !!! Warning: This may break touch events on a touch screen or mobile device.
#             # See https://bugreports.qt.io/browse/QTBUG-103935
#             self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
    

# def array2d_to_qpolygonf(xdata, ydata) -> QPolygonF:
#     """
#     See https://github.com/PlotPyStack/PythonQwt/blob/master/qwt/plot_curve.py#L63

#     Utility function to convert two 1D-NumPy arrays representing curve data
#     (X-axis, Y-axis data) into a single polyline (QtGui.PolygonF object).
#     This feature is compatible with PyQt5 and PySide6 (requires QtPy).

#     License/copyright: MIT License © Pierre Raybaut 2020-2021.

#     :param numpy.ndarray xdata: 1D-NumPy array
#     :param numpy.ndarray ydata: 1D-NumPy array
#     :return: Polyline
#     :rtype: QtGui.QPolygonF
#     """
#     if not (xdata.size == ydata.size == xdata.shape[0] == ydata.shape[0]):
#         raise ValueError("Arguments must be 1D NumPy arrays with same size")
#     size = xdata.size
#     if QT_API.startswith("pyside"):  # PySide (obviously...)
#         polyline = QPolygonF()
#         polyline.resize(size)
#         address = shiboken.getCppPointer(polyline.data())[0]
#         buffer = (ctypes.c_double * 2 * size).from_address(address)
#     else:  # PyQt
#         if QT_API == "pyqt6":
#             polyline = QPolygonF([QPointF(0, 0)] * size)
#         else:
#             polyline = QPolygonF(size)
#         buffer = polyline.data()
#         buffer.setsize(16 * size)  # 16 bytes per point: 8 bytes per X,Y value (float64)
#     memory = np.frombuffer(buffer, np.float64)
#     memory[: (size - 1) * 2 + 1 : 2] = np.array(xdata, dtype=np.float64, copy=False)
#     memory[1 : (size - 1) * 2 + 2 : 2] = np.array(ydata, dtype=np.float64, copy=False)
#     return polyline


# def test_live():
#     import sys
#     import time

#     app = QApplication(sys.argv)
#     plot = Plot()

#     series = QLineSeries(name='test')
#     plot._chart.addSeries(series)
#     series.attachAxis(plot._xaxis)
#     series.attachAxis(plot._yaxis)
#     series.setUseOpenGL(True)

#     a = time.time()
#     n = int(1e7)
#     x = np.linspace(0, 10, n)
#     y = np.random.rand(n)
#     b = time.time()
#     poly = array2d_to_qpolygonf(x, y)
#     points = QPointFList()
#     points.reserve(n)
#     for i in range(n):
#         points.append(poly[i])
#     c = time.time()
#     series.replace(points)
#     plot.show()
#     d = time.time()
#     print('data creation (sec):', b - a)
#     print('data -> line series (sec):', c - b)
#     print('line plot (sec):', d - c)

#     app.exec()


# def test_live_pyqtgraph():
#     import sys
#     import time
#     from pyqtgraph_ext import PlotWidget, XYDataItem

#     app = QApplication(sys.argv)
#     plot = PlotWidget()

#     a = time.time()
#     n = int(1e7)
#     x = np.linspace(0, 10, n)
#     y = np.random.rand(n)
#     b = time.time()
#     data = XYDataItem(x=x, y=y)
#     plot.addItem(data)
#     plot.show()
#     c = time.time()
#     print('data creation (sec):', b - a)
#     print('line plot (sec):', c - b)

#     app.exec()


# def test_live_vispy():
#     import sys
#     import time
#     from vispy import plot as vp

#     app = QApplication(sys.argv)
#     win = QMainWindow()
#     fig = vp.Fig()
#     win.setCentralWidget(fig.native)

#     a = time.time()
#     n = int(1e7)
#     x = np.linspace(0, 10, n)
#     y = np.random.rand(n)
#     b = time.time()
#     ax = fig[0,0]
#     ax.plot((x, y))
#     win.show()
#     c = time.time()
#     print('data creation (sec):', b - a)
#     print('line plot (sec):', c - b)

#     app.exec()


# if __name__ == '__main__':
#     # test_live()
#     # test_live_pyqtgraph()
#     test_live_vispy()

