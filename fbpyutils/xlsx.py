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
    def __init__(self, xl_file):
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


def get_sheet_names(xl_file):
    xl = ExcelWorkbook(xl_file)
    return xl.sheet_names


def get_sheet_by_name(xl_file, sheet_name):
    xl = ExcelWorkbook(xl_file)
    return xl.read_sheet(sheet_name)


def get_all_sheets(xl_file):
    xl = ExcelWorkbook(xl_file)
    sheet_names = xl.sheet_names
    return {sheet_name: tuple(xl.read_sheet(sheet_name)) for sheet_name in sheet_names}


def write_to_sheet(df, workbook_path, sheet_name):
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
