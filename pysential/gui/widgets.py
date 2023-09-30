
from .elements import Elements


class Widgets(Elements):
    """A class containing all widgets and elements that connect to the GUI module

    Attributes
    ----------
    parent : object
        Parent object to attach all widgets

    Methods
    ----------
    set_parent(parent)
        Add new root_dir location
    new_window
        Creates a new window attached to parent
    show_window(win)
        Shows the window passed as win
    make_toolbar(grid=None, parent=None, *args, **kwargs) -> object
        Return a toolbar compatible widget object, see toolbar_add
    make_line_edit(grid=None, on_change=None, parent=None) -> object
        Return a line edit compatible widget object, see get_line_edit
    get_line_edit(line_edit) -> str
        Return the state of a line edit widget, see make_line_edit
    toolbar_add(widget, function, arguments=None, label='', img='', parent=None) -> object:
        Returns the updated toolbar compatible widget object, see make_toolbar
    make_tree_view(function_connect=None, grid=None, parent=None) -> object:
        Return a tree_view compatible widget object
    multiple_trees(function_connect=None, grid=None, parent=None)
        Compound widget of make_tree_view
    make_database_view(database=None, grid=None, index=0, parent=None) -> object
        Create a database view object
    get_database_tab(widget) -> int
        Returns the current tab index in view, see make_database_view
    make_chart_view(grid=None, parent=None) -> object
        Return a chart_view compatible widget object, see add_chart_axis, add_chart_data and save_chart
    add_chart_axis(widget, series_id=-1, align='Bottom', axis_name='', axis_ticks=9)
        Add axis to chart_view compatible widget object, see make_chart_view
    add_chart_data(widget, series_name='', x_data=None, y_data=None, hex_color="#000000", x_range=None, y_range=None, x_name='', y_name='') -> object
        Add data to chart_view compatible widget object, see make_chart_view
    save_chart(widget, file_name) -> None
        Saves chart_view compatible widget object to image, see make_chart_view
    file_save_dialog(title='', root_dict="...", extensions="", parent=None)
        Opens a file save dialog
    make_draw_area(grid=None, parent=None)
        Return a draw_area compatible widget object, see add_draw_area_item
    add_draw_area_item(widget)
        Add draw area to draw_area compatible widget object, see make_draw_area
    """

    def __init__(self, obj: object):
        super(Widgets, self).__init__(obj)
        self.parent = None

    def set_parent(self, parent):
        """Sets the parent object to attach widgets too

        Parameters
        ----------
        parent : object
            Parent object
        """
        self.parent = parent

    def new_window(self):
        """Creates a new window attached to parent
        """
        return self.widgets.new_window(self.parent)

    def show_window(self, win):
        """Shows the window passed as win

        Parameters
        ----------
        win : object
            Window object to show
        """
        self.widgets.show_window(win)

    @ staticmethod
    def _get_grid(grid):
        if grid:
            y, y2, x, x2 = grid
            dx = x2 - x
            dy = y2 - y
            return x, y, dx, dy
        else:
            return 0, 0, 1, 1

    def make_toolbar(self, grid=None, parent=None, *args, **kwargs) -> object:
        """Return a toolbar compatible widget object, see toolbar_add

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_toolbar(parent, x=x, y=y, dx=dx, dy=dy)

    def make_label(self, grid=None, text=None, parent=None) -> object:
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_label(parent, x=x, y=y, dx=dx, dy=dy, text=text)

    def make_dropdown(self, grid=None, on_change=None, parent=None) -> object:
        """Return a line edit compatible widget object, see get_line_edit

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        on_change : object
            Function object to send results on change
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_dropdown(parent, x=x, y=y, dx=dx, dy=dy, on_change=on_change)

    def make_line_edit(self, grid=None, on_change=None, parent=None) -> object:
        """Return a line edit compatible widget object, see get_line_edit

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        on_change : object
            Function object to send results on change
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_line_edit(parent, x=x, y=y, dx=dx, dy=dy, on_change=on_change)

    def get_line_edit(self, line_edit) -> str:
        """Return the state of a line edit widget, see make_line_edit

        Parameters
        ----------
        line_edit:
            Line edit compatible widget object
        Returns
        -------
        str
        """

        return self.widgets.get_line_edit(line_edit)

    def toolbar_add(self, widget, function, arguments=None, label='', img='', parent=None) -> object:
        """Returns the updated toolbar compatible widget object, see make_toolbar

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
        object
        """

        if not parent:
            parent = self.parent
        img = self.obj.image_manager.get_image(img)
        return self.widgets.toolbar_add(parent, widget, function, arguments=arguments, label=label, img=img)

    def make_tree_view(self, function_connect=None, grid=None, parent=None) -> object:
        """Return a tree_view compatible widget object

        Parameters
        ----------
        function_connect : object
            Function to call upon click
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_tree_view(parent, function_connect=function_connect, x=x, y=y, dx=dx, dy=dy)

    @ staticmethod
    def _panels(x, y):
        return 1/x, 1/y

    def multiple_trees(self, function_connect=None, grid=None, parent=None):
        """Compound widget of make_tree_view

        Parameters
        ----------
        function_connect : object
            Function to call upon click
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        None
        """
        # Compound widget
        x_panels, y_panels = self._panels(2, 1)
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent

        dx0, dy0 = int(dx*x_panels), int(dy*y_panels)

        if (int(dx0 / x_panels) == dx) and (int(dy0 / y_panels) == dy):
            self.widgets.make_tree_view(parent, function_connect=function_connect,
                                        x=x, y=y, dx=dx0, dy=dy0)
            self.widgets.make_tree_view(parent, function_connect=function_connect,
                                        x=x+dx0, y=y, dx=dx0, dy=dy0)
            return True
        else:
            print("Dimension error")

    def make_database_view(self, database=None, grid=None, index=0, function_connect=None, parent=None) -> object:
        """Create a database view object

        Parameters
        ----------
        database : object
            DatabaseManager object, see .database.DatabaseManager
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        index : int
            Index of the tab to be displayed
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_database_view(parent, database=database, function_connect=function_connect, x=x, y=y, dx=dx, dy=dy, index=index)

    def get_database_tab(self, widget) -> int:
        """Returns the current tab index in view, see make_database_view

        Parameters
        ----------
        widget : object
            database_view compatible widget object
        Returns
        -------
        int
        """

        return self.widgets.get_database_tab(widget)

    def make_chart_view(self, grid=None, parent=None) -> object:
        """Return a chart_view compatible widget object
        see add_chart_axis, add_chart_data and save_chart

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_chart_view(parent, x=x, y=y, dx=dx, dy=dy)

    def add_chart_axis(self, widget, series_id=-1, align='Bottom', axis_name='', axis_ticks=9) -> object:
        """Add axis to chart_view compatible widget object, see make_chart_view

        Parameters
        ----------
        widget : object
            chart_view compatible widget object
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
        return self.widgets.add_chart_axis(widget, series_id=series_id, align=align,
                                           axis_name=axis_name, axis_ticks=axis_ticks)

    def add_chart_data(self, widget, series_name='', data=None, x_data=None, y_data=None, hex_color="#000000", log_x=False, log_y=False,
                       x_range=None, y_range=None, x_name='', y_name='', x_unit='', y_unit='', reset=False, symbol=None,
                       hold=False) -> object:
        """Add data to chart_view compatible widget object, see make_chart_view

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
            Y-axis start and end range as tuple (start, end
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
        return self.widgets.add_chart_data(widget, series_name=series_name, data=data, x_data=x_data, y_data=y_data,
                                           hex_color=hex_color, x_range=x_range, y_range=y_range,
                                           x_unit=x_unit, y_unit=y_unit, symbol=symbol, log_x=log_x, log_y=log_y,
                                           x_name=x_name, y_name=y_name, reset=reset, hold=hold
                                           )

    def save_chart(self, widget, file_name) -> None:
        """Saves chart_view compatible widget object to image, see make_chart_view

        Parameters
        ----------
        widget : object
            chart_view compatible widget object
        file_name : str
            Output file location
        """
        return self.widgets.save_chart(widget, file_name)

    def file_save_dialog(self, title='', root_dict="...", extensions="", parent=None):
        """Opens a file save dialog

        Parameters
        ----------
        title : str
            Title of the save dialog
        root_dict : str
            Root directory
        extensions : str
            Supported extensions
        parent : object
            Parent object to attach widget too
        Returns
        -------
        object
        """

        if not parent:
            parent = self.parent
        return self.widgets.file_save_dialog(parent, title=title, root_dict=root_dict, extensions=extensions)

    def make_draw_area(self, grid=None, parent=None):
        """Return a draw_area compatible widget object, see add_draw_area_item

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """

        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_draw_area(parent, x=x, y=y, dx=dx, dy=dy)

    def add_draw_area_item(self, widget):
        """Add draw area to draw_area compatible widget object, see make_draw_area

        Parameters
        ----------
        widget : object
            draw_area compatible widget object
        Returns
        -------
        object
        """
        return self.widgets.add_draw_area_item(widget)
