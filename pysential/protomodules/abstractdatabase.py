# importing the required packages
from .abstractwindow import AbstractWindow
from .formdialogs import FormDialogs
from ..default_modules import excel_database
from ..database import DatabaseManager


class AbstractDatabase(AbstractWindow):
    def __init__(self, obj: object, db_object: object, db_path=None) -> None:
        # Inherent AbstractModule
        super(AbstractDatabase, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Face recognition"
        self.ico = "./img/logos/logo.png"
        self.toolbar = None
        self.db_view = None
        self.query_edit = None
        self.dialog_window = None

        self.db_path = db_path
        self.db_object = db_object
        self.database = DatabaseManager(db_module=self.db_object, db_path=self.db_path)

    def set_database_object(self, db_object):
        self.db_object = db_object

    def set_database_path(self, db_path):
        self.db_path = db_path

    def connect_database(self):
        self.database = DatabaseManager(db_module=self.db_object, db_path=self.db_path)

    def run(self):
        self.toolbar = self.widgets.make_toolbar(grid=(0, 10, 0, 1))
        self.widgets.toolbar_add(self.toolbar, self.placeholder_function, img='search_button')
        self.widgets.toolbar_add(self.toolbar, self._add_sample, img='add_button')
        self.widgets.toolbar_add(self.toolbar, self._add_field, img='add_field')
        self.widgets.toolbar_add(self.toolbar, self._add_table, img='add_database')
        self.widgets.toolbar_add(self.toolbar, self._export_database, img='export')

        self.query_edit = self.widgets.make_line_edit(grid=(10, 20, 0, 1), on_change=self._search_database)

        self.db_view = self.widgets.make_database_view(database=self.database, grid=(0, 20, 1, 2))

        # Set window contents (finish)
        self.set_content()

    @staticmethod
    def placeholder_function():
        print("Invoked placeholder_function")

    def _add_sample(self):
        fields = self.database.get_fields()
        tab_id = self.widgets.get_database_tab(self.db_view)
        self.dialog_window = FormDialogs(self.obj)
        for field in fields[tab_id]:
            self.dialog_window.add_option(field)
        self.dialog_window.connect(self._add_sample_result)
        self.dialog_window.run()

    def _add_sample_result(self, results):
        tables = self.database.get_tables()
        fields = self.database.get_fields()
        tab_id = self.widgets.get_database_tab(self.db_view)
        self.database.add_sample(table_name=tables[tab_id], fields=fields[tab_id], data=results)
        self._update_view()

    def _add_field(self):
        print('Add Field')

    def _search_database(self):
        query = self.widgets.get_line_edit(self.query_edit)
        self.database.set_query(query)
        self._update_view()

    def _export_database(self):
        print('Export Database')

    def _add_table(self):
        field = ('Table name', 'VARCHAR')
        self.dialog_window = FormDialogs(self.obj)
        self.dialog_window.add_option(field)
        self.dialog_window.connect(self._add_table_result)
        self.dialog_window.run()

    def _add_table_result(self, results):
        self.database.add_table(results[0])
        self._update_view()

    def _update_view(self):
        tab_id = self.widgets.get_database_tab(self.db_view)
        self.db_view = self.widgets.make_database_view(database=self.database, index=tab_id, grid=(0, 20, 1, 2))
