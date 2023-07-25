'''
Utility functions to manipulate data and dataframes.
'''
import pandas as pd
from sqlalchemy import inspect, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, text, Index
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists


def table_operation(operation, dataframe, engine, table_name, schema=None, keys=None, index=None):
    """
    Perform upsert or replace operation on a table based on the provided dataframe.

    Args:
        dataframe (pd.DataFrame): The pandas DataFrame containing the data to be inserted or updated.
        table_name (str): The name of the table to operate on.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine engine.
        operation (str, optional): The operation to be performed ('upsert' or 'replace').
        keys (list of str, optional for operation=replace): List of column names to use as keys for upsert operation.
        index (str, optional): Whether to create an index and what kind using the keys. Default is None (not create index).
            If an index muste be created, index be in 'standard' or 'unique'.

    Returns:
        dict: A dictionary containing information about the performed operation.

    """
    # Check parameters
    if operation not in ('upsert', 'replace'):
        raise ValueError("Invalid operation. Valid values: upsert|replace.")
    
    if not type(dataframe) == pd.DataFrame:
        raise ValueError("Dataframe must be a Pandas DataFrame.")
    
    if operation == 'upsert' and not keys:
        raise ValueError("For upsert operation 'keys' parameter is mandatory.")
    
    if keys and not type(keys) == list:
        raise ValueError("Parameters 'keys' must be a list of str.")
    
    if keys and index and index not in ('standard', 'unique'):
        raise ValueError("If an index will be created, it must be any of standard|unique.")

    # Set default value for keys
    if keys is None:
        keys = []

    # Check if the table exists in the database, if not create it
    if not inspect(engine).has_table(table_name, schema=schema):
        create_table(dataframe, engine, table_name, schema, keys, index)

    # Get the table object
    metadata = MetaData(schema)
    table = Table(table_name, metadata, autoload_with=engine)

    # Initialize reports for insertions, updates, and failures
    insert_count = 0
    update_count = 0
    failures = []

    try:
        with engine.begin() as conn:
            step = 'drop table'
            if operation == 'replace':
                conn.execute(table.delete())

            for i, row in dataframe.iterrows():
                try:
                    step = 'check existence'
                    values = {col: row[col] for col in dataframe.columns}

                    # Check if row exists in the table based on keys
                    exists_query = table.select().where(
                        exists(
                            table.select().where(
                                text(' AND '.join([f"{col} = :{col}" for col in keys]))
                            )
                        )
                    ).params(**values)
                    if conn.execute(exists_query).fetchone():
                        # Perform update
                        step = 'replace with update'
                        update_filter = {
                            k: values[k]
                            for k in keys
                        }

                        update_values = {
                            k: values[k]
                            for k in values.keys() if k not in keys
                        }

                        update_stmt = table.update().where(
                            text(' AND '.join([f"{col}=:{col}" for col in keys]))
                        ).values(**update_values)

                        update_stmt = text(str(update_stmt))
                        conn.execute(update_stmt).params(**values)
                        update_count += 1
                    else:
                        # Perform insert
                        step = 'replace with insert'
                        insert_stmt = table.insert().values(**values)
                        conn.execute(insert_stmt)
                        insert_count += 1
                except Exception as e:
                        failures .append({
                            'step': step,
                            'row': (i, values),
                            'error': str(e)
                        })
                        continue
    
            conn.commit()
            conn.close()
    except Exception as e:
        failures.append({
            'step': step,
            'row': None,
            'error': str(e)
        })

    return {
        'operation': operation,
        'table_name': '.'.join([schema, table_name]),
        'insertions': insert_count,
        'updates': update_count,
        'failures': failures,
    }


def create_table(dataframe, engine, table_name, schema=None, keys=None, index=None):
    """
    Create a table in the database using the provided pandas DataFrame as a schema.

    Args:
        dataframe (pd.DataFrame): The pandas DataFrame containing the schema information.
        table_name (str): The name of the table to be created.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine engine.
        keys (list of str, optional): List of column names to use as keys for index creation. Default is None.
        index (str, optional): Whether to create an index and what kind using the keys. Default is None (not create index).
            If an index muste be created, index be in 'standard' or 'unique'.

    """
    # Check parameters
    if not type(dataframe) == pd.DataFrame:
        raise ValueError("Dataframe must be a Pandas DataFrame.")
    
    if keys and not type(keys) == list:
        raise ValueError("Parameters 'keys' must be a list of str.")
    
    if keys and index and index not in ('standard', 'unique'):
        raise ValueError("If an index will be created, it must be any of standard|unique.")

    metadata = MetaData(schema)
    columns = get_columns_types(dataframe)
    table = Table(table_name, metadata, *columns)

    # Create the index if required
    if index:
        unique = (index == 'unique')
        table.indexes.add(
            create_index(f"pki_{table_name}", table, keys, unique)
        )

    metadata.create_all(engine)


def create_index(name, table, keys, unique=True):
    index_cols = [c for c in table.columns if c.name in keys]
    index_obj = Index(name, *index_cols, unique=unique)
    
    return index_obj


def get_columns_types(dataframe):
    """
    Returns a list of Column objects representing the columns of the given dataframe.
     Args:
        dataframe (pandas.DataFrame): The input dataframe for which column types are to be determined.
     Returns:
        list: A list of Column objects, where each object represents a column in the dataframe.
     Raises:
        None.
     Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
        >>> get_columns_types(df)
        [Column('A', 'int64'), Column('B', 'object')]
     Column object:
        - The Column object represents a column in a dataframe and stores its name and type.
         Attributes:
            name (str): The name of the column.
            dtype (str): The data type of the column.
         Example:
            >>> col = Column('A', 'int64')
            >>> col.name
            'A'
            >>> col.dtype
            'int64'
    """
    return [
        Column(col, get_column_type(dataframe.dtypes[col])) for 
        col in dataframe.columns
    ]


def get_column_type(dtype):
    """
    Map Pandas data types to SQLAlchemy data types.

    Args:
        dtype (dtype): The Pandas data type to be mapped.

    Returns:
        sqlalchemy.sql.sqltypes.TypeEngine: The corresponding SQLAlchemy data type.

    """
    if dtype == 'int64':
        return Integer()
    elif dtype == 'float64':
        return Float()
    elif dtype == 'bool':
        return Boolean()
    elif dtype == 'object':
        return String()
    elif dtype == 'datetime64[ns]':
        return DateTime()
    else:
        return String()
