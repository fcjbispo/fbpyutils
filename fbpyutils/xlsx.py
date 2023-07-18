'''
Functions to read and MS Excel Spreadsheet files in xls or xlsx formats.
'''
import os
import io
import openpyxl, xlrd
from openpyxl import load_workbook

import pandas as pd

from typing import Union

import warnings

XLS, XLSX = 0, 1


class ExcelWorkbook:
    """
    Represents an Excel workbook.
     Args:
        xl_file (str or bytes): The file path or array of bytes representing the Excel file.
     Attributes:
        workbook: The Excel workbook object.
        sheet_names: A list of sheet names in the workbook.
        kind: The type of Excel file (XLSX or XLS).
     Raises:
        FileNotFoundError: If the file path does not exist.
        TypeError: If the file reference is invalid.
     """

    def __init__(self, xl_file):
        """
        Initializes a new instance of the ExcelWorkbook class.
         Args:
            xl_file (str or bytes): The file path or array of bytes representing the Excel file.
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

    def read_sheet(self, sheet_name=None):
        """
        Reads the contents of a sheet in the workbook.
         Args:
            sheet_name (str, optional): The name of the sheet to read. If not provided, reads the first sheet.
         Returns:
            tuple of tuples: A tuple of tuples representing the rows and columns of the sheet.
         Raises:
            NameError: If the sheet name is invalid or does not exist.
         """
        sheet_name = sheet_name or self.sheet_names.get(sheet_name)

        if sheet_name not in self.sheet_names:
            raise NameError('Invalid/Nonexistent sheet.')

        sh = self.workbook[sheet_name]

        return (
            tuple(c.value for c in r)
            for r in (sh.iter_rows() if self.kind == XLSX else sh.get_rows())
        )

    def read_sheet_by_index(self, index=None):
        """
        Reads the contents of a sheet in the workbook by index.
         Args:
            index (int, optional): The index of the sheet to read. If not provided, reads the first sheet.
         Returns:
            tuple of tuples: A tuple of tuples representing the rows and columns of the sheet.
         Raises:
            NameError: If the sheet index is invalid or does not exist.
         """

        index = index or 0

        if index < 0 or index >= len(self.sheet_names):
            raise NameError('Invalid/Nonexistent sheet.')

        return self.read_sheet(self.sheet_names[index])
"""
Overview:
The ExcelWorkbook class represents an Excel workbook and provides methods to read the contents of sheets within the workbook. It supports both XLSX and XLS file formats. The class constructor takes a file path or array of bytes representing the Excel file. The read_sheet method reads the contents of a specific sheet in the workbook, while the read_sheet_by_index method reads the contents of a sheet based on its index. The sheet names and workbook type are stored as attributes of the class. Exceptions are raised for invalid file paths, file references, sheet names, and sheet indexes.
"""


def get_sheet_names(xl_file):
    """
    Get the names of all sheets in an Excel file.
     Args:
        xl_file (str): File path of the Excel file.
     Returns:
        list: List of sheet names in the Excel file.
     Functionality:
        - Create an ExcelWorkbook object using the xl_file.
        - Retrieve the sheet names from the ExcelWorkbook object.
     Overview:
        This function allows you to obtain the names of all sheets in an Excel file.
    """
    xl = ExcelWorkbook(xl_file)

    return xl.sheet_names


def get_sheet_by_name(xl_file, sheet_name):
    """
    Get the contents of a specific sheet in an Excel file.
     Args:
        xl_file (str): File path of the Excel file.
        sheet_name (str): Name of the sheet to retrieve.
     Returns:
        list: Contents of the specified sheet as a list of tuples.
     Functionality:
        - Create an ExcelWorkbook object using the xl_file.
        - Read the contents of the specified sheet using the sheet_name.
     Overview:
        This function allows you to retrieve the contents of a specific sheet in an Excel file.
    """
    xl = ExcelWorkbook(xl_file)

    return xl.read_sheet(sheet_name)


def get_all_sheets(xl_file):
    """
    Get the contents of all sheets in an Excel file.
     Args:
        xl_file (str): File path of the Excel file.
     Returns:
        dict: Dictionary where keys are sheet names and values are the contents of each sheet as a list of tuples.
     Functionality:
        - Create an ExcelWorkbook object using the xl_file.
        - Retrieve the sheet names from the ExcelWorkbook object.
        - Read the contents of each sheet and store them in a dictionary.
     Overview:
        This function allows you to retrieve the contents of all sheets in an Excel file and store them in a dictionary.
    """
    xl = ExcelWorkbook(xl_file)

    sheet_names = xl.sheet_names

    return {sheet_name: tuple(xl.read_sheet(sheet_name)) for sheet_name in sheet_names}


def write_to_sheet(df, workbook_path, sheet_name):
    """
    Write a pandas DataFrame to a specified sheet in an Excel file.
     Args:
        df (pandas.DataFrame): DataFrame to be written to the Excel file.
        workbook_path (str): File path of the Excel file.
        sheet_name (str): Name of the sheet to write the DataFrame to.
     Returns:
        None
     Functionality:
        - Checks if the Excel file specified by workbook_path exists.
        - If the file does not exist, writes the DataFrame to a new Excel file with the specified sheet_name.
        - If the file exists, opens the file using the load_workbook function from the openpyxl library.
        - Creates a writer object using pd.ExcelWriter with the existing workbook.
        - Checks if the sheet_name already exists in the workbook, if it does, appends a number to the sheet_name to make it unique.
        - Writes the DataFrame to the specified sheet_name in the workbook.
        - Saves and closes the writer and workbook objects.
        - Ignores warnings during the process.
     Overview:
        This function provides a convenient way to write a pandas DataFrame to a specified sheet in an Excel file. 
        It checks if the file already exists and handles the case where the sheet_name already exists in the file by appending a number to make it unique. 
        The function uses the openpyxl library to load and manipulate the Excel file, and the pd.ExcelWriter class to write the DataFrame to the file.
    """
    if not os.path.exists(workbook_path):
        df.to_excel(
            workbook_path, sheet_name=sheet_name, 
            index=False, freeze_panes=(1,0), header=True)
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
            writer, sheet_name=sheet_name, index=False, freeze_panes=(1,0), header=True)

        writer.save()
        writer.close()
        book.close()
        warnings.simplefilter("default")
