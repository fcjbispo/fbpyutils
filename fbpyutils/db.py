'''
Utility functions to manipulate data, tables and dataframes.
'''
import pandas as pd
from sqlalchemy import inspect, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, text, Index
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists
import hashlib
import re


def isolate(df, group_columns, unique_columns):
    """
    Filters the dataframe to isolate rows with maximum values in unique_columns 
    for each unique combination of values in group_columns.
    Parameters:
    -----------
    df : pd.DataFrame
        The input pandas dataframe.
    group_columns : list
        A list of column names used for grouping the dataframe.
    unique_columns : list
        A list of column names for which the maximum values are calculated.
    Returns:
    --------
    pd.DataFrame
        A pandas dataframe containing only the rows with maximum values in unique_columns
        for each unique combination of values in group_columns.
    Example:
    --------
    >>> df = pd.DataFrame({'Group': ['A', 'A', 'B', 'B'],
    ...                    'Value': [1, 2, 3, 4],
    ...                    'Unique': [5, 6, 7, 8]})
    >>> isolate(df, ['Group'], ['Value', 'Unique'])
      Group  Value  Unique
    1     A      2       6
    3     B      4       8
    """
    dfs = []
    for u in unique_columns:
        dfs.append(df.groupby(group_columns)[u].idxmax())
    rows_ids = pd.concat(dfs).drop_duplicates()
    return df.loc[rows_ids]


_create_hash_column = lambda x, y=12: x.apply(lambda x: hashlib.md5(str(x).encode()).hexdigest()[:y], axis=1)


def add_hash_column(df, column_name, length=12):
    """
    Adds a hash column to the given DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to be created.
        length (int): The length of the column to be created. Defaults to 12.

    Returns:
        pandas.DataFrame: A new DataFrame with the hash column added as the first column.
                          The order of other columns remains the same.
    """
    # Parameter checks
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The 'df' parameter should be of type pandas.DataFrame.")
    if not isinstance(column_name, str):
        raise TypeError("The 'index_name' parameter should be a string.")
    if not isinstance(length, int):
        raise TypeError("The 'length' parameter should be an integer.")
    if length <= 0:
        raise ValueError("The 'length' parameter should be greater than 0.")
    # Creates the hash column
    df[column_name] = _create_hash_column(df, length)
    xcolumns = [column_name, *[c for c in df.columns if c != column_name]]
    return df[xcolumns].copy()


def add_hash_index(df, index_name='id', length=12):
    """
    Replaces the dataframe index with a hash string with length of 12 characters
    calculated using all columns values for each row and renames the dataframe index
    to the name supplied by index_name.
    Parameters:
    -----------
    df : pd.DataFrame
        A pandas dataframe.
    index_name : str
        The name to be given to the new index. Defaults to 'id'
    length : int
        The length of the column to be created. Defaults to 12.
    Returns:
    --------
    pd.DataFrame
        A pandas dataframe with the new index.
    Example:
    --------
    >>> df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    >>> add_hash_index(df, 'new_index')
               col1 col2
    new_index          
    8b9c45e2a9f6   1   a
    3d4c4f4f4d1f   2   b
    5b5d8c7a2a4c   3   c
    """
    # Parameter checks
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The 'df' parameter should be of type pandas.DataFrame.")
    if not isinstance(index_name, str):
        raise TypeError("The 'index_name' parameter should be a string.")
    if not isinstance(length, int):
        raise TypeError("The 'length' parameter should be an integer.")
    if length <= 0:
        raise ValueError("The 'length' parameter should be greater than 0.")
    # Creates the hash column
    hash_df = _create_hash_column(df, length)
    # Set the hash string as the new index
    df.index = hash_df
    # Rename the index
    df.index.name = index_name
    return df


