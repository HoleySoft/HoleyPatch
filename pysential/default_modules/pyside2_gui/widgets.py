# -*- coding: utf-8 -*-
# Third party libraries
from PySide2 import QtCore
from PySide2 import (QtMultimedia, QtMultimediaWidgets)
from PySide2 import QtWidgets
from PySide2.QtWidgets import QDialog



import logging
logger = logging.getLogger(__name__)

# Custom libraries
from .cidgets import *
from .plot_widgets import *
from .app_builder import *


def _widget_manager(func):
    def wrapper(parent, x=0, y=0, dx=1, dy=1, *args, **kwargs):
        widget = func(parent, *args, **kwargs)
        parent.layout.addWidget(widget, x, y, dx, dy)
        return widget
    return wrapper


def new_window(parent):
    """Creates a new window attached to parent

    Parameters
    ----------
    parent : object
        Parent of the widget
    """
    widget = QtWidgets.QWidget(parent=parent)
    widget.layout = QtWidgets.QGridLayout()
    return widget


def show_window(win):
    """Shows the window passed as win

    Parameters
    ----------
    win : object
        window object
    """
    win.show()


def _post_function(trigger, arguments=None):
    if arguments:
        trigger(arguments)
    else:
        trigger()


def set_content(parent):
    """Sets the layout of parent to parent

    Parameters
    ----------
    parent : object
        Parent of the widget

    Returns
    -------
    parent
    """
    parent.setLayout(parent.layout)
    return parent


@_widget_manager
def make_label(parent, x=0, y=0, dx=1, dy=1, text=""):
    """Add and return a QtWidgets.QLabel to parent

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y
    text : str
        Text to be displayed on label

    Returns
    -------
    QtWidgets.QLabel
    """
    return QtWidgets.QLabel(text, parent=parent)


@_widget_manager
def make_toolbar(parent, x=0, y=0, dx=1, dy=1):
    """Add and return a QtWidgets.QToolBar

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    QtWidgets.QToolbar
    """
    return QtWidgets.QToolBar("", parent=parent)


def toolbar_add(parent, widget, function, arguments=None, label='', img=''):
    """Adds functions/buttons to QtWidgets.QToolBar, see make_toolbar

    Parameters
    ----------
    widget : object
        Toolbar compatible widget object
    function : object
        Function to call upon click
    arguments
        Arguments to pass to function
    label : str
        Text to display on toolbar button
    img : str
        Image path
    parent : object
        Parent contained to attach the widget
    Returns
    -------
    QtWidgets.QToolBar
    """
    action = QtWidgets.QAction(QtGui.QIcon(img), '', parent)
    action.triggered.connect(partial(_post_function, function, arguments=arguments))
    widget.addAction(action)
    return widget

@_widget_manager
def make_dropdown(parent, x=0, y=0, dx=1, dy=1, on_change=None):
    """Add and return a QtWidgets.QLineEdit

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y
    on_change : object
        Function to call when line edit is changed

    Returns
    -------
    QtWidgets.QLineEdit
    """
    dropdown = QtWidgets.QComboBox()
    if on_change:
        dropdown.textChanged.connect(on_change)
    return dropdown

@_widget_manager
def make_line_edit(parent, x=0, y=0, dx=1, dy=1, on_change=None):
    """Add and return a QtWidgets.QLineEdit

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y
    on_change : object
        Function to call when line edit is changed

    Returns
    -------
    QtWidgets.QLineEdit
    """
    line_edit = QtWidgets.QLineEdit()
    if on_change:
        line_edit.textChanged.connect(on_change)
    return line_edit


def get_line_edit(line_edit):
    """Return the value of QtWidgets.QLineEdit, see make_line_edit

    Parameters
    ----------
    line_edit : QtWidgets.QLineEdit
        Line edit widget, see make_line_edit

    Returns
    -------
    str
    """
    return line_edit.text()


@_widget_manager
def make_button(parent, function_connect=None, arguments=None, text='', border=True, img='', x=0, y=0, dx=1, dy=1):
    """Add a QWidgets.QButton to the main parent

    Parameters
    ----------
    parent : object
        Parent of the widget
    function_connect : object
        Function to connect upon press
    arguments
        Arguments to pass to function defined in function_connect
    text : str
        Text to be displayed over button
    border : bool
        Bool to show or hide border
    img : str
        Image file location
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    QtWidgets.QPushButton
    """
    if img != '':
        widget = QtWidgets.QPushButton(QtGui.QIcon(img), text, parent=parent)
    else:
        widget = QtWidgets.QPushButton(QtGui.QIcon(img), text, parent=parent)
    if not border:
        widget.setFlat(True)
    widget.clicked.connect(partial(_post_function, function_connect, arguments=arguments))
    return widget


@_widget_manager
def media_feed(parent, x=0, y=0, dx=1, dy=1):
    """Return a MediaFeedWidget, see MediaFeedWidget

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    MediaFeedWidget
    """
    return MediaFeedWidget(parent=parent)


