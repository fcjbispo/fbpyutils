'''
Utility functions to manipulate data and dataframes.
'''
import pandas as pd
from sqlalchemy import inspect, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, text, Index
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists


def table_operation(dataframe, table_name, connection, schema=None, operation='upsert', keys=None, index=False):
    """
    Perform upsert or replace operation on a table based on the provided dataframe.

    Args:
        dataframe (pd.DataFrame): The pandas DataFrame containing the data to be inserted or updated.
        table_name (str): The name of the table to operate on.
        connection (sqlalchemy.engine.Engine): The SQLAlchemy engine connection.
        operation (str, optional): The operation to be performed ('upsert' or 'replace'). Default is 'upsert'.
        keys (list of str, optional): List of column names to use as keys for upsert operation. Default is None.
        index (bool, optional): Whether to create an index using the keys. Default is False.

    Returns:
        dict: A dictionary containing information about the performed operation.

    """
    # Set default value for keys
    if keys is None:
        keys = []

    # Check if the table exists in the database, if not create it
    if not inspect(connection).has_table(table_name):
        create_table_from_dataframe(dataframe, table_name, connection, schema, keys, index)

    # Get the table object
    metadata = MetaData(schema)
    table = Table(table_name, metadata, autoload=True, autoload_with=connection)

    # Initialize counts for insertions, updates, and failures
    insert_count = 0
    update_count = 0
    failure_count = 0

    # Upsert operation
    if operation == 'upsert':
        with connection.begin() as trans:
            for _, row in dataframe.iterrows():
                values = {col: row[col] for col in dataframe.columns}
                # Check if row exists in the table based on keys
                exists_stmt = exists(table.select().where(text(' AND '.join([f"{col} = :{col}" for col in keys]))))
                exists_query = exists_stmt.params(**values)
                if connection.execute(exists_query).scalar():
                    # Perform update
                    update_stmt = table.update().where(text(' AND '.join([f"{col} = :{col}" for col in keys]))).values(**values)
                    connection.execute(update_stmt)
                    update_count += 1
                else:
                    # Perform insert
                    try:
                        insert_stmt = table.insert().values(**values)
                        connection.execute(insert_stmt)
                        insert_count += 1
                    except IntegrityError:
                        # Handle failure due to unique constraint violation
                        failure_count += 1
                        continue

    # Replace operation
    elif operation == 'replace':
        with connection.begin() as trans:
            # Drop the index if it exists
            if index:
                index_name = f"pki_{table_name}"
                connection.execute(f"DROP INDEX IF EXISTS {index_name}")

            # Truncate the table
            connection.execute(table.delete())

            # Insert new data
            dataframe.to_sql(table_name, connection, if_exists='append', index=False)

            # Create the index if required
            if index:
                keys_to_index = keys if keys else dataframe.columns
                index_obj = Index(f"pki_{table_name}", *keys_to_index)
                index_obj.create(connection)

            # Get the total number of records inserted
            insert_count = len(dataframe)

    return {
        'operation': operation,
        'table_name': table_name,
        'total_insertions': insert_count,
        'total_updates': update_count,
        'total_failures': failure_count,
    }


def create_table_from_dataframe(dataframe, table_name, connection, schema=None, keys=None, index=False):
    """
    Create a table in the database using the provided pandas DataFrame as a schema.

    Args:
        dataframe (pd.DataFrame): The pandas DataFrame containing the schema information.
        table_name (str): The name of the table to be created.
        connection (sqlalchemy.engine.Engine): The SQLAlchemy engine connection.
        keys (list of str, optional): List of column names to use as keys for index creation. Default is None.
        index (bool, optional): Whether to create an index using the keys. Default is False.

    """
    metadata = MetaData(schema)
    columns = get_columns_types(dataframe)
    table = Table(table_name, metadata, *columns)

    # Create the index if required
    if index:
        keys = [k for k in keys] or [k for k in dataframe]
        keys_to_index = [c for c in table.columns if c.name in keys]
        index_obj = Index(f"pki_{table_name}", *keys_to_index, unique=True)
        table.indexes.add(index_obj)

    metadata.create_all(connection)


def get_columns_types(dataframe):
    return  [
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