def table_operation(operation, dataframe, engine, table_name, schema=None, keys=None, index=None, commit_at=50):
    """
    Perform upsert or replace operation on a table based on the provided dataframe.

    Args:
        operation (str, optional): The operation to be performed ('upsert' or 'replace').
        dataframe (pd.DataFrame): The pandas DataFrame containing the data to be inserted or updated.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine engine.
        table_name (str): The name of the table to operate on.
        schema (str, optional): the schena name to preffix the table objects.
        keys (list of str, optional for operation=replace): List of column names to use as keys for upsert operation.
        index (str, optional): Whether to create an index and what kind using the keys. Default is None (not create index).
            If an index must be created, index be in 'standard' or 'unique'.
        commit_at (int, optional): Number of rows to commit in the database at once. Defaults to 50. 
            Must be > 1 and < total rows of the dataframe.

    Returns:
        dict: A dictionary containing information about the performed operation.

    """
    # Check parameters
    if operation not in ('append', 'upsert', 'replace'):
        raise ValueError("Invalid operation. Valid values: append|upsert|replace.")
    
    if not type(dataframe) == pd.DataFrame:
        raise ValueError("Dataframe must be a Pandas DataFrame.")
    
    if operation == 'upsert' and not keys:
        raise ValueError("For upsert operation 'keys' parameter is mandatory.")
    
    if keys and not type(keys) == list:
        raise ValueError("Parameters 'keys' must be a list of str.")
    
    if (keys and index) and index not in ('standard', 'unique', 'primary'):
        raise ValueError("If an index will be created, it must be any of standard|unique|primary.")
    
    commit_at = commit_at or 50
    if not type(commit_at) == int or (commit_at < 1 and commit_at > len(dataframe)):
        raise ValueError('Commit At must be > 1 and < total rows of DataFrame.')

    # Check if the table exists in the database, if not create it
    if not inspect(engine).has_table(table_name, schema=schema):
        create_table(dataframe, engine, table_name, schema, keys, index)

    # Get the table object
    metadata = MetaData(schema)
    table = Table(table_name, metadata, autoload_with=engine)

    # Initialize reports for insertions, updates, and failures
    inserts = 0
    updates = 0
    skips   = 0
    failures = []

    try:
        with engine.connect() as conn:
            step = 'drop table'
            if operation == 'replace':
                conn.execute(table.delete())
                conn.commit()

            rows = 0
            for i, row in dataframe.iterrows():
                try:
                    exists = False
                    step = 'check existence'
                    if keys:
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
                            exists = True 
                    if exists:
                        if  operation == 'upsert':
                            # Perform update
                            step = 'replace with update'
                            update_values = {
                                k: values[k]
                                for k in values.keys() if k not in keys
                            }

                            update_stmt = table.update().where(
                                text(' AND '.join([f"{col}=:{col}" for col in keys]))
                            ).values(**update_values)

                            update_stmt = text(str(update_stmt))
                            conn.execute(update_stmt, values)
                            updates += 1
                        else:
                            skips += 1
                    else:
                        # Perform insert
                        step = 'perform insert'
                        insert_stmt = table.insert().values(**values)
                        conn.execute(insert_stmt)
                        inserts += 1

                    rows += 1
                    if rows >= commit_at:
                        conn.commit()
                        rows = 0
                except Exception as e:
                        failures .append({
                            'step': step,
                            'row': (
                                i, ', '.join([
                                    f"{k}='{str(v)}'" for k, v in values.items()
                            ])),
                            'error': str(e)
                        })
                        conn.rollback()
                        continue    
            conn.commit()
    except Exception as e:
        conn.rollback()
        failures.append({
            'step': step,
            'row': None,
            'error': str(e)
        })

    return {
        'operation': operation,
        'table_name': '.'.join([schema, table_name]),
        'insertions': inserts,
        'updates': updates,
        'skips': skips,
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
    
    if keys and index and index not in ('standard', 'unique', 'primary'):
        raise ValueError("If an index will be created, it must be any of standard|unique|primary.")

    metadata = MetaData(schema)

    if keys and index == 'primary':
        columns = get_columns_types(dataframe, primary_keys=keys)
    else:
        columns = get_columns_types(dataframe, primary_keys=[])

    table = Table(table_name, metadata, *columns)

    # Create the index if required
    if keys and index in ('standard', 'unique'):
        unique = (index == 'unique')
        idx_suffix = 'uk' if unique else 'ik'
        table.indexes.add(
            create_index(f"{table_name}_i001_{idx_suffix}", table, keys, unique)
        )

    return metadata.create_all(engine)


def create_index(name, table, keys, unique=True):
    index_cols = [c for c in table.columns if c.name in keys]
    index_obj = Index(name, *index_cols, unique=unique)
    
    return index_obj


def get_columns_types(dataframe, primary_keys=[]):
    """
    Returns a list of Column objects representing the columns of the given dataframe.
     Args:
        dataframe (pandas.DataFrame): The input dataframe for which column types are to be determined.
        primary_keys (List[str]): Optional list of primary key column names. 
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
        Column(
            col, get_column_type(dataframe.dtypes[col]), primary_key=(col in primary_keys)
        ) for col in dataframe.columns
    ]


def get_column_type(dtype):
    """
    Map Pandas data types to SQLAlchemy data types.

    Args:
        dtype (dtype): The Pandas data type to be mapped.

    Returns:
        sqlalchemy.sql.sqltypes.TypeEngine: The corresponding SQLAlchemy data type.

    """
    if dtype in ('int64', 'int32', 'int'):
        return Integer()
    elif dtype in ('float64', 'float32', 'float'):
        return Float()
    elif dtype == 'bool':
        return Boolean()
    elif dtype == 'object':
        return String()
    elif dtype == 'datetime64[ns]':
        return DateTime()
    else:
        return String()


def get_data_from_pandas(df, include_index=False):
    """
    Extracts data and column names from a Pandas DataFrame.

    Args:
        df (pandas.DataFrame): A Pandas DataFrame.
        include_index (bool, optional): If True, includes the index column in the extracted data. Defaults to False.

    Returns:
        tuple: A tuple containing the extracted data and column names.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Name': ['John', 'Alice', 'Bob'], 'Age': [25, 30, 40]})
        >>> data, columns = get_data_from_pandas(df)
        >>> print(data)
        [['John', 25], ['Alice', 30], ['Bob', 40]]
        >>> print(columns)
        ['Name', 'Age']
    """
    if not 'pandas.core.frame.DataFrame' in str(type(df)):
        raise ValueError('Not a Pandas DataFrame.')
    
    data = [list(d) for d in df.to_records(index=include_index)]

    columns = list(c for c in df.columns)

    if include_index:
        columns.insert(0, 'Index')

    return data, columns


def ascii_table(data, columns=[], alignment='left'):
    """
    Creates an ASCII table representation of the given data.

    Args:
        data (list): A list of lists representing the data rows.
        columns (list, optional): A list of column names. Defaults to an empty list.
        alignment (str, optional): The alignment of the table cells. Valid values are 'left', 'right', or 'center'. Defaults to 'left'.

    Returns:
        list: A list of strings representing the ASCII table.

    Example:
        >>> data = [['John', 25, 'USA'], ['Alice', 30, 'Canada'], ['Bob', 40, 'UK']]
        >>> columns = ['Name', 'Age', 'Country']
        >>> table = ascii_table(data, columns=columns, alignment='center')
        >>> for line in table:
        ...     print(line)
        +-------+-----+---------+
        |  Name | Age | Country |
        +-------+-----+---------+
        |  John |  25 |   USA   |
        | Alice |  30 |  Canada |
        |  Bob  |  40 |    UK   |
        +-------+-----+---------+

    """
    if len(data) == 0:
        return None

    data = [list(e) for e in data] 
    columns = list([c for c in columns])
    alignment = alignment or 'left'

    def pad(x, size, char=' ', where='center'):
        char = char or ' '
        where = where or 'center'
        return str(x).rjust(size, char) \
            if where=='right' else str(x).ljust(size, char) \
                if where=='left' else str(x).center(size, char)

    def line(rows, sizes, where='center'):
        return '|'+'|'.join([
            pad(rows[i], sizes[i], where=where) 
            for i in range(0, len(rows))
        ])+'|'

    col_lenghts = tuple(set([len(d) for d in data]))

    if len(col_lenghts) == 0:
        return None

    if len(col_lenghts) > 1:
        raise ValueError('Number of columns mismatch among rows.')
    
    if alignment not in ('left', 'right', 'center'):
        raise ValueError(
            'Alignment valid values: left|right|center')
        
    if columns is None or len(columns) == 0:
        columns = [f'column_{i}' for i in range(0, col_lenghts[0])]

    if len(columns) != col_lenghts[0]:
        print(col_lenghts, columns)
        raise ValueError(f'Number of columns mismatch with data row.')
    
    xdata = [[row[i] for i in range(len(data[0])) if columns[i] in columns] for row in data]

    max_sizes = list(
        max(n) for n in list(
            list(
                len(str(r[i])) for r in xdata
            ) for i in range(0, len(xdata[0]))
        )
    )

    line_sep = ''.join(['+'+'-'*i for i in max_sizes])+'+'

    table = []
    table.append(line_sep)
    table.append(line(columns, max_sizes))
    table.append(line_sep)
    for row in data:
        table.append(line(row, max_sizes, where=alignment))
    table.append(line_sep)

    return table


def print_ascii_table(data, columns=[], alignment='left'):
    """
    Prints the ASCII table representation of the given data.

    Args:
        data (list): A list of lists representing the data rows.
        columns (list, optional): A list of column names. Defaults to an empty list.
        alignment (str, optional): The alignment of the table cells. Valid values are 'left', 'right', or 'center'. Defaults to 'left'.

    Returns:
        None

    Example:
        >>> data = [['John', 25, 'USA'], ['Alice', 30, 'Canada'], ['Bob', 40, 'UK']]
        >>> columns = ['Name', 'Age', 'Country']
        >>> print_ascii_table(data, columns=columns, alignment='center')
        +-------+-----+---------+
        |  Name | Age | Country |
        +-------+-----+---------+
        |  John |  25 |   USA   |
        | Alice |  30 |  Canada |
        |  Bob  |  40 |    UK   |
        +-------+-----+---------+

    """
    table = ascii_table(data, columns=columns, alignment=alignment)

    for line in table:
        print(line)


def print_ascii_table_from_dataframe(df, alignment='left'):
    """
    Prints the ASCII table representation of a pandas DataFrame.
    - Attempts to extract the data and column names from the pandas DataFrame using a helper function.
    - Raises a ValueError if the DataFrame is invalid.

    Args:
        df (pandas.DataFrame): A pandas DataFrame.
        alignment (str, optional): The alignment of the table cells. Valid values are 'left', 'right', or 'center'. Defaults to 'left'.

    Returns:
        None

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Name': ['John', 'Alice', 'Bob'], 'Age': [25, 30, 40], 'Country': ['USA', 'Canada', 'UK']})
        >>> print_ascii_table_from_dataframe(df, alignment='center')
        +-------+-----+---------+
        |  Name | Age | Country |
        +-------+-----+---------+
        |  John |  25 |   USA   |
        | Alice |  30 |  Canada |
        |  Bob  |  40 |    UK   |
        +-------+-----+---------+

    """
    data, columns = None, None
    try:
        data, columns = get_data_from_pandas(df)
    except Exception as e:
        raise ValueError(f'Invalid pandas dataframe: {e}.')

    if all([data, columns]):
        print_ascii_table(data, columns, alignment)

    
def normalize_columns(cols):
    """
    Normalizes a list of column names.
    - Removes any non-alphanumeric characters and underscores from each column name.
    - Converts each column name to lowercase.

    Args:
        cols (list): A list of column names.

    Returns:
        list: A new list of normalized column names.

    Example:
        >>> cols = ['Name', 'Age', 'Address']
        >>> normalized_cols = normalize_columns(cols)
        >>> print(normalized_cols)
        ['name', 'age', 'address']
    """
    return [
        [re.sub('[^0-9a-zA-Z_]+', '', x).lower() for x in cols]
    ]


def print_columns(cols, normalize=False, length=None, quotes=False):
    """
    Prints a formatted string representation of a list of columns.

    Args:
        cols (list): A list of column names.
        normalize (bool, optional): If True, normalizes the columns before printing. Defaults to False.
        length (int, optional): The desired length for each column. If not provided, the length will be determined automatically. Defaults to None.
        quotes (bool, optional): If True, adds single quotes around each column name. Defaults to False.

    Returns:
        None

    Example:
        >>> cols = ['Name', 'Age', 'Address']
        >>> print_columns(cols, normalize=True, length=10, quotes=True)
        'name     ', 'age      ', 'address  '
    """
    if normalize:
        cols = normalize_columns(cols)

    if quotes:
        cols = [f"'{c}'" for c in cols]

    length = length or max([len(c) for c in cols])

    colstrings = ', '.join([c.ljust(length, ' ') for c in cols])

    print(colstrings)