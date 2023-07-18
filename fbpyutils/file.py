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
    """
    Finds files recursively in a source folder using a specific mask.
     Parameters:
        x (str): The source folder to find and list files from.
        mask (str): The mask to be used when finding files. Default is '*.*'.
     Returns:
        list: A list containing the full paths of files found recursively in the source folder using the specified mask.
     Examples:
        >>> find('/path/to/folder', '*.txt')
        ['/path/to/folder/file1.txt', '/path/to/folder/subfolder/file2.txt']
        >>> find('/path/to/another/folder')
        ['/path/to/another/folder/file3.txt', '/path/to/another/folder/file4.jpg']
    """
    all_files = [str(filename)
                 for filename in Path(x).rglob(mask)]

    return all_files


def creation_date(x: str) -> datetime:
    """
    Tries to retrieve the datetime when a file was created, falling back to when it was last modified if that information is not available.
    See http://stackoverflow.com/a/39501288/1709587 for more details.
     Parameters:
        x (str): The path of the file for which the creation date is desired.
     Returns:
        datetime: The creation datetime for the file.
     Example:
        >>> creation_date('/path/to/file.txt')
        datetime.datetime(2022, 1, 1, 10, 30, 15)
    """
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
    """
    Loads data from a JSON file and returns it as a dictionary.
     Parameters:
        x (str): The path of the file to be read.
        encoding (str): The encoding of the file. Default is 'utf-8'.
     Returns:
        Dict: A dictionary containing the data from the JSON file.
     Example:
        >>> load_from_json('/path/to/file.json')
        {'key1': 'value1', 'key2': 'value2'}
    """
    return json.load(open(x, 'r', encoding=encoding))


def write_to_json(x: Dict, path_to_file: str, prettify=True):
    """
    Writes data from a dictionary to a JSON file.
     Parameters:
        x (Dict): The dictionary to be written to the file.
        path_to_file (str): The path of the file to be written.
        prettify (bool): Flag indicating whether the JSON output should be prettified. Default is True.
     Returns:
        None
     Example:
        >>> data = {'key1': 'value1', 'key2': 'value2'}
        >>> write_to_json(data, '/path/to/file.json', prettify=True)
    """
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
    """
    Reads a file and returns its contents as an array of bytes.
     Parameters:
        x (str): The path of the file to be read.
     Returns:
        bytearray: The contents of the file as an array of bytes.
     Example:
        >>> contents('/path/to/file.txt')
        bytearray(b'This is the file contents.')
    """
    fileName = x
    fileContent = None

    with open(fileName, mode='rb') as file:
        fileContent = file.read()
        file.close()

    return fileContent


def mime_type(x: str) -> str:
    """
    Returns the mime type of a file.
     Parameters:
        x (str): The path of the file to get its mime type.
     Returns:
        str: The mime type of the file passed.
     Example:
        >>> mime_type('/path/to/file.txt')
        'text/plain'
    """
    file_path = x

    try:
        return magic.from_file(
            file_path, mime=True)
    except IsADirectoryError:
        return 'directory'
    except FileNotFoundError:
        return 'file_not_found'


def _is_windows() -> bool:
    """
    Returns whether the code is running on the Windows operating system.
     Returns:
        bool: True if the current operating system is Windows, False otherwise.
     Example:
        >>> _is_windows()
        True
    """
    return sys.platform.upper().startswith('WIN')


def build_platform_path(winroot: str, otherroot: str, pathparts: list) -> str:
    """
    Builds a path for a specific file according to the operating system.
     Parameters:
        winroot (str): The root path for Windows operating systems.
        otherroot (str): The root path for other operating systems.
        pathparts (list): The elements to build the path. The last element should be the file.
     Returns:
        str: The path for the file according to the operating system.
     Example:
        >>> build_platform_path('C:\\', '/root/', ['folder', 'subfolder', 'file.txt'])
        'C:\\folder\\subfolder\\file.txt'
    """
    return os.path.sep.join([(winroot if _is_windows() else otherroot), *pathparts])


def absolute_path(x: str):
    """
    Returns the absolute path for the file x.
     Parameters:
        x (str): The full name of the file to extract the absolute path from.
     Returns:
        str: The absolute path for the given file.
     Example:
        >>> absolute_path('file.txt')
        '/path/to/file.txt'
    """
    x = x or __file__
    return os.path.sep.join(os.path.realpath(x).split(os.path.sep)[:-1])