
from PySide2 import QtGui, QtCore
from PySide2 import QtWidgets
from PySide2.QtCharts import QtCharts
from PySide2 import (QtMultimedia, QtMultimediaWidgets)
from functools import partial
import qimage2ndarray
import time

import pyqtgraph as pg

import logging
logger = logging.getLogger(__name__)


class MediaFeedWidget(QtWidgets.QWidget):
    """Media feed for continuous frame update

    Attributes
    ----------
    layout : QtWidgets.QGridLayout
        Layout of the widget
    parent : QtWidgets
        Parent widget

    Methods
    ----------
    resizeEvent(event)
        Function called upon resize, sets new frame size
    set_image(frame, slot=0)
        Set current frame
    """
    def __init__(self, parent=None):
        super(MediaFeedWidget, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout()
        self.parent = parent
        self.image_area = QtWidgets.QLabel()
        self.image_area.setStyleSheet("border: 3px solid blue;")
        self.layout.addWidget(self.image_area, 0, 0, 1, 1)
        self.size = self.image_area.frameSize()
        self.setLayout(self.layout)
        self.allow_resize = True

    def resizeEvent(self, event):
        """Function called upon resize, sets new frame size

        Parameters
        ----------
        event
            Event information
        """
        self.size = self.image_area.frameSize()

    def set_image(self, frame, slot=0):
        """Set current frame

        Parameters
        ----------
        frame : np.array
            Numpy array containing image
        slot : int
            Slot

        Returns
        -------
        bool
        """
        image = qimage2ndarray.array2qimage(frame)
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.image_area.setPixmap(pixmap)
        if self.parent.visibleRegion().isEmpty():
            return False
        else:
            return True


class MediaWidget(QtWidgets.QWidget):
    # TODO: This is not a functional widget currently
    def __init__(self, parent=None):
        super(MediaWidget, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.video_widget = QtMultimediaWidgets.QVideoWidget()
        self.player = QtMultimedia.QMediaPlayer(parent=parent)
        self.playlist = QtMultimedia.QMediaPlaylist(self.player)

        test_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

        self.playlist.addMedia(QtCore.QUrl(test_url))
        self.player.setVideoOutput(self.video_widget)
        self.playlist.setCurrentIndex(1)

        layout.addWidget(self.video_widget, 0, 1, 1, 1)
        self.video_widget.show()
        self.player.play()
        self.setLayout(layout)

        # Code to mark area, remove before release.
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(128, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        # ###


class TreeView(pg.QtGui.QTreeWidget):
    """Make a tree view widget

    Attributes
    ----------
    mdl : QtWidgets.QFileSystemModel
        Tree view model
    parent : QtWidgets
        Parent widget
    """
    def __init__(self, parent=None, function_connect=None):
        super(TreeView, self).__init__(parent)
        self.setHeaderLabels(['Node', 'Label'])
        self.function_connect = function_connect
        self.itemSelectionChanged.connect(self._tree_view_connect)

        '''
        self.setColumnCount(1)
        items = []
        for i in range(10):
            
            items.append(QtWidgets.QTreeWidgetItem(["1", "2"]))
        self.insertTopLevelItems(None, items)
        
        self.mdl = QtWidgets.QFileSystemModel()
        data_folder = QtCore.QDir('./data').path()
        self.mdl.setRootPath(data_folder)
        self.setModel(self.mdl)
        self.setRootIndex(self.mdl.index(data_folder))
        self.doubleClicked.connect(partial(self._tree_view_connect, func=function_connect))
        self.expandAll()
        
        '''
        self.setColumnWidth(0, 300)

    def new_node(self, n, label, marker=None, parent=None):
        if not parent:
            parent = self.invisibleRootItem()
        item = pg.QtGui.QTreeWidgetItem([n, label])
        item.marker = marker
        parent.addChild(item)
        return item

    def add_item(self, n, label, marker=None, parent=None):
        if not parent:
            parent = self.invisibleRootItem()
        item = pg.QtGui.QTreeWidgetItem([n, label])
        item.marker = marker
        parent.addChild(item)

    def _tree_view_connect(self):
        selected = self.selectedItems()
        if len(selected) < 1:
            return
        return [self.function_connect(sel.marker) for sel in selected]


class DatabaseView(QtWidgets.QTabWidget):
    """Make a database view widget

    Attributes
    ----------
    parent : QtWidgets
        Parent widget
    """
    def __init__(self, tables, fields, samples, index=0, parent=None, function_connect=None):
        super(DatabaseView, self).__init__(parent)
        self.parent = parent
        self.func = function_connect
        views = []

        for table, field, sample in zip(tables, fields, samples):
            views.append(QtWidgets.QTableView())
            views[-1].doubleClicked.connect(self._click_sample)
            model = TableModel(sample, [i.replace("_", " ") for i in field])
            views[-1].setModel(model)
            for c, _ in enumerate(sample):
                views[-1].setRowHeight(c, 2)
            self.addTab(views[-1], table)
            views[-1].setSortingEnabled(True)
        self.setCurrentIndex(index)

    def _click_sample(self, e):
        if self.func is not None:
            self.func(self.currentIndex(), e.row())


class TableModel(QtCore.QAbstractTableModel):
    """Make a new table model

    Attributes
    ----------
    header : list
        List containing strings of the header

    Methods
    ----------
    data(index, role)
    rowCount(index)
    columnCount(index)
    headerData(col, orientation, role)
    """
    def __init__(self, data, header):
        super(TableModel, self).__init__()
        self._data = data
        self.header = header

    def data(self, index, role):
        """Get data, don't change this function

        Parameters
        ----------
        index
        role : QtCore.Qt.DisplayRole

        Returns
        -------
        data
        """
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        """Get length of data, don't change this function

        Parameters
        ----------
        index

        Returns
        -------
        int
        """
        return len(self._data)

    def columnCount(self, index):
        """Get number of columns in data, don't change this function

        Parameters
        ----------
        index

        Returns
        -------
        int
        """
        try:
            return len(self._data[0])
        except IndexError as e:
            logger.error(e, exc_info=True)
            return 0

    def headerData(self, col, orientation, role):
        """Get data, don't change this function

        Parameters
        ----------
        col
        orientation
        role

        Returns
        -------
        str
        """

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return col
        return None


class ChartView(QtWidgets.QWidget):
    """Media feed for continuous frame update

    Attributes
    ----------
    base_axis : list
    current_axis : list
    base_x : float
    base_y : float
    base_dx : float
    base_dy : float
    x : float
    y : float
    dx : float
    dy : float
    x_zoom : float
    y_zoom : float
    x_zoom_pos : float
    y_zoom_pos : float
    scroll_steps : int
    max_zoom_factor : float
    chart : QtCharts.QChart
    chart_view : QtCharts.QChartView
    x_scroll : float
    y_scroll : float
    x_scroll_max : float
    y_scroll_max : float

    Methods
    ----------
    mouseDoubleClickEvent(e)
        Reset zoom to max upon mouseDoubleClickEvent
    update_view
        Update the view on the chart
    update_zoom
        Update zoom based on current values
    update_scroll_x
        Update the x-axis scroll
    update_scroll_y
        Update the y-axis scroll
    add_chart_axis(series_id=-1, align='Bottom', axis_name='', axis_ticks=9)
        Add axis to self
    add_chart_data(series_name='', x_data=None, y_data=None, hex_color="#000000", x_name='', y_name='', setUseOpenGL=True)
        Add data to self
    """
    def __init__(self, parent=None):
        super(ChartView, self).__init__(parent)
        layout = QtWidgets.QGridLayout()

        self.base_axis = [0, 1, 0, 1]
        self.current_axis = [0, 1, 0, 1]
        self.base_x, self.base_y, self.base_dx, self.base_dy = 1, 1, 1, 1
        self.x, self.y, self.dx, self.dy = 1, 1, 1, 1

        self.x_zoom = 1
        self.y_zoom = 1
        self.x_zoom_pos = 0.5
        self.y_zoom_pos = 0.5
        self.scroll_steps = 10000
        self.max_zoom_factor = 1000

        self.chart = QtCharts.QChart()
        self.chart_view = QtCharts.QChartView(self.chart)
        self.chart_view.setRubberBand(self.chart_view.RectangleRubberBand)
        self.chart.plotAreaChanged.connect(self.update_view)

        self.chart_view.chart().createDefaultAxes()

        self.x_scroll = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        self.x_scroll.valueChanged.connect(self.update_scroll_x)

        self.y_scroll = QtWidgets.QScrollBar(QtCore.Qt.Vertical)
        self.y_scroll.valueChanged.connect(self.update_scroll_y)

        self.x_scroll_max = 1
        self.y_scroll_max = 1

        layout.addWidget(self.y_scroll, 0, 0, 1, 1)
        layout.addWidget(self.x_scroll, 1, 1, 1, 1)
        layout.addWidget(self.chart_view, 0, 1, 1, 1)

        self.setLayout(layout)
        self.update_view()

    def mouseDoubleClickEvent(self, e):
        """Reset zoom to max upon mouseDoubleClickEvent

        Parameters
        ----------
        e
            Event information
        """
        self.chart.zoomReset()
        self.update_view()

    def update_view(self):
        """Update the view on the chart
        """
        try:
            self.update_zoom()
            self.x_zoom_pos = (((self.dx / 2) + self.x)-self.base_x)/self.base_dx
            self.x_scroll.setRange(1, self.scroll_steps)
            self.x_scroll.setPageStep(int(self.scroll_steps / self.x_zoom))
            self.x_scroll.setValue(int(self.x_zoom_pos * self.scroll_steps))

            self.y_zoom_pos = 1 - ((((self.dy / 2) + self.y) - self.base_y) / self.base_dy)
            self.y_scroll.setRange(1, self.scroll_steps)
            self.y_scroll.setPageStep(int(self.scroll_steps / self.y_zoom))
            self.y_scroll.setValue(int(self.y_zoom_pos * self.scroll_steps))
        except IndexError as e:
            logger.error(e, exc_info=True)

    def update_zoom(self):
        """Update zoom based on current values
        """
        self.chart_view.chart().update()
        y_min = self.chart.axes(QtCore.Qt.Vertical)[0].min()
        y_max = self.chart.axes(QtCore.Qt.Vertical)[0].max()

        x_min = self.chart.axes(QtCore.Qt.Horizontal)[0].min()
        x_max = self.chart.axes(QtCore.Qt.Horizontal)[0].max()
        if not self.chart.isZoomed():
            self.base_x = x_min
            self.base_y = y_min
            self.base_dx = x_max - x_min
            self.base_dy = y_max - y_min
        self.x = x_min
        self.y = y_min
        self.dx = (x_max - self.base_x) - (x_min - self.base_x)
        self.dy = (y_max - self.base_y) - (y_min - self.base_y)
        self.x_zoom = self.base_dx / self.dx
        self.y_zoom = self.base_dy / self.dy

    def update_scroll_x(self):
        """Update the x-axis scroll
        """
        width = max(1, self.x_scroll.pageStep())
        window_width = (width / self.scroll_steps) * self.base_dx
        mean_pos = self.x_scroll.value()
        pos_min = float((mean_pos - (width / 2)) / self.scroll_steps)
        pos_max = float((mean_pos + (width / 2)) / self.scroll_steps)
        min_range = min(self.base_x + self.base_dx - window_width,
                        max(self.base_x, self.base_dx * pos_min + self.base_x))
        max_range = max(self.base_x + window_width,
                        min(self.base_x + self.base_dx, self.base_dx * pos_max + self.base_x))
        self.chart.axes(QtCore.Qt.Horizontal)[0].setRange(min_range, max_range)
        if self.chart.isZoomed():
            self.x_scroll.setHidden(False)
        else:
            self.x_scroll.setHidden(True)

    def update_scroll_y(self):
        """Update the y-axis scroll
        """
        width = max(1, self.y_scroll.pageStep())
        window_width = (width / self.scroll_steps) * self.base_dy
        mean_pos = self.scroll_steps - self.y_scroll.value()
        pos_min = float((mean_pos - (width / 2)) / self.scroll_steps)
        pos_max = float((mean_pos + (width / 2)) / self.scroll_steps)
        pos_min = self.base_dy * pos_min + self.base_y
        pos_max = self.base_dy * pos_max + self.base_y
        min_range = min(self.base_y + self.base_dy - window_width,
                        max(self.base_y, pos_min))
        max_range = max(self.base_y + window_width,
                        min(self.base_y + self.base_dy, pos_max))
        self.chart.axes(QtCore.Qt.Vertical)[0].setRange(min_range, max_range)
        if self.chart.isZoomed():
            self.y_scroll.setHidden(False)
        else:
            self.y_scroll.setHidden(True)

    def add_chart_axis(self, series_id=-1, align='Bottom', axis_name='', axis_ticks=9):
        """Add axis to self

        Parameters
        ----------
        series_id : int
            Index of series to add
        align : str
            Alignment of the axis, supported arguments: "Top", "Bottom", "Left" and "Right"
        axis_name : str
            Name of the axis
        axis_ticks : int
            Axis ticks
        Returns
        -------
        object
        """
        align_dict = {'Left': QtCore.Qt.AlignLeft, 'Bottom': QtCore.Qt.AlignBottom,
                      'Right': QtCore.Qt.AlignRight, 'Top': QtCore.Qt.AlignTop}
        axis = QtCharts.QValueAxis()
        axis.setTickCount(axis_ticks)
        axis.setLabelFormat("%.2f")
        axis.setTitleText(axis_name)
        self.chart_view.chart().series()[series_id].attachAxis(axis)
        self.chart.addAxis(axis, align_dict[align])
        return True

    def _make_series(self, series_name='', x_data=None, y_data=None, hex_color="#000000", setUseOpenGL=True):
        color = QtGui.QColor(hex_color)
        series = QtCharts.QLineSeries()
        series.setName(series_name)
        series.setColor(color)
        if setUseOpenGL:
            series.setUseOpenGL(True)
        for i, j in zip(x_data, y_data):
            series.append(i, j)
        return series

    def add_chart_data(self, series_name='', x_data=None, y_data=None, hex_color="#000000", x_name='', y_name='', setUseOpenGL=True):
        """Add data to self

        Parameters
        ----------
        series_name : str
            Name of the data series
        x_data : np.array
            Numpy array containing x_data
        y_data : np.array
            Numpy array containing y_data
        hex_color : str
            Hexadecimal color of data, default #000000
        x_name : str
            X-axis title
        y_name : str
            Y-axis title
        setUseOpenGL : bool
            Parameter to determine if the engine uses openGL

        Returns
        -------
        object
        """
        if len(x_data) == len(y_data):
            series = self._make_series(series_name=series_name,
                                       x_data=x_data, y_data=y_data,
                                       hex_color=hex_color, setUseOpenGL=setUseOpenGL)
            self.chart.addSeries(series)
            self.chart_view.chart().createDefaultAxes()
            return True
        return False
