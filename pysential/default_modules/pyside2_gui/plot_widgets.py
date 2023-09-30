
from PySide2 import QtGui, QtCore
from PySide2 import QtWidgets
import pyqtgraph as pg
from pyqtgraph import functions
import math
import numpy as np
import logging
logger = logging.getLogger(__name__)

# PyQtGraph options
pg.setConfigOption('useOpenGL', False)
pg.setConfigOption('useWeave', True)
pg.setConfigOption('crashWarning', True)


class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, x, y):
        """x and y are 2D arrays of shape (Nplots, Nsamples)"""
        connect = np.ones(x.shape, dtype=bool)
        # connect[:,-1] = 0 # don't draw the segment between each trace
        self.path = pg.arrayToQPath(x.flatten(), y.flatten(), connect.flatten())
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(pg.mkPen('w'))

    def shape(self): # override because QGraphicsPathItem.shape is too expensive.
        return pg.QtGui.QGraphicsItem.shape(self)

    def boundingRect(self):
        return self.path.boundingRect()


class GraphView(QtWidgets.QWidget):
    """A class used to create a GraphView

    Attributes
    ----------
    plot : pg.PlotWidget
        Main plot widget
    x_min : float
        Minimum on x-axis
    x_max : float
        Maximum on x-axis
    y_min : float
        Minimum on y-axis
    y_max : float
        Maximum on x-axis
    x_range : float
        Total x range
    y_range : float
        Total y range
    x_aspect : float
        x aspect ratio
    y_aspect : float
        y aspect ratio
    x_scroll : ScrollBar
        x-axis scroll area
    y_scroll : ScrollBar
        y-axis scroll area
    x_resize : ResizeBar
        x-axis resize area
    y_resize : ResizeBar
        y-axis resize area
    """
    def __init__(self, parent=None):
        super(GraphView, self).__init__(parent)
        layout = QtWidgets.QGridLayout()

        # self.win = pg.GraphicsWindow(parent=parent)
        # self.win.setBackground('w')
        self.x_units = ''
        self.y_units = ''
        self.plot = pg.PlotWidget(parent=parent)
        self.plot.setBackground('w')
        # self.plot = self.win.addPlot()
        self.plot.setMouseEnabled(False, False)
        self.plot.disableAutoRange()
        self.plot.autoDownsample = True
        # self.plot.clipToView = True

        self.cursors = []
        self.x_min, self.x_max = 0, 0
        self.y_min, self.y_max = 0, 0
        self.x_range, self.y_range = 0, 0
        self.x_aspect, self.y_aspect = 1, 1

        self.x_scroll = ScrollBar(orientation=QtCore.Qt.Horizontal, continuous_updates=True)
        self.x_scroll.connector(self._scroll)
        self.y_scroll = ScrollBar(orientation=QtCore.Qt.Vertical, continuous_updates=True)
        self.y_scroll.connector(self._scroll)

        self.x_resize = ResizeBar(minimum_height=20, orientation='x')
        self.x_resize.connector(self._zoom)
        self.y_resize = ResizeBar(minimum_width=20, orientation='y')
        self.y_resize.connector(self._zoom)

        layout.addWidget(self.y_scroll, 0, 0, 1, 1)
        layout.addWidget(self.x_scroll, 2, 2, 1, 1)
        layout.addWidget(self.y_resize, 0, 1, 1, 1)
        layout.addWidget(self.x_resize, 1, 2, 1, 1)
        layout.addWidget(self.plot, 0, 2, 1, 1)
        # layout.addWidget(self.win, 0, 2, 1, 1)

        self.x_data = []
        self.y_data = []
        self.holding = False
        self.source_path = None

        self.setLayout(layout)
        self.update_view()

    def _zoom(self, fractions, *args, **kwargs):
        x_min_range = self.plot.getAxis('bottom').range[0]
        y_min_range = self.plot.getAxis('left').range[0]
        x_view_range = self.plot.getAxis('bottom').range[1] - self.plot.getAxis('bottom').range[0]
        y_view_range = self.plot.getAxis('left').range[1] - self.plot.getAxis('left').range[0]
        self.plot.setXRange(x_min_range + x_view_range * fractions[0],
                            x_min_range + x_view_range * fractions[1], padding=0)
        self.plot.setYRange(y_min_range + y_view_range * fractions[2],
                            y_min_range + y_view_range * fractions[3], padding=0)

    def _scroll(self, item, fraction, *args, **kwargs):
        if item == self.x_scroll:
            x_min = (self.x_range * (fraction)) + self.x_min
            x_max = self.x_range * self.x_aspect + x_min
            self.plot.setXRange(x_min, x_max, padding=0)
        elif item == self.y_scroll:
            y_min = (self.y_range * (1 - fraction)) + self.y_min
            y_max = self.y_range * self.y_aspect + y_min
            self.plot.setYRange(y_min, y_max, padding=0)

    def _zoom_event(self):
        x_view_range = self.plot.getAxis('bottom').range[1] - self.plot.getAxis('bottom').range[0]
        y_view_range = self.plot.getAxis('left').range[1] - self.plot.getAxis('left').range[0]
        x_aspect = x_view_range / self.x_range
        y_aspect = y_view_range / self.y_range
        if round(x_aspect, 9) != round(self.x_aspect, 9):
            self.x_aspect = x_aspect
            self._update_scrollbars()
            x_fraction = ((self.plot.getAxis('bottom').range[0] - self.x_min) / self.x_range)
            self.x_scroll.setValue(int(x_fraction * (self.x_steps + 1)))
        if round(y_aspect, 9) != round(self.y_aspect, 9):
            self.y_aspect = y_aspect
            self._update_scrollbars()
            y_fraction = 1 - ((self.plot.getAxis('left').range[0] - self.y_min) / self.y_range)
            self.y_scroll.setValue(int(y_fraction * (self.y_steps + 1)))
        # self._update_source_path()

    def _update_scrollbars(self):
        if self.x_aspect == 1:
            self.x_steps = 1
        else:
            self.x_steps = int(10 * math.ceil(1 / self.x_aspect))
        if self.y_aspect == 1:
            self.y_steps = 1
        else:
            self.y_steps = int(10 * math.ceil(1 / self.y_aspect))

        self.x_scroll.set_scroll_steps(self.x_steps)
        self.y_scroll.set_scroll_steps(self.y_steps)


    def mouseDoubleClickEvent(self, e):
        self.plot.setXRange(self.x_min, self.x_max, padding=0)
        self.plot.setYRange(self.y_min, self.y_max, padding=0)

    def update_view(self):
        pass

    def update_zoom(self):
        pass

    def add_chart_axis(self, series_id=-1, align='Bottom', axis_name='', axis_ticks=9):
        pass

    def _make_series(self, series_name='', x_data=None, y_data=None, hex_color="#000000", setUseOpenGL=True):
        pass

    def add_chart_data(self, series_name='', data=None, x_data=None, y_data=None, hex_color="#000000",
                       x_name='', y_name='', x_unit='', y_unit='', symbol=None, log_x=False, log_y=False,
                       x_range=None, y_range=None, setUseOpenGL=True, reset=False, hold=False):
        if reset:
            self.x_data = []
            self.y_data = []
            self.plot.clear()
        if data:
            d = data.data
            x_data = d[1]
            y_data = d[0]

        self.x_data.append(x_data)
        self.y_data.append(y_data)
        self.x_units = x_unit
        self.y_units = y_unit



        if not hold:
            self.plot.setLogMode(x=log_x)
            self.plot.setLogMode(y=log_y)

            if symbol is not None:
                symbolPen = pg.mkPen(color=QtGui.QColor(hex_color), width=0)
                pen = None
            else:
                symbolPen = None
                pen = pg.mkPen(color=QtGui.QColor(hex_color), width=1)
            if len(x_data) == len(y_data):
                self.plot.plot(self.x_data[-1], self.y_data[-1], pen=pen, symbol=symbol, symbolPen=symbolPen, symbolSize=5)
            elif len(x_data) == len(y_data) + 1:
                self.plot.plot(self.x_data[-1], self.y_data[-1], pen=pen, symbol=symbol, stepMode=True)

            self.plot.sigRangeChanged.connect(self._zoom_event)
            self.plot.showGrid(x=True, y=True)

            # self.plot.setBackground('w')

            if not x_range:
                self.x_min, self.x_max = min(x_data), max(x_data)
            elif x_range:
                self.x_min, self.x_max = x_range
            self.x_range = self.x_max - self.x_min
            if not y_range and (self.y_min == self.y_max):
                self.y_min, self.y_max = min(y_data), max(y_data)
            elif y_range:
                self.y_min, self.y_max = y_range
            self.y_range = self.y_max - self.y_min
            self.plot.setLimits(xMin=self.x_min, xMax=self.x_max, yMin=self.y_min, yMax=self.y_max)
            self.plot.setLabel("left", y_name, y_unit)
            self.plot.setLabel("bottom", x_name, x_unit)
            self.plot.setTitle(title=series_name, size="8pt")
            self.plot.setXRange(self.x_min, self.x_max, padding=0)
            self.plot.setYRange(self.y_min, self.y_max, padding=0)


    def _update_source_path(self):
        self.win.removeItem(self.source_path)
        if self.source_path is not None:
            print(self.source_path)
            axX = self.plot.getAxis('bottom')
            axY = self.plot.getAxis('left')
            self.source_path.setPos(axX.range[0] + (axX.range[1] - axX.range[0]) * 0.05,
                                    axY.range[0] + (axY.range[1] - axY.range[0]) * 0.05)
            self.source_path.setPos(-0.5, 0)
            self.win.addItem(self.source_path)

    def add_source(self, file_path):
        text = "From: %s" % file_path
        self.source_path = pg.TextItem(text=text, anchor=(0, 0))
        self._update_source_path()

    def add_cursor(self, angle=90, hex_color="#19891A"):
        pen = pg.mkPen(color=QtGui.QColor(hex_color), width=5)
        # item = pg.InfiniteLine(movable=True, pen=pen, label="Cursor 1", labelOpts={"movable": True})
        # self.plot.plotItem.addItem(item)
        self.cursors.append(InspectorLine(self.plot.getPlotItem(), angle=angle, pen=pen, x_units=self.x_units, y_units=self.y_units))
        self.cursors[-1].attachToPlotItem()
        self.cursors.append(
            InspectorLine(self.plot.getPlotItem(), angle=angle, pen=pen, x_units=self.x_units, y_units=self.y_units))
        self.cursors[-1].link_cursor(self.cursors[-2])
        self.cursors[-1].link_data((self.x_data[-1], self.y_data[-1]))

        self.cursors[-1].attachToPlotItem()
        return self.cursors[-1]


