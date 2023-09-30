# importing the required packages
from pysential.protomodules import AbstractWindow
from pysential.default_modules import excel_database
from pysential.database import DatabaseManager


class TestWindow(AbstractWindow):
    def __init__(self, obj: object) -> None:
        # Inherent AbstractModule
        super(TestWindow, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Face recognition"
        self.ico = "logo"
        self.toolbar = None
        self.db_view = None
        self.query_edit = None

        # TODO: make AbstractDatabase
        self.db_path = './data/database/test.xlsx'

        self.database = DatabaseManager(db_module=excel_database, db_path=self.db_path)

    def run(self, win: object, *args, **kwargs):
        self.toolbar = self.widgets.make_toolbar(grid=(0, 10, 0, 1))
        self.widgets.toolbar_add(self.toolbar, self.test_function, img='search_button')
        self.widgets.toolbar_add(self.toolbar, self._add_sample, img='add_button')
        self.widgets.toolbar_add(self.toolbar, self._add_field, img='add_field')
        self.widgets.toolbar_add(self.toolbar, self._add_table, img='add_database')
        self.widgets.toolbar_add(self.toolbar, self._export_database, img='export')

        self.query_edit = self.widgets.make_line_edit(grid=(10, 20, 0, 1), on_change=self._search_database)

        # tables = self.database.get_tables()
        # fields = self.database.get_fields(tables)
        # samples = self.database.get_samples(table_names=tables)

        self.db_view = self.widgets.make_database_view(database=self.database, grid=(0, 20, 1, 2))

        # Set window contents (finish)
        self.set_content()

    @staticmethod
    def test_function():
        print("Test")

    def _add_sample(self, *args, tab_idx=None):
        print('Add Sample')

    def _add_field(self, *args, tab_idx=None):
        print('Add Field')

    def _search_database(self, *args, tab_idx=None):
        query = self.widgets.get_line_edit(self.query_edit)
        self.database.set_query(query)
        self.db_view = self.widgets.make_database_view(database=self.database, grid=(0, 20, 1, 2))

    def _export_database(self, *args):
        print('Export Database')

    def _add_table(self, *args):
        print('Add Table')