@_widget_manager
def media_area(parent, x=0, y=0, dx=1, dy=1):
    """Return a MediaWidget, see MediaWidget

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    MediaWidget
    """
    return MediaWidget(parent=parent)


@_widget_manager
def make_tree_view(parent, function_connect=None, x=0, y=0, dx=1, dy=1):
    """Return a tree_view compatible widget object

    Parameters
    ----------
    parent : object
        Parent of the widget
    function_connect : object
        Function to connect upon click
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    TreeView
    """

    return TreeView(parent=parent, function_connect=function_connect)


@_widget_manager
def make_database_view(parent, database=None, function_connect=None, index=0, x=0, y=0, dx=1, dy=1):
    """Create a database view object

    Parameters
    ----------
    parent : object
        Parent of the widget
    database : ..database.DatabaseManager
        Database object from ..database.DatabaseManager
    index : int
        Tab id
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    DatabaseView
    """
    try:
        tables = database.get_tables()
        print(tables)
        fields = database.get_fields(tables)
        print(fields)
        samples = database.get_samples(table_names=tables)
        return DatabaseView(tables, fields, samples, function_connect=function_connect, index=index, parent=parent)
    except AttributeError as e:
        logger.error(e, exc_info=True)


def get_database_tab(widget):
    """Returns the current tab index in view, see make_database_view

    Parameters
    ----------
    widget : DatabaseView
        database_view widget, see make_database_view
    Returns
    -------
    int
    """
    return widget.currentIndex()


@_widget_manager
def make_chart_view(parent, x=0, y=0, dx=1, dy=1):
    """Return a chart_view compatible widget object, see add_chart_axis, add_chart_data and save_chart

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    GraphView
    """
    return GraphView(parent=parent)


def add_chart_axis(widget, series_id=-1, align='Bottom', axis_name='', axis_ticks=9) -> bool:
    """Add axis to chart_view widget, see make_chart_view

    Parameters
    ----------
    widget : object
        chart_view widget, see make_chart_view
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
    return widget.add_chart_axis(series_id=series_id, align=align, axis_name=axis_name, axis_ticks=axis_ticks)


def add_chart_data(widget, series_name='', data=None, x_data=None, y_data=None, x_unit='', y_unit='', symbol=None,
                   log_x=False, log_y=False,
                   x_range=None, y_range=None, hex_color="#000000", x_name='', y_name='', reset=False, hold=False):
    """Add data to chart_view widget, see make_chart_view

    Parameters
    ----------
    widget : object
        chart_view compatible widget object
    series_name : str
        Name of the data series
    x_data : np.array
        Numpy array containing x_data
    y_data : np.array
        Numpy array containing y_data
    hex_color : str
        Hexadecimal color of data, default #000000
    x_range : tuple
        X-axis start and end range as tuple (start, end)
    y_range : tuple
        Y-axis start and end range as tuple (start, end)
    x_name : str
        X-axis title
    y_name : str
        Y-axis title
    reset : bool
        If true, reset plot data
    Returns
    -------
    object
    """
    return widget.add_chart_data(series_name=series_name, data=data, x_data=x_data, y_data=y_data, hex_color=hex_color,
                                 x_unit=x_unit, y_unit=y_unit, symbol=symbol, log_x=log_x, log_y=log_y,
                                 x_range=x_range, y_range=y_range, x_name=x_name, y_name=y_name, reset=reset, hold=hold)


def save_chart(widget, file_name):
    """Saves chart_view compatible widget object to image, see make_chart_view

    Parameters
    ----------
    widget : object
        Chart view widget, see make_chart_view
    file_name : str
        Location to save chart

    Returns
    -------
    object
    """
    widget.chart_view.grab().save(file_name)


def file_save_dialog(parent, title='', root_dict="...", extensions="") -> str:
    """Opens a file save dialog

    Parameters
    ----------
    parent : object
        Parent of the widget
    title : str
        Title of dialog window
    root_dict : str
        Location of root directory
    extensions : str
        File extensions to display
    """
    title_name = QtCore.QObject.tr(parent, title)
    if extensions:
        extensions = "Images (" + " ".join(extensions) + ")"
    return QtWidgets.QFileDialog.getSaveFileName(parent, title_name, root_dict, extensions)


@_widget_manager
def make_draw_area(parent, x=0, y=0, dx=1, dy=1):
    """Return a draw_area compatible widget object, see add_draw_area_item

    Parameters
    ----------
    parent : object
        Parent of the widget
    x : int
        Root x position
    y :int
        Root y position
    dx :int
        Delta x
    dy :int
        Delta y

    Returns
    -------
    AppBuilder
    """
    return AppBuilder(parent=parent)


def add_draw_area_item(widget):
    """Add draw area to draw_area compatible widget object, see make_draw_area

    Parameters
    ----------
    widget : object
        Parent widget, see make_draw_area

    Returns
    -------
    object
    """
    return widget.add_function_item()
