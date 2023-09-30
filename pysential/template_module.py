# importing the required packages
from pysential.protomodules import (AbstractModule, AbstractDatabase)
from pysential.default_modules import excel_database
import numpy as np


class TestModule(AbstractModule):
    def __init__(self, obj: object) -> None:
        # Inherent AbstractModule
        super(TestModule, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Workspace title"
        self.ico = "logo"

        # Show when starting the program
        self.show = True

        # Add menu bar items
        self.add_menu('Tests', 'Test', self.test_function) # When clicked, it will run self.test_function
        self.add_menu('Tests2', 'Test', self.test_function2, args="TETETE") # When clicked, it will run self.test_function2, and pass the args

        # Initiate any variables in self
        self.list_view = None
        self.toolbar = None
        self.chart_view = None
        self.chart_view2 = None

    def handle_file(self, fname):
        # This function is called whenever a new file is loaded
        print(fname)

    def run(self, win: object):
        # Setup a new window
        self.new_window(win)

        # Data (random)
        x = np.linspace(0, 100, 100)
        y = np.random.rand(100)

        # Example of a tree
        self.widgets.multiple_trees(function_connect=self._tree_view_clicked, grid=(0, 5, 2, 12))
        self.widgets.multiple_trees(function_connect=self._tree_view_clicked, grid=(5, 15, 2, 12))
        self.widgets.make_tree_view(function_connect=self._tree_view_clicked, grid=(15, 20, 2, 12))

        # Creating buttons:
        # With border
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(1, 2, 0, 1),
                                 text='button')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(0, 1, 1, 2),
                                 text='button', img='openFolder')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(1, 2, 1, 2))

        # Without border
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(2, 3, 0, 1),
                                 border=False, img='openFolder')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(3, 4, 0, 1),
                                 border=False, text='button')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(2, 3, 1, 2),
                                 border=False, text='button', img='openFolder')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(3, 4, 1, 2), border=False)

        # Create a toolbar
        self.toolbar = self.widgets.make_toolbar(grid=(4, 20, 0, 2))

        # Add buttons to the toolbar
        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='openFolder')
        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='save')
        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='settings')

        # Make a chart
        self.chart_view = self.widgets.make_chart_view(grid=(0, 10, 12, 22))
        self.widgets.add_chart_data(self.chart_view, x_data=x, y_data=y)
        self.widgets.add_chart_data(self.chart_view, x_data=x, y_data=y[::-1])

        self.chart_view2 = self.widgets.make_chart_view(grid=(10, 20, 12, 22))
        self.widgets.add_chart_data(self.chart_view2, x_data=x, y_data=y)

        # Set window contents (finish)
        self.set_content()

    @ staticmethod
    def _tree_view_clicked(file_path):
        print(file_path)

    @ staticmethod
    def test_function():
        print("Test")

    @ staticmethod
    def test_function2(i):
        print(i)
