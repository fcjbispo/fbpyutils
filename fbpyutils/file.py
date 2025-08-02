"""
Functions to read and/or processes files and directories on the operating system.
"""

import os
import sys
import platform
import json
import datetime
from datetime import datetime
from pathlib import Path
from typing import Dict, Union
import base64
import mimetypes
import requests

from fbpyutils import get_logger
from fbpyutils.process import Process
from fbpyutils.image import get_image_info

_logger = get_logger()

def find(
    x: str, mask: str = "*.*", recurse: bool = True, parallel: bool = False
) -> list:
    """
    Finds files in a source folder using a specific mask, with options for recursive and parallel search.

    Parameters:
        x (str): The source folder to find and list files from.
        mask (str): The mask to be used when finding files. Default is '*.*'.
        recurse (bool): If True, the search will be recursive. If False, it will only search the top-level directory. Default is True.
        parallel (bool): If True and recurse is also True, the search will be performed in parallel. Default is False.

    Returns:
        list: A sorted list containing the full paths of unique files found.

    Examples:
        >>> find('/path/to/folder', '*.txt')
        ['/path/to/folder/file1.txt', '/path/to/folder/subfolder/file2.txt']
        >>> find('/path/to/another/folder', recurse=False)
        ['/path/to/another/folder/file3.txt', '/path/to/another/folder/file4.jpg']
    """
    _logger.debug(
        f"Starting find in folder: {x} with mask: {mask}, recurse: {recurse}, parallel: {parallel}"
    )

    source_path = Path(x)
    if not source_path.is_dir():
        _logger.warning(f"Source folder not found or is not a directory: {x}")
        return []

    found_files = set()

    if parallel and recurse:
        # Parallel search
        subdirectories = [str(d) for d in source_path.iterdir() if d.is_dir()]
        subdirectories.append(str(source_path))  # Include the root directory itself

        def search_worker(directory: str, search_mask: str):
            """Worker function to search for files in a directory."""
            try:
                path = Path(directory)
                files = {str(p) for p in path.rglob(search_mask) if p.is_file()}
                return True, None, list(files)
            except Exception as e:
                return False, str(e), []

        process_runner = Process(process=search_worker, parallelize=True)
        params = [(d, mask) for d in subdirectories]
        results = process_runner.run(params)

        for success, error, files in results:
            if success and files:
                found_files.update(files)
            elif error:
                _logger.error(f"Error in parallel search worker: {error}")

    else:
        # Sequential search
        if recurse:
            search_method = source_path.rglob
        else:
            search_method = source_path.glob

        found_files.update(str(p) for p in search_method(mask) if p.is_file())

    sorted_files = sorted(list(found_files))
    _logger.debug(f"Found {len(sorted_files)} files.")
    return sorted_files


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
    _logger.debug(f"Attempting to get creation date for file: {x}")
    t = None
    try:
        if platform.system() == "Windows":
            t = os.path.getctime(x)
            _logger.debug(f"Using ctime for Windows: {t}")
        else:
            stat = os.stat(x)
            try:
                t = stat.st_birthtime
                _logger.debug(f"Using st_birthtime for non-Windows: {t}")
            except AttributeError:
                _logger.warning(
                    "st_birthtime not available, falling back to st_mtime."
                )
                t = stat.st_mtime
                _logger.debug(f"Using st_mtime for non-Windows: {t}")
    except FileNotFoundError:
        _logger.error(f"File not found when getting creation date: {x}")
        raise
    except Exception as e:
        _logger.error(
            f"An error occurred while getting creation date for {x}: {e}"
        )
        raise

    result = datetime.fromtimestamp(t)
    _logger.debug(f"Creation date for {x}: {result}")
    return result


def load_from_json(x: str, encoding="utf-8") -> Dict:
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
    _logger.debug(f"Loading JSON from file: {x} with encoding: {encoding}")
    try:
        with open(x, "r", encoding=encoding) as f:
            data = json.load(f)
        _logger.debug(f"Successfully loaded JSON from {x}")
        return data
    except FileNotFoundError:
        _logger.error(f"JSON file not found: {x}")
        raise
    except json.JSONDecodeError as e:
        _logger.error(f"Error decoding JSON from {x}: {e}")
        raise
    except Exception as e:
        _logger.error(
            f"An unexpected error occurred while loading JSON from {x}: {e}"
        )
        raise


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
    _logger.debug(f"Writing JSON to file: {path_to_file}, prettify: {prettify}")
    try:
        with open(path_to_file, "w") as outputfile:
            if prettify:
                json.dump(x, outputfile, indent=4, sort_keys=True, ensure_ascii=False)
            else:
                json.dump(x, outputfile, ensure_ascii=False)
        _logger.debug(f"Successfully wrote JSON to {path_to_file}")
    except IOError as e:
        _logger.error(f"Error writing JSON to file {path_to_file}: {e}")
        raise
    except Exception as e:
        _logger.error(
            f"An unexpected error occurred while writing JSON to {path_to_file}: {e}"
        )
        raise