class InspectorLine(pg.InfiniteLine):
    '''
        Adjusted from:
        https://gist.github.com/cpascual/5620f913f83cae4be2a4f50057111e4c
    '''
    def __init__(self, plot_item, angle=90, pen=None, x_units='', y_units=''):
        super(InspectorLine, self).__init__(angle=angle, movable=True, pen=pen)
        self._plot_item = plot_item
        self.x_units = x_units
        self.y_units = y_units
        self._labels = []
        self.sigPositionChanged.connect(self._onMoved)
        self.linked_cursor = None
        self.x_data, self.y_data = None, None

    def link_cursor(self, cursor):
        self.linked_cursor = cursor

    def link_data(self, data):
        self.x_data, self.y_data = data

    def _get_points(self):
        x_px_size, _ = self.getViewBox().viewPixelSize()
        inspector_x = self.value()
        points = []
        # iterate over the existing curves
        for c in self._plot_item.curves:
            # find the index of the closest point of this curve
            adiff = np.abs(c.xData - inspector_x)
            idx = np.argmin(adiff)

            # only add a label if the line touches the symbol
            tolerance = .5 * max(1, c.opts['symbolSize']) * x_px_size
            if adiff[idx] < tolerance:
                points.append((c.xData[idx], c.yData[idx]))
        return points

    def _onMoved(self):
        # x_px_size, _ = self.getViewBox().viewPixelSize()
        # inspector_x = self.value()
        self._removeLabels()
        '''
        points = []
        # iterate over the existing curves
        for c in self._plot_item.curves:
            # find the index of the closest point of this curve
            adiff = np.abs(c.xData - inspector_x)
            idx = np.argmin(adiff)

            # only add a label if the line touches the symbol
            tolerance = .5 * max(1, c.opts['symbolSize']) * x_px_size
            if adiff[idx] < tolerance:
                points.append((c.xData[idx], c.yData[idx]))
        '''
        points = self._get_points()
        self._createLabels(points)

    def _createLabels(self, points):
        for x, y in points:
            if self.linked_cursor == None:
                text = 'x={}, y={}'.format(functions.siFormat(x, suffix=self.x_units), functions.siFormat(y, suffix=self.y_units))
                text_item = pg.TextItem(text=text, color="#2d3c48")
                text_item.setPos(x, y)
            else:
                x2 = self.linked_cursor._get_points()[0][0]
                y_text = np.mean(self.y_data[np.where((self.x_data < max([x2, x])) & (self.x_data > min([x2, x])))[0]])
                text = 'dx={}, dy={}'.format(functions.siFormat(abs(x2-x), suffix=self.x_units),
                                             functions.siFormat(y_text, suffix=self.y_units))
                text_item = pg.TextItem(text=text, color="#2d3c48", fill="#FFF")
                text_item.setPos(x, y+50e-12)
            self.setPos(x)
            self._labels.append(text_item)
            self._plot_item.addItem(text_item)

    def _removeLabels(self):
        # remove existing texts
        for item in self._labels:
            self._plot_item.removeItem(item)
        self._labels = []

    def attachToPlotItem(self):
        self._plot_item.addItem(self, ignoreBounds=True)

    def dettach(self):
        self._removeLabels()
        self._plot_item.removeItem(self)
        # self._plot_item = None


