'''
Functions to read and/or processes files and directories on the operating system.
'''
import os
import sys
import platform
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Union
import base64
import magic
import sys
from fbpyutils.logging import logger # Import the global logger


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
    # Use pathlib to ensure proper path handling, especially with special characters
    file_path_obj: Path = Path(x).resolve() # Resolve to get absolute path and normalize
    file_path_str = str(file_path_obj)
    logger.debug(f"Resolved file_path (string): {file_path_str}")

    try:
        if not os.path.isfile(file_path_str):
            logger.warning(f"Path '{file_path_str}' is not a file. Accepting as directory.")
            return 'directory'

        if sys.platform.startswith('win'):
            file_contents = contents(file_path_str)[0:256]
            mime_type_detected = magic.from_buffer(file_contents, mime=True)
            logger.debug(f"Detected mime type for '{file_path_str}' on Windows: {mime_type_detected}")
        else:
            mime_type_detected = magic.from_file(file_path_str, mime=True)
            logger.debug(f"Detected mime type for '{file_path_str}' on non-Windows: {mime_type_detected}")
        return mime_type_detected
    except IsADirectoryError:
        logger.warning(f"Path '{file_path_str}' is a directory, returning 'directory'.")
        return 'directory'
    except FileNotFoundError:
        logger.error(f"File not found: '{file_path_str}'. Returning 'file_not_found'.")
        return 'file_not_found'
    except Exception as e:
        logger.exception(f"An unexpected error occurred while getting mime type for '{file_path_str}'.")
        raise # Re-raise the exception for further handling if needed


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
    winroot = winroot.rstrip(os.path.sep) # Remove trailing separator from winroot
    return os.path.sep.join([(winroot.rstrip(os.path.sep) if _is_windows() else otherroot), *pathparts])


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


def describe_file(file_path: str) -> Dict:
    """
    Describes a file, returning a dictionary with its properties.
     Parameters:
        file_path (str): The path of the file to describe.
     Returns:
        Dict: A dictionary containing the file properties.
     Example:
        >>> describe_file('/path/to/file.txt')
        {
            'complete_filename': 'file.txt',
            'filename_no_ext': 'file',
            'extension': '.txt',
            'size_bytes': 1234,
            'creation_date': '2022-01-01T10:30:15',
            'mime_type_code': 'text/plain',
            'mime_type_description': 'Text file',
            'first_256_bytes_sha256_hex': '...',
            'md5sum': '...'
        }
    """
    # Import hashlib here to avoid circular dependencies if it's used elsewhere
    import hashlib

    complete_filename = os.path.basename(file_path)
    filename_no_ext, extension = os.path.splitext(complete_filename)
    size_bytes = os.path.getsize(file_path)
    # creation_date returns a naive datetime object.
    created_at = creation_date(file_path)
    mime_type_code = mime_type(file_path)

    # Basic MIME type mapping
    mime_type_map = {
        'text/plain': 'Text file',
        'application/pdf': 'PDF document',
        'application/json': 'JSON file',
        'image/jpeg': 'JPEG image',
        'image/png': 'PNG image',
        'application/zip': 'ZIP archive',
        # Add more mappings as needed
    }
    mime_type_description = mime_type_map.get(mime_type_code, 'Other')

    file_content = contents(file_path)

    # SHA256 hash of the first 256 bytes
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_content[:256])
    first_256_bytes_sha256_hex = sha256_hash.hexdigest()

    # MD5 hash of the entire file
    md5_hash = hashlib.md5()
    md5_hash.update(file_content)
    md5sum = md5_hash.hexdigest()

    return {
        'complete_filename': complete_filename,
        'filename_no_ext': filename_no_ext,
        'extension': extension,
        'size_bytes': size_bytes,
        'creation_date': created_at.isoformat(),
        'mime_type_code': mime_type_code,
        'mime_type_description': mime_type_description,
        'first_256_bytes_sha256_hex': first_256_bytes_sha256_hex,
        'md5sum': md5sum,
    }


def get_file_head_content(
    file_path: str,
    num_bytes: int = 256,
    output_format: str = 'text',
    encoding: str = 'utf-8',
    errors: str = 'replace'
) -> Union[str, bytes, None]:
    """
    Reads the first `num_bytes` of a file and returns its content in the specified format.

    Parameters:
        file_path (str): The path to the file.
        num_bytes (int): The number of bytes to read from the beginning of the file. Defaults to 256.
        output_format (str): The desired output format. Can be 'text', 'bytes', or 'base64'.
                             Defaults to 'text'.
        encoding (str): The encoding to use if output_format is 'text'. Defaults to 'utf-8'.
        errors (str): The error handling scheme to use for decoding if output_format is 'text'.
                      Defaults to 'replace'.

    Returns:
        Union[str, bytes, None]: The content of the head of the file in the specified format,
                                 or None if the file does not exist, an error occurs,
                                 or the output_format is invalid.
    """
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'rb') as f:
            head_bytes = f.read(num_bytes)

        if output_format == 'text':
            return head_bytes.decode(encoding, errors=errors)
        elif output_format == 'bytes':
            return head_bytes
        elif output_format == 'base64':
            return base64.b64encode(head_bytes).decode('ascii')
        else:
            return None # Invalid output_format
    except IOError:
        return None