def contents(x: str) -> bytearray:
    """
    Reads a file and returns its contents as a byte array.

    Note:
        This function loads the entire file into memory. For very large files,
        consider using a streaming approach to avoid high memory consumption.

    Parameters:
        x (str): The path of the file to be read.

    Returns:
        bytearray: The contents of the file as a byte array.

    Example:
        >>> contents('/path/to/file.txt')
        bytearray(b'This is the file contents.')
    """
    _logger.debug(f"Reading contents of file: {x}")
    fileName = x
    fileContent = None

    try:
        with open(fileName, mode="rb") as file:
            fileContent = file.read()
        _logger.debug(f"Successfully read contents from {x}")
        return fileContent
    except FileNotFoundError:
        _logger.error(f"File not found when reading contents: {x}")
        raise
    except IOError as e:
        _logger.error(f"Error reading contents from file {x}: {e}")
        raise
    except Exception as e:
        _logger.error(
            f"An unexpected error occurred while reading contents from {x}: {e}"
        )
        raise


def mime_type(x: str) -> str:
    """
    Guesses the mime type of a file based on its extension.

    Parameters:
        x (str): The path of the file to get its mime type.

    Returns:
        str: The guessed mime type of the file, or 'application/octet-stream' if the type
             cannot be determined. Returns 'directory' if the path is a directory,
             and 'file_not_found' if the path does not exist.

    Example:
        >>> mime_type('/path/to/file.txt')
        'text/plain'
        >>> mime_type('/path/to/unknown.xyz')
        'application/octet-stream'
    """
    _logger.debug(f"Attempting to guess mime type for: {x}")

    if not os.path.exists(x):
        _logger.error(f"File not found: '{x}'.")
        return "file_not_found"

    if os.path.isdir(x):
        _logger.warning(f"Path '{x}' is a directory.")
        return "directory"

    try:
        mime_type_detected, _ = mimetypes.guess_type(x)
        if mime_type_detected:
            _logger.debug(f"Detected mime type for '{x}': {mime_type_detected}")
            return mime_type_detected
        else:
            _logger.warning(
                f"Could not guess mime type for '{x}'. Defaulting to 'application/octet-stream'."
            )
            return "application/octet-stream"
    except Exception as e:
        _logger.error(
            f"An unexpected error occurred while guessing mime type for '{x}': {e}"
        )
        raise


def _is_windows() -> bool:
    """
    Returns whether the code is running on the Windows operating system.
     Returns:
        bool: True if the current operating system is Windows, False otherwise.
     Example:
        >>> _is_windows()
        True
    """
    return sys.platform.upper().startswith("WIN")


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
    _logger.debug(
        f"Building platform path with winroot: {winroot}, otherroot: {otherroot}, pathparts: {pathparts}"
    )
    winroot = winroot.rstrip(os.path.sep)  # Remove trailing separator from winroot
    result = os.path.sep.join(
        [(winroot.rstrip(os.path.sep) if _is_windows() else otherroot), *pathparts]
    )
    _logger.debug(f"Built platform path: {result}")
    return result


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
    _logger.debug(f"Getting absolute path for: {x}")
    x = x or __file__
    result = os.path.sep.join(os.path.realpath(x).split(os.path.sep)[:-1])
    _logger.debug(f"Absolute path for {x}: {result}")
    return result