class ScrollBar(QtWidgets.QScrollBar):
    """A class used to create a ScrollBar widget

    Attributes
    ----------
    func : object
        Connector function
    args
        Connector function arguments
    scroll_steps : int
        Number of scroll steps available
    continuous_updates : bool
        Set if need to update continuously

    Methods
    ----------
    set_scroll_steps(scroll_steps)
        Function to set the number of scroll steps
    connector(function, *args, **kwargs)
        Function to connect upon scroll
    """
    def __init__(self, orientation=QtCore.Qt.Horizontal, parent=None, scroll_steps=1, continuous_updates=True):
        super(ScrollBar, self).__init__(orientation, parent=parent)
        self.continuous_updates = continuous_updates
        self.func, self.args, self.kwargs = None, None, None
        self.scroll_steps = scroll_steps
        self.setRange(1, self.scroll_steps)
        self.sliderReleased.connect(self._update_scroll)
        self.valueChanged.connect(self._update_scroll)
        self.setPageStep(3)

    def set_scroll_steps(self, scroll_steps):
        """Function to set the number of scroll steps

        Parameters
        ----------
        scroll_steps : int
            The number of scroll steps
        """
        if scroll_steps == 1:
            self.scroll_steps = scroll_steps
        else:
            self.scroll_steps = scroll_steps + 1
        self.setRange(1, self.scroll_steps)

    def _update_scroll(self, *args, **kwargs):
        if not self.isSliderDown() or self.continuous_updates:
            total_range = self.maximum() - self.minimum()
            try:
                if total_range != 0:
                    fraction = (self.value() - 1) / total_range
                else:
                    fraction = 1
            except ZeroDivisionError as e:
                logger.error(e, exc_info=True)
                fraction = 1
            self.func(self, fraction, self.args, self.kwargs)

    def connector(self, function, *args, **kwargs):
        """Function to connect upon scroll

        Parameters
        ----------
        function : object
            function to call after mouseReleaseEvent
        *args
            Arguments to pass to function
        **kwargs
            Keyword arguments to pass to function

        """
        self.func, self.args, self.kwargs = function, args, kwargs


