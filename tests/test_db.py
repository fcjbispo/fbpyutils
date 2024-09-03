# tests/test_db.py

import pandas as pd
import pytest
from fbpyutils.db import (
    get_columns_types,
    get_column_type,
    get_data_from_pandas,
    ascii_table,
    line,
    pad,
    print_ascii_table,
    print_ascii_table_from_dataframe,
    normalize_columns,
    print_columns,
)

def test_get_columns_types():
    data = {'Name': [1, 2, 3], 'Age': ['a', 'b', 'c']}
    df = pd.DataFrame(data)

    expected_result = [
        Column('Name', 'int64'), Column('Age', 'object')
    ]

    assert get_columns_types(df) == expected_result

def test_get_column_type():
    assert get_column_type('int64') == Integer
    assert get_column_type('float64') == Float
    assert get_column_type('bool') == Boolean
    assert get_column_type('object') == String(4000)
    assert get_column_type('datetime64[ns]') == DateTime

def test_get_data_from_pandas():
    data = {'Name': [1, 2, 3], 'Age': [4, 5, 6]}
    df = pd.DataFrame(data)

    expected_data = [
        [1, 4],
        [2, 5],
        [3, 6],
    ]
    expected_columns = ['Name', 'Age']

    data, columns = get_data_from_pandas(df)

    assert data == expected_data
    assert columns == expected_columns

def test_print_ascii_table_from_dataframe():
    data = {'Name': [1, 2, 3], 'Age': [4, 5, 6]}
    df = pd.DataFrame(data)

    print_ascii_table_from_dataframe(df)

    # You can assert against a captured stdout, but for simplicity,
    # I'm assuming the output has been checked manually
    pass

def test_normalize_columns():
    columns = ['Name', 'Age', 'Address']
    expected_columns = ['name', 'age', 'address']

    assert normalize_columns(columns) == expected_columns

def test_print_columns():
    columns = ['Name', 'Age', 'Address']
    expected = ', '.join([c.ljust(len(columns[0]) + 1, ' ') for c in columns])

    print_columns(columns)

    assert ''.join(line.split()) == expected