def describe_file(file_path: str) -> Dict:
    """
    Describes a file, returning a dictionary with its properties.

    Note:
        This function reads the entire file into memory to calculate hashes,
        which may cause performance issues with very large files.

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
    _logger.debug(f"Describing file: {file_path}")
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
        # Text files
        "text/plain": "Text file",
        "text/html": "HTML document",
        "text/css": "CSS stylesheet",
        "text/javascript": "JavaScript file",
        "text/csv": "CSV file",
        "text/xml": "XML document",
        "text/markdown": "Markdown file",
        # Documents
        "application/pdf": "PDF document",
        "application/msword": "Word document",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word document (DOCX)",
        "application/vnd.ms-excel": "Excel spreadsheet",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel spreadsheet (XLSX)",
        "application/vnd.ms-powerpoint": "PowerPoint presentation",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint presentation (PPTX)",
        "application/rtf": "Rich Text Format document",
        "application/vnd.oasis.opendocument.text": "OpenDocument text",
        "application/vnd.oasis.opendocument.spreadsheet": "OpenDocument spreadsheet",
        "application/vnd.oasis.opendocument.presentation": "OpenDocument presentation",
        # Data formats
        "application/json": "JSON file",
        "application/xml": "XML document",
        "application/yaml": "YAML file",
        "application/x-yaml": "YAML file",
        "text/yaml": "YAML file",
        # Images
        "image/jpeg": "JPEG image",
        "image/jpg": "JPEG image",
        "image/png": "PNG image",
        "image/gif": "GIF image",
        "image/bmp": "BMP image",
        "image/tiff": "TIFF image",
        "image/webp": "WebP image",
        "image/svg+xml": "SVG image",
        "image/x-icon": "Icon file",
        # Audio
        "audio/mpeg": "MP3 audio",
        "audio/wav": "WAV audio",
        "audio/ogg": "OGG audio",
        "audio/aac": "AAC audio",
        "audio/flac": "FLAC audio",
        "audio/x-m4a": "M4A audio",
        # Video
        "video/mp4": "MP4 video",
        "video/avi": "AVI video",
        "video/quicktime": "QuickTime video",
        "video/x-msvideo": "AVI video",
        "video/webm": "WebM video",
        "video/x-flv": "FLV video",
        "video/3gpp": "3GP video",
        # Archives
        "application/zip": "ZIP archive",
        "application/x-zip-compressed": "ZIP archive",
        "application/x-rar-compressed": "RAR archive",
        "application/x-7z-compressed": "7Z archive",
        "application/x-tar": "TAR archive",
        "application/gzip": "GZIP archive",
        "application/x-bzip2": "BZIP2 archive",
        # Executables
        "application/x-msdownload": "Windows executable",
        "application/x-executable": "Executable file",
        "application/x-msdos-program": "DOS executable",
        "application/vnd.microsoft.portable-executable": "Windows executable",
        "application/x-apple-diskimage": "Mac disk image",
        "application/vnd.debian.binary-package": "Debian package",
        "application/x-rpm": "RPM package",
        # Fonts
        "font/ttf": "TrueType font",
        "font/otf": "OpenType font",
        "font/woff": "WOFF font",
        "font/woff2": "WOFF2 font",
        "application/font-woff": "WOFF font",
        "application/font-woff2": "WOFF2 font",
        # Web files
        "application/javascript": "JavaScript file",
        "application/x-javascript": "JavaScript file",
        "text/x-php": "PHP file",
        "application/x-httpd-php": "PHP file",
        "application/x-python-code": "Python file",
        "text/x-python": "Python file",
        "text/x-java-source": "Java source file",
        "text/x-c": "C source file",
        "text/x-c++": "C++ source file",
        # Others
        "application/octet-stream": "Binary file",
        "application/x-binary": "Binary file",
        "inode/x-empty": "Empty file",
        "application/x-iso9660-image": "ISO image",
        "application/vnd.sqlite3": "SQLite database",
        "application/x-font-ttf": "TrueType font",
        "application/postscript": "PostScript document",
        "application/eps": "EPS document",
        "application/x-shockwave-flash": "Flash file",
        "application/vnd.adobe.flash.movie": "Flash movie",
        "application/x-bittorrent": "BitTorrent file",
        "message/rfc822": "Email message",
        "application/mbox": "Email mailbox",
        "application/pkcs7-mime": "S/MIME message",
        "application/x-x509-ca-cert": "X.509 certificate",
        "application/x-pkcs12": "PKCS#12 certificate",
        "application/pgp-keys": "PGP key",
        "application/pgp-signature": "PGP signature",
    }
    mime_type_description = mime_type_map.get(mime_type_code, "Other")

    file_content = contents(file_path)

    # SHA256 hash of the first 256 bytes
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_content[:256])
    first_256_bytes_sha256_hex = sha256_hash.hexdigest()

    # MD5 hash of the entire file
    md5_hash = hashlib.md5()
    md5_hash.update(file_content)
    md5sum = md5_hash.hexdigest()

    result = {
        "complete_filename": complete_filename,
        "filename_no_ext": filename_no_ext,
        "extension": extension,
        "size_bytes": size_bytes,
        "creation_date": created_at.isoformat(),
        "mime_type_code": mime_type_code,
        "mime_type_description": mime_type_description,
        "first_256_bytes_sha256_hex": first_256_bytes_sha256_hex,
        "md5sum": md5sum,
    }

    # Adding image info for image files
    if "image" in mime_type_code:
        _logger.debug(f"Adding image info for image file: {file_path}")
        result["image_info"] = get_image_info(file_path)

    _logger.debug(f"Finished describing file: {file_path}")
    return result


def get_file_head_content(
    file_path: str,
    num_bytes: int = 256,
    output_format: str = "text",
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Union[str, bytes, None]:
    """
    Reads the first `num_bytes` of a file and returns its content in the specified format.

    Note:
        This function is memory-efficient as it only reads the specified number of bytes
        from the beginning of the file without loading the entire file into memory.

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
    _logger.debug(
        f"Getting file head content for: {file_path}, num_bytes: {num_bytes}, output_format: {output_format}"
    )
    if not os.path.exists(file_path):
        _logger.warning(f"File not found: {file_path}. Returning None.")
        return None

    try:
        with open(file_path, "rb") as f:
            head_bytes = f.read(num_bytes)

        if output_format == "text":
            return head_bytes.decode(encoding, errors=errors)
        elif output_format == "bytes":
            return head_bytes
        elif output_format == "base64":
            return base64.b64encode(head_bytes).decode("ascii")
        else:
            return None  # Invalid output_format
    except IOError as e:
        _logger.error(f"IOError reading file head content from {file_path}: {e}")
        return None
    except Exception as e:
        _logger.error(
            f"An unexpected error occurred while getting file head content from {file_path}: {e}"
        )
        return None


