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

from fbpyutils import logging

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
        logging.debug(f"Initializing ExcelWorkbook with file: {xl_file}")
        data = None

        if isinstance(xl_file, str):
            if os.path.exists(xl_file):
                try:
                    with open(xl_file, 'rb') as f:
                        data = f.read()
                    logging.info(f"Successfully read Excel file from path: {xl_file}")
                except (OSError, IOError) as e:
                    logging.error(f"Error reading the Excel file {xl_file}: {e}")
                    raise type(e)(f'Error reading the file {xl_file}: {e}')
            else:
                logging.error(f"Excel file not found: {xl_file}")
                raise FileNotFoundError(f'File {xl_file} does not exist.')
        elif isinstance(xl_file, bytes):
            data = xl_file
            logging.info("Received Excel file as bytes.")
        else:
            logging.error(f"Invalid file reference type: {type(xl_file)}. Must be a file path (str) or bytes.")
            raise TypeError('Invalid file reference. Must be a file path or array of bytes.')

        self.workbook = None
        self.sheet_names = None
        self.kind = XLSX

        try:
            xl_data = io.BytesIO(data)
            warnings.simplefilter("ignore") # Ignore warnings from openpyxl/xlrd
            self.workbook = openpyxl.open(xl_data, data_only=True)
            self.sheet_names = self.workbook.sheetnames
            logging.debug("Workbook opened successfully with openpyxl (XLSX format).")
        except Exception as e_xlsx: # Catch a broader exception for openpyxl to try xlrd
            logging.warning(f"Failed to open with openpyxl, trying xlrd. Error: {e_xlsx}")
            try:
                xl_data.seek(0) # Reset stream position for xlrd
                self.workbook = xlrd.open_workbook(file_contents=xl_data.read())
                self.sheet_names = self.workbook.sheet_names()
                self.kind = XLS
                logging.debug("Workbook opened successfully with xlrd (XLS format).")
            except Exception as e_xls:
                logging.critical(f"Failed to open workbook with both openpyxl and xlrd. XLSX error: {e_xlsx}, XLS error: {e_xls}")
                raise ValueError("Could not open workbook. Invalid file format or corrupted file.") from e_xls
        finally:
            warnings.simplefilter("default") # Restore default warning behavior
        logging.info("ExcelWorkbook initialized.")

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
        logging.debug(f"Reading sheet: {sheet_name}")

        if sheet_name not in self.sheet_names:
            logging.error(f"Invalid or nonexistent sheet name: {sheet_name}. Available sheets: {self.sheet_names}")
            raise NameError('Invalid/Nonexistent sheet.')

        try:
            if self.kind == XLSX:
                sh = self.workbook[sheet_name]
                rows = tuple(tuple(c.value for c in r) for r in sh.iter_rows())
            else: # XLS
                sh = self.workbook.sheet_by_name(sheet_name)
                rows = tuple(tuple(sh.cell_value(r, c) for c in range(sh.ncols)) for r in range(sh.nrows))
            logging.info(f"Successfully read sheet '{sheet_name}'. Rows read: {len(rows)}")
            return rows
        except Exception as e:
            logging.critical(f"Error reading sheet '{sheet_name}': {e}")
            raise

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
        logging.debug(f"Reading sheet by index: {index}")

        if not 0 <= index < len(self.sheet_names):
            logging.error(f"Invalid or nonexistent sheet index: {index}. Total sheets: {len(self.sheet_names)}")
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
def get_sheet_names(xl_file: Union[str, bytes]) -> list[str]:
    """
    Retrieves sheet names from an Excel file.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.

    Returns:
        list[str]: List of sheet names.
    """
    logging.debug(f"Getting sheet names for file: {xl_file}")
    try:
        xl = ExcelWorkbook(xl_file)
        logging.info(f"Retrieved sheet names: {xl.sheet_names}")
        return xl.sheet_names
    except Exception as e:
        logging.error(f"Error getting sheet names from {xl_file}: {e}")
        raise


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
    logging.debug(f"Getting sheet by name '{sheet_name}' from file: {xl_file}")
    try:
        xl = ExcelWorkbook(xl_file)
        sheet_content = xl.read_sheet(sheet_name)
        logging.info(f"Successfully retrieved sheet '{sheet_name}'.")
        return sheet_content
    except Exception as e:
        logging.error(f"Error getting sheet by name '{sheet_name}' from {xl_file}: {e}")
        raise


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
    logging.debug(f"Getting all sheets from file: {xl_file}")
    try:
        xl = ExcelWorkbook(xl_file)
        sheet_names = xl.sheet_names
        all_sheets_content = {
            sheet_name: tuple(xl.read_sheet(sheet_name)) for sheet_name in sheet_names
        }
        logging.info(f"Successfully retrieved all sheets from {xl_file}.")
        return all_sheets_content
    except Exception as e:
        logging.error(f"Error getting all sheets from {xl_file}: {e}")
        raise


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
    logging.debug(f"Writing DataFrame to Excel sheet '{sheet_name}' in workbook: {workbook_path}")
    try:
        if not os.path.exists(workbook_path):
            logging.info(f"Workbook does not exist, creating new file: {workbook_path}")
            df.to_excel(
                workbook_path,
                sheet_name=sheet_name,
                index=False,
                freeze_panes=(1, 0),
                header=True,
            )
            logging.info(f"Successfully created new workbook and wrote sheet '{sheet_name}'.")
        else:
            logging.info(f"Workbook exists, appending to: {workbook_path}")
            warnings.simplefilter("ignore") # Ignore warnings from openpyxl/xlrd
            try:
                with pd.ExcelWriter(workbook_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
                    # The 'if_sheet_exists' handles new sheet creation.
                    # Pandas >= 1.3.0 handles sheet name duplication by appending numbers if 'new' is used and name exists.
                    # For older pandas or more control, manual check might be needed, but 'new' should suffice.
                    # The logic for renaming (while loop) might be redundant with if_sheet_exists='new'
                    # but let's keep it for now to ensure unique names if 'new' doesn't behave as expected across all pandas versions.
                    
                    # Temporarily load book to check existing sheet names for custom renaming logic if needed.
                    # This is a bit redundant if if_sheet_exists='new' works perfectly.
                    temp_book = load_workbook(workbook_path)
                    current_sheet_names = temp_book.sheetnames
                    temp_book.close() # Close immediately after getting names

                    final_sheet_name = sheet_name
                    index = 0
                    while final_sheet_name in current_sheet_names:
                        index += 1
                        final_sheet_name = f"{sheet_name}{index}"
                    
                    logging.debug(f"Final sheet name determined: {final_sheet_name}")
                    df.to_excel(
                        writer,
                        sheet_name=final_sheet_name,
                        index=False,
                        freeze_panes=(1, 0),
                        header=True,
                    )
                logging.info(f"Successfully wrote DataFrame to sheet '{final_sheet_name}' in existing workbook.")
            except Exception as e:
                logging.error(f"Error writing to existing Excel workbook {workbook_path}: {e}")
                raise
            finally:
                warnings.simplefilter("default") # Restore default warning behavior
    except Exception as e:
        logging.critical(f"Critical error in write_to_sheet: {e}")
        raise
