
class DatabaseManager:
    """A class used to manage multi database types

    Attributes
    ----------
    db_path : str
        File path of called database
    module : object
        Module to use with database file
    search_query : str
        Active search query

    Methods
    ----------
    set_query(search_query: str) -> None
        Sets the active search query
    make_database -> bool
        Makes a new database of type module in db_path
    get_tables -> list
        Retrieves all tables in db_path
    add_table(table_name='', fields='') -> bool
        Adds new table to db_path
    get_field(table_name='') -> list
        text
    get_fields(table_names=list()) -> list
        text
    add_field(table_name='', field_info='') -> bool
        text
    get_sample(table_name='', field_name='*', search_query='*')
        text
    get_samples(self, table_names=list(), field_names='*', search_query='*') -> list
        text
    add_sample(self, table_name='', fields=None, data=None) -> bool
        text
    """
    def __init__(self, db_module=None, db_path=None):
        self.db_path = db_path
        self.module = db_module
        self.search_query = '*'

    def set_query(self, search_query: str) -> None:
        """Sets the active search query

        Parameters
        ----------
        search_query : str
            Search query to apply over the database
        """
        if search_query == '':
            self.search_query = '*'
        else:
            self.search_query = search_query

    def make_database(self) -> bool:
        """Makes a new database of type module in db_path

        Returns
        -------
        bool
        """
        return self.module.make_database(db_path=self.db_path)

    def get_tables(self) -> list:
        """Sets the active search query

        Parameters
        ----------
        search_query : str
            Search query to apply over the database

        Returns
        -------
        None
        """
        return self.module.get_tables(db_path=self.db_path)

    def add_table(self, table_name='', fields='') -> bool:
        """Adds new table to db_path

        Parameters
        ----------
        table_name : str
            New table name
        fields : str
            Fields to add

        Returns
        -------
        bool
        """
        return self.module.add_table(table_name=table_name, fields=fields, db_path=self.db_path)

    def get_field(self, table_name='') -> list:
        """Get fields from table_name

        Parameters
        ----------
        table_name : str
            Name of the table to retrieve fields

        Returns
        -------
        list
        """
        return self.module.get_fields(db_path=self.db_path, table_name=table_name)

    def get_fields(self, table_names=list()) -> list:
        """Same as get_field; except with a list of table_name(s), see get_field

        Parameters
        ----------
        table_names : list
            List of table names

        Returns
        -------
        list
        """
        if len(table_names) == 0:
            table_names = self.get_tables()
        return [self.get_field(table) for table in table_names]

    def add_field(self, table_name='', field_info='') -> bool:
        """Adds new field to table_name with field_info

        Parameters
        ----------
        table_name : str
            Name of table to add field
        field_info : str
            Info of field, field type and name

        Returns
        -------
        bool
        """
        return self.module.add_field(table_name=table_name, field_info=field_info, db_path=self.db_path)

    def get_sample(self, table_name='', field_name='*'):
        """Retrieves samples from table_name with field_name and search_query filter, see set_query

        Parameters
        ----------
        table_name : str
            Name of table to search
        field_name : str
            Field query, default is '*'

        Returns
        -------
        None
        """
        return self.module.get_samples(db_path=self.db_path, table_name=table_name, field_name=field_name,
                                       search_query=self.search_query)

    def get_samples(self, table_names=list(), field_names='*') -> list:
        """Same as get_sample; except with a list of table_name(s), see get_sample

        Parameters
        ----------
        table_names : list
            List of table names
        field_names : str
            Field query, default is '*'

        Returns
        -------
        list
        """
        samples = []
        if type(field_names) == list:
            for table_name, field_name in zip(table_names, field_names):
                samples.append(
                    self.get_sample(table_name=table_name, field_name=field_name)
                )
        else:
            for table_name in table_names:
                samples.append(
                    self.get_sample(table_name=table_name, field_name=field_names)
                )
        return samples

    def add_sample(self, table_name='', fields=None, data=None) -> bool:
        """Add new sample to database

        Parameters
        ----------
        table_name : str
            Search query to apply over the database
        fields : list
            List of field names
        data : list
            List of data to add to fields

        Returns
        -------
        bool
        """
        return self.module.add_sample(table_name=table_name, fields=fields, data=data, db_path=self.db_path)