def get_base64_data_from(file_uri: str, timeout: int = 300) -> str:
    """
    Retrieves data from a file URI (local path, remote URL, or base64 string)
    and returns it as a base64 encoded string.

    Note:
        When fetching from a URL or reading a local file, this function loads
        the entire file content into memory. Be cautious with very large files.

    This function handles three types of file URIs:
    1.  A local file path: It reads the file, encodes its content to base64, and returns the result.
    2.  A remote URL (starting with 'http://' or 'https://'): It downloads the content from the URL,
        encodes it to base64, and returns the result.
    3.  A base64 encoded string: It validates if the string is a valid base64 string and returns it.

    Parameters:
        file_uri (str): The URI of the file to process. Can be a local path, a URL, or a base64 string.
        timeout (int): The timeout in seconds for the request if the URI is a URL. Defaults to 300.

    Returns:
        str: The base64 encoded data as a string, or an empty string if an error occurs
             or the input is invalid.
    """
    _logger.debug(f"Getting base64 data from: {file_uri}")

    # Check if the data file is a local file
    if os.path.exists(file_uri):
        _logger.info(f"'{file_uri}' is a local file. Reading content.")
        try:
            with open(file_uri, "rb") as f:
                file_bytes = f.read()
            base64_data = base64.b64encode(file_bytes).decode("utf-8")
            _logger.debug("Successfully encoded local file to base64.")
            return base64_data
        except IOError as e:
            _logger.error(f"Error reading local file '{file_uri}': {e}")
            return ""
        except Exception as e:
            _logger.error(
                f"An unexpected error occurred while processing local file '{file_uri}': {e}"
            )
            return ""

    # If the data_file is a remote URL
    elif file_uri.startswith("http://") or file_uri.startswith("https://"):
        _logger.info(f"'{file_uri}' is a remote URL. Downloading content.")
        try:
            response = requests.get(file_uri, timeout=timeout)
            response.raise_for_status()  # Raise an exception for bad status codes
            image_bytes = response.content
            base64_data = base64.b64encode(image_bytes).decode("utf-8")
            _logger.debug(
                "Successfully downloaded and encoded remote file to base64."
            )
            return base64_data
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error downloading the file from '{file_uri}': {e}")
            return ""
        except Exception as e:
            _logger.error(
                f"An unexpected error occurred while processing remote file '{file_uri}': {e}"
            )
            return ""

    # Assume the content is already in base64 and validate it
    else:
        _logger.info("Assuming the input is a base64 string. Validating.")
        try:
            # Add padding if it's missing
            missing_padding = len(file_uri) % 4
            if missing_padding:
                file_uri += "=" * (4 - missing_padding)

            # Validate by decoding
            base64.b64decode(file_uri, validate=True)
            _logger.debug("Input string is a valid base64 string.")
            return file_uri
        except (base64.binascii.Error, ValueError) as e:
            _logger.error(f"Invalid base64 string provided: {e}")
            return ""
        except Exception as e:
            _logger.error(
                f"An unexpected error occurred during base64 validation: {e}"
            )
            return ""