class ResizeBar(QtWidgets.QWidget):
    """A class used to create a ResizeBar widget

    Attributes
    ----------
    func : object
        Connector function
    args
        Connector function arguments
    orientation : str
        Orientation of the resize bar, accepts arguments "x" or "y"
    minimum_height : float
        Minimum resize height of the ResizeBar
    minimum_width : float
        Minimum resize width of the ResizeBar
    rubberBand : QtWidgets.QRubberBand
        Rubber band on the ResizeBar
    origin
        Event position upon mouse down

    Methods
    ----------
    connector(function, *args, **kwargs)
        Function to connect after mouseReleaseEvent
    mousePressEvent(event)
        Set origin to rubberBand upon mousePressEvent
    mouseMoveEvent(event)
        Update rubberBand upon mouseMoveEvent
    mouseReleaseEvent(event)
        Sent rubberBand information to func upon mouseReleaseEvent
    """
    def __init__(self, parent=None, orientation=None, minimum_height=10, minimum_width=10):
        super(ResizeBar, self).__init__(parent=parent)
        self.func, self.args, self.kwargs = None, None, None
        self.orientation = orientation
        self.minimum_height = minimum_height
        self.minimum_width = minimum_width
        self.setMinimumHeight(self.minimum_height)
        self.setMinimumWidth(self.minimum_width)
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Line, self)
        self.origin = None

    def connector(self, function, *args, **kwargs):
        """Function to connect after mouseReleaseEvent

        Parameters
        ----------
        function : object
            function to call after mouseReleaseEvent
        *args
            Arguments to pass to function
        **kwargs
            Keyword arguments to pass to function

        """
        self.func, self.args, self.kwargs = function, args, kwargs

    def mousePressEvent(self, event):
        """Set origin to rubberBand upon mousePressEvent

        Parameters
        ----------
        event
            Event information
        """
        self.origin = event.pos()
        origin = event.pos()
        self.rubberBand.setGeometry(self.origin.x(), self.origin.y(), -1, -1)
        if self.orientation:
            if self.orientation == 'x':
                self.origin.setY(1)
                origin.setY(self.minimum_height)
            elif self.orientation == 'y':
                self.origin.setX(1)
                origin.setX(self.minimum_width)
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, origin).normalized())
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        """Update rubberBand upon mouseMoveEvent

        Parameters
        ----------
        event
            Event information
        """
        origin = event.pos()
        if self.orientation:
            if self.orientation == 'x':
                origin.setY(self.minimum_height)
            elif self.orientation == 'y':
                origin.setX(self.minimum_width)
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, origin).normalized())

    def mouseReleaseEvent(self, event):
        """Sent rubberBand information to func upon mouseReleaseEvent

        Parameters
        ----------
        event
            Event information
        """
        self.rubberBand.hide()
        x_0 = self.origin.x() / self.width()
        x_1 = event.pos().x() / self.width()
        x_min, x_max = min(x_0, x_1), max(x_0, x_1)
        y_0 = self.origin.y() / self.height()
        y_1 = event.pos().y() / self.height()
        y_min, y_max = min(y_0, y_1), max(y_0, y_1)
        if self.orientation:
            if self.orientation == 'x':
                y_min, y_max = 0, 1
            elif self.orientation == 'y':
                x_min, x_max = 0, 1
        if self.func:
            self.func((x_min, x_max, (1-y_min), (1-y_max)), self.args, self.kwargs)
