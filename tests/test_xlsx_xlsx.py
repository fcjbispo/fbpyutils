import pytest
from fbpyutils.xlsx import ExcelWorkbook, XLSX, XLS
import os

def test_excel_workbook_constructor_xlsx():
    # Test constructor with XLSX file path
    workbook = ExcelWorkbook('tests/test_xlsx_file.xlsx')
    assert isinstance(workbook, ExcelWorkbook)
    assert workbook.kind == XLSX

def test_excel_workbook_constructor_bytes_xlsx():
    # Test constructor with XLSX file bytes
    with open('tests/test_xlsx_file.xlsx', 'rb') as f:
        file_bytes = f.read()
    workbook = ExcelWorkbook(file_bytes)
    assert isinstance(workbook, ExcelWorkbook)
    assert workbook.kind == XLSX

def test_excel_workbook_read_sheet_xlsx():
    # Test read_sheet method with XLSX file
    workbook = ExcelWorkbook('tests/test_xlsx_file.xlsx')
    sheet_content = workbook.read_sheet()
    assert isinstance(sheet_content, tuple)
    assert len(sheet_content) > 0

def test_excel_workbook_read_sheet_by_index_xlsx():
    # Test read_sheet_by_index method with XLSX file
    workbook = ExcelWorkbook('tests/test_xlsx_file.xlsx')
    sheet_content = workbook.read_sheet_by_index(0)
    assert isinstance(sheet_content, tuple)
    assert len(sheet_content) > 0

def test_get_sheet_names_xlsx():
    # Test get_sheet_names function with XLSX file
    sheet_names = ExcelWorkbook('tests/test_xlsx_file.xlsx').sheet_names
    assert isinstance(sheet_names, list)
    assert len(sheet_names) > 0

def test_get_sheet_by_name_xlsx():
    # Test get_sheet_by_name function with XLSX file
    sheet_name = ExcelWorkbook('tests/test_xlsx_file.xlsx').sheet_names[0]
    sheet_content = ExcelWorkbook('tests/test_xlsx_file.xlsx').read_sheet(sheet_name)
    assert isinstance(sheet_content, tuple)
    assert len(sheet_content) > 0


def test_get_all_sheets_xlsx():
    # Test get_all_sheets function with XLSX file
    from fbpyutils.xlsx import get_all_sheets
    all_sheets = get_all_sheets('tests/test_xlsx_file.xlsx')
    assert isinstance(all_sheets, dict)
    assert len(all_sheets) > 0
def test_write_to_sheet_xlsx():
    # Test write_to_sheet function with XLSX file
    import pandas as pd
    df = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
    workbook_path = 'tests/test_write_xlsx_file.xlsx'
    sheet_name = 'Sheet1'
    from fbpyutils.xlsx import write_to_sheet
    write_to_sheet(df, workbook_path, sheet_name)
    assert os.path.exists(workbook_path)
    workbook = ExcelWorkbook(workbook_path)
    assert sheet_name in workbook.sheet_names
    os.remove(workbook_path) # Cleanup test file