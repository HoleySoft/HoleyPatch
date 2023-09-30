
import sqlite3
import os.path

import logging
logger = logging.getLogger(__name__)


def _push_query(db_path=None, query=None, fetch=False, commit=False):
    if os.path.exists(db_path):
        conn = _load_database(db_path=db_path)
        if not conn:
            return False
        try:
            c = conn.cursor()
            if type(query) == str:
                result = c.execute(query)
            elif type(query) == list:
                [c.execute(q) for q in query]
            if commit:
                conn.commit()
            if fetch:
                return [list(i) for i in result.fetchall()]
            return True
        except sqlite3.DatabaseError as e:
            logger.error(e, exc_info=True)
            return False
        finally:
            conn.close()
    return False


def _load_database(db_path=None):
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute('SELECT name from sqlite_master where type= "table"')
        return conn
    except sqlite3.DatabaseError as e:
        logger.error(e, exc_info=True)
        return False


def make_database(db_path=None) -> bool:
    """Makes a new database in db_path

    Parameters
    ----------
    db_path : str
        File path of called database

    Returns
    -------
    bool
    """
    conn = _load_database(db_path=db_path)
    if conn:
        conn.close()
        return True
    return False


def get_tables(db_path=None) -> list:
    """Get all tables in db_path

    Parameters
    ----------
    db_path : str
        File path of called database

    Returns
    -------
    list
    """
    query = 'SELECT name from sqlite_master where type= "table";'
    return [i[0] for i in _push_query(db_path=db_path, query=query, fetch=True)]


def add_table(db_path=None, table_name='', fields='') -> bool:
    """Add new table to db_path

    Parameters
    ----------
    db_path : str
        File path of called database
    table_name : str
        Name of new table
    fields : str
        Fields string

    Returns
    -------
    bool
    """
    query = "CREATE TABLE " + table_name + " (" + fields + ");"
    return _push_query(db_path=db_path, query=query, fetch=False)


def get_fields(db_path=None, table_name='') -> list:
    """Gets all fields from table_name

    Parameters
    ----------
    db_path : str
        File path of called database
    table_name : str
        Table name to search for fields

    Returns
    -------
    list
    """
    query = 'SELECT sql FROM sqlite_master WHERE tbl_name="'+table_name+'" AND type="table";'
    result = _push_query(db_path=db_path, query=query, fetch=True)[0][0]
    fields = str(result[result.find("(") + 1:result.find("))")]).split(',')
    field_list = [i.split(" ")[0] for i in fields]
    return field_list


def add_field(db_path=None, table_name='', field_info='') -> bool:
    """Add new field to table

    Parameters
    ----------
    db_path : str
        File path of called database
    table_name : str
        Table name to insert new field
    field_info : str
        Field information

    Returns
    -------
    bool
    """
    query = 'ALTER TABLE ' + table_name + ' ADD ' + field_info + ' VARCHAR;'
    return _push_query(db_path=db_path, query=query)


def get_samples(db_path=None, table_name='', field_name='*', search_query='*') -> list:
    """Get samples of specified table_name and field_name

    Parameters
    ----------
    db_path : str
        File path of called database
    table_name : str
        Table name to insert new field
    field_name : str
        Name of field(s) to search
    search_query : str
        Search query, default '*'

    Returns
    -------
    list
    """
    if search_query != '*':
        query = 'SELECT FROM ' + table_name + ' WHERE '
        for c, field in enumerate(field_name):
            query = query + '(' + field + ' LIKE "%' + search_query + '%")'
            if c != len(field_name)-1:
                query = query + ' OR '
        query = query + ';'
    else:
        query = 'SELECT ' + field_name + ' FROM ' + table_name + ';'
    return _push_query(db_path=db_path, query=query, fetch=True)


def add_sample(db_path=None, table_name='', fields=None, data=None) -> bool:
    """Add sample to specified table_name and field_name

    Parameters
    ----------
    db_path : str
        File path of called database
    table_name : str
        Table name to insert new field
    fields : list
        Name of field(s)
    data : list
        List of data to add

    Returns
    -------
    bool
    """
    fields_string = ", ".join(["'" + str(i) + "'" for i in fields])
    data_string = ""
    for c, i in enumerate(data):
        if c != 0:
            data_string += ", "
        if type(i) == str:
            data_string += "'" + i + "'"
        else:
            data_string += str(i)
    query = "INSERT INTO '" + table_name + "' (" + fields_string + ") VALUES (" + data_string + ");"
    return _push_query(db_path=db_path, query=query, commit=True)
