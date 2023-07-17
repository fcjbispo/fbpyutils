'''
Functions to read and/or processes files and directories on the operating system.
'''
import os
import sys
import platform
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

if platform.system() == 'Windows':
    from winmagic import magic
else:
    import magic


def find(x: str, mask: str = '*.*') -> list:
    '''
    Finds recursively for files in a source folder using specific mask
    Based on the code:
        https://stackoverflow.com/questions/2186525/how-to-use-glob-to-find-files-recursively

        x
            The source folder to find and list out
        mask
            The mask to be used when find files. Default = *.*

        Return a list with the full path of files found recursivelly in source
        folder using the specified mask
    '''
    all_files = [str(filename)
                 for filename in Path(x).rglob(mask)]

    return all_files


def creation_date(x: str) -> datetime:
    '''
    Try to get the datetime that a file was created, falling back to when it
    was last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.

        x
            The path for the file which creation date is desired

        Return the creation datetime for the file
    '''
    if platform.system() == 'Windows':
        t = os.path.getctime(x)
    else:
        stat = os.stat(x)
        try:
            t = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            t = stat.st_mtime

    return datetime.fromtimestamp(t)


def load_from_json(x: str, encoding='utf-8') -> Dict:
    '''
    Load data from JSON file and return a dict.

        x
            The path for the file which will be read

        Return a dictionary with data from JSON file
    '''
    return json.load(open(x, 'r', encoding=encoding))


def write_to_json(x: Dict, path_to_file: str, prettify=True):
    '''
    Write data from dictionary to JSON.

        x
            The dict to be written to file
        path_to_file
            The path for the file which will be written

    '''
    with open(path_to_file, 'w') as outputfile:
        if prettify:
            json.dump(
                x, outputfile,
                indent=4, sort_keys=True,
                ensure_ascii=False)
        else:
            json.dump(
                x, outputfile,
                ensure_ascii=False)


def contents(x: str) -> bytearray:
    '''
    Reads a file and returns its contents as an array of bytes.

        x
            The path for the file to be read

        Return the file contets as an array of bytes
    '''
    fileName = x
    fileContent = None

    with open(fileName, mode='rb') as file:
        fileContent = file.read()
        file.close()

    return fileContent


def mime_type(x: str) -> str:
    '''
    Returns the mime type of a file.

        x
            The path for the file to get its mime type

        Return the mime type of the file passed
    '''
    file_path = x

    try:
        return magic.from_file(
            file_path, mime=True)
    except IsADirectoryError:
        return 'directory'
    except FileNotFoundError:
        return 'file_not_found'


def _is_windows() -> bool:
    '''
    Returns if the code is running on Windows OS.

        True if current os is Windows or False otherwise
    '''
    return sys.platform.upper().startswith('WIN')


def build_platform_path(winroot: str, otherroot: str, pathparts: list) -> str:
    '''
    Build a path for specific file according operating system.

        winroot
            The root path for windows operating systems

        otherroot
            The root path for other operating systems

        pathparts
            The elements to build the path. The last element shoud be the file

        Return the path for the file according the operating system
    '''
    return os.path.sep.join([(winroot if _is_windows() else otherroot), *pathparts])


def absolute_path(x: str):
    '''
    Return the absolute path for the file x.

        x
            The file full name to have the absolute path extracted


        Return the absolute path for the given file
    '''
    x = x or __file__
    return os.path.sep.join(os.path.realpath(x).split(os.path.sep)[:-1])