'''
Functions to read and MS Excel Spreadsheet files in xls or xlsx formats.
'''
import os
import io
from click.termui import prompt
import openpyxl, xlrd
import csv
import json
import click

from datetime import datetime, date
import pandas as pd
import numpy as np

from typing import Union


XLS, XLSX = 0, 1


class ExcelWorkbook:
    def __init__(self, xl_file: Union[str, bytes]):
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
                raise NameError(f'File {xl_file} does not exists.')
        elif type(xl_file) == bytes:
            data = xl_file
        else:
            raise TypeError('Invalid file reference. Must be a file path or array of bytes.')
        
        self.workbook = None
        self.sheet_names = None 
        self.kind = XLSX

        try:
            xl_data = io.BytesIO(data)
            self.workbook = openpyxl.open(xl_data, data_only=True)
            self.sheet_names = self.workbook.sheetnames
        except OSError:
            xl_data.seek(0)
            self.workbook = xlrd.open_workbook(file_contents=xl_data.read())
            self.sheet_names = self.workbook.sheet_names()
            self.kind = XLS
        except Exception as e:
            print(f"Unexpected error: {e}")

    def read_sheet(self, sheet_name=None):
        sheet_name = sheet_name or self.sheet_names.get(sheet_name)
        if sheet_name not in self.sheet_names:
            raise NameError('Invalid/Non existent sheet.')
        sh = self.workbook[sheet_name]
        return (
            tuple(c.value for c in r)
            for r in (sh.iter_rows() if self.kind == XLSX else sh.get_rows())
        )
    
    def read_sheet_by_index(self, index=None):
        index = index or 0
        if index < 0 or index >= len(self.sheet_names):
            raise NameError('Invalid/Non existent sheet.')
        return self.read_sheet(self.sheet_names[index])

def get_sheet_names(xl_file: str) -> list:
    pass
