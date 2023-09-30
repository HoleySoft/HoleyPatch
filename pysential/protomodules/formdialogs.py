
from . import AbstractWindow


class FormDialogs(AbstractWindow):
    """
    A class used to create a form dialog window for SimpleDatabase


    Attributes
    ----------
    left_grid : tuple
        Coordinates of the left grid
    right_grid : tuple
        Coordinates of the right grid
    grid_space : tuple
        Increment to add to left_grid and right_grid upon update
    field_results : list
        List containing the results when called
    func_connect : object
        Function to send results too

    Methods
    ----------
    add_option(field: tuple)
        Add new option to the form dialog
    connect(func)
        Set func_connect
    run
        This function is called upon start and sets the content of the form dialog
    """
    def __init__(self, obj: object) -> None:
        """
        Parameters
        ----------
        obj : object
            Parent object
        """
        super(FormDialogs, self).__init__(obj)
        self.left_grid = (0, 1, 0, 1)
        self.right_grid = (1, 2, 0, 1)
        self.grid_space = (0, 0, 1, 1)
        self.field_results = []
        self.func_connect = None

    def _update_grid(self):
        self.left_grid = tuple(i + j for i, j in zip(self.left_grid, self.grid_space))
        self.right_grid = tuple(i + j for i, j in zip(self.right_grid, self.grid_space))

    def add_option(self, field: tuple):
        """Add new option to the form dialog

        Parameters
        ----------
        field : tuple
            Tuple containing (field_label: str, field_type: str).
            Supported field types: "Label", "VARCHAR"
        """
        field_label, field_type = field
        result = None
        if field_type == 'Label':
            self.widgets.make_label(text=field_label, grid=self.left_grid)
            self.widgets.make_label(text='', grid=self.right_grid)
        elif field_type == 'VARCHAR':
            self.widgets.make_label(text=field_label, grid=self.left_grid)
            result = self.widgets.make_line_edit(grid=self.right_grid)
        elif field_type == 'Dropdown':
            self.widgets.make_label(text=field_label, grid=self.left_grid)
            result = self.widgets.make_dropdown(grid=self.right_grid)
        self.field_results.append((field_type, result, field_label))
        self._update_grid()
        return result

    def _read_results(self):
        results = {}
        # results = []
        for result in self.field_results:
            field_type, widget, field_label = result
            if field_type == 'Label':
                # results.append(None)
                pass
            elif field_type == 'VARCHAR':
                # results.append(self.get_line_edit(widget))
                results[field_label] = self.get_line_edit(widget)
            elif field_type == "Dropdown":
                # results.append(widget.currentText())
                results[field_label] = widget.currentText()
        if self.func_connect:
            self.func_connect(results)
        self.close()

    def connect(self, func):
        """Set func_connect

        Parameters
        ----------
        func : object
            Function to send results too
        """
        self.func_connect = func

    def close_dialog(self):
        self.close()

    def run(self) -> None:
        """This function is called upon start and sets the content of the form dialog
        """
        self.widgets.make_button(
            function_connect=self._read_results,
            grid=self.left_grid,
            text='Submit'
        )

        self.widgets.make_button(
            function_connect=self.close_dialog,
            grid=self.right_grid,
            text='Cancel'
        )
        self.set_content()
