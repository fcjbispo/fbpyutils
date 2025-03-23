'''
Functions to read and MS Excel Spreadsheet files in xls or xlsx formats.
'''
import os
import io
import openpyxl, xlrd
from openpyxl import load_workbook
from datetime import datetime

import pandas as pd

from typing import Union, Dict
    
import warnings

XLS, XLSX = 0, 1


class ExcelWorkbook:
    """Represents an Excel workbook."""

    def __init__(self, xl_file: Union[str, bytes]):
        """
        Initializes an ExcelWorkbook object.

        Args:
            xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.

        Attributes:
            workbook: The underlying openpyxl or xlrd workbook object.
            sheet_names (list): List of sheet names in the workbook.
            kind (int): Type of Excel file (XLSX or XLS).

        Raises:
            FileNotFoundError: If the file path does not exist.
            TypeError: If the file reference is invalid.
        """
        data = None

        if type(xl_file) == str:
            if os.path.exists(xl_file):
                try:
                    with open(xl_file, 'rb') as f:
                        data = f.read()
                        f.close()
                except (OSError, IOError) as e:
                    raise e(f'Error reading the file {xl_file}: {e}')
            else:
                raise NameError(f'File {xl_file} does not exist.')
        elif type(xl_file) == bytes:
            data = xl_file
        else:
            raise TypeError('Invalid file reference. Must be a file path or array of bytes.')

        self.workbook = None
        self.sheet_names = None
        self.kind = XLSX

        try:
            xl_data = io.BytesIO(data)
            warnings.simplefilter("ignore")
            self.workbook = openpyxl.open(xl_data, data_only=True)
            self.sheet_names = self.workbook.sheetnames
        except OSError:
            xl_data.seek(0)
            self.workbook = xlrd.open_workbook(file_contents=xl_data.read())
            self.sheet_names = self.workbook.sheet_names()
            self.kind = XLS
        finally:
            warnings.simplefilter("default")

    def read_sheet(self, sheet_name: str = None) -> tuple[tuple[Union[str, float, int, bool, str, None], ...], ...]:
        """
        Reads the contents of a sheet in the workbook.

        Args:
            sheet_name (str, optional): The name of the sheet to read.
                Defaults to None, which reads the first sheet.

        Returns:
            tuple[tuple[Union[str, float, int, bool, str, None], ...], ...]:
                A tuple of tuples representing the rows and columns of the sheet.

        Raises:
            NameError: If the sheet name is invalid or does not exist.
        """
        sheet_name = sheet_name or self.sheet_names[0]

        if sheet_name not in self.sheet_names:
            raise NameError('Invalid/Nonexistent sheet.')

        sh = self.workbook[sheet_name]

        return tuple(
            tuple(c.value for c in r)
            for r in (sh.iter_rows() if self.kind == XLSX else sh.get_rows())
        )

    def read_sheet_by_index(self, index: int = None) -> tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
        """
        Reads the contents of a sheet in the workbook by index.

        Args:
            index (int, optional): The index of the sheet to read (0-based).
                Defaults to None, which reads the first sheet (index 0).

        Returns:
            tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
                A tuple of tuples representing the rows and columns of the sheet.

        Raises:
            NameError: If the sheet index is invalid or does not exist.
        """
        index = index or 0

        if not 0 <= index < len(self.sheet_names):
            raise NameError('Invalid/Nonexistent sheet.')

        return self.read_sheet(self.sheet_names[index])
"""
Overview:
The ExcelWorkbook class represents an Excel workbook and provides methods to read the contents of sheets within the workbook. It supports both XLSX and XLS file formats. The class constructor takes a file path or array of bytes representing the Excel file. The read_sheet method reads the contents of a specific sheet in the workbook, while the read_sheet_by_index method reads the contents of a sheet based on its index. The sheet names and workbook type are stored as attributes of the class. Exceptions are raised for invalid file paths, file references, sheet names, and sheet indexes.
"""


def get_sheet_names(xl_file: Union[str, bytes]) -> list[str]:
    """
    Retrieves sheet names from an Excel file.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.

    Returns:
        list[str]: List of sheet names.
    """
    xl = ExcelWorkbook(xl_file)
    return xl.sheet_names


def get_sheet_by_name(
    xl_file: Union[str, bytes], sheet_name: str
) -> tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
    """
    Reads a specific sheet from an Excel file by name.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.
        sheet_name (str): Name of the sheet to read.

    Returns:
        tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
            Contents of the sheet as a tuple of tuples.
    """
    xl = ExcelWorkbook(xl_file)
    return xl.read_sheet(sheet_name)


def get_all_sheets(
    xl_file: Union[str, bytes]
) -> Dict[str, tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]]:
    """
    Reads all sheets from an Excel file.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.

    Returns:
        dict[str, tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]]:
            Dictionary where keys are sheet names and values are sheet contents.
    """
    xl = ExcelWorkbook(xl_file)
    sheet_names = xl.sheet_names
    return {
        sheet_name: tuple(xl.read_sheet(sheet_name)) for sheet_name in sheet_names
    }


def write_to_sheet(
    df: pd.DataFrame, workbook_path: str, sheet_name: str
) -> None:
    """
    Writes a pandas DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): DataFrame to write.
        workbook_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to write to.

    Returns:
        None
    """
    if not os.path.exists(workbook_path):
        df.to_excel(
            workbook_path,
            sheet_name=sheet_name,
            index=False,
            freeze_panes=(1, 0),
            header=True,
        )
    else:
        warnings.simplefilter("ignore")
        book = load_workbook(workbook_path)
        writer = pd.ExcelWriter(workbook_path, engine='openpyxl')
        writer.book = book

        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        index, sheet_names = 0, [ws.title for ws in book.worksheets]
        while sheet_name in sheet_names:
            index += 1
            sheet_name = sheet_name + str(index)

        df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            freeze_panes=(1, 0),
            header=True,
        )

        writer.save()
        writer.close()
        book.close()
        warnings.simplefilter("default")