# fbpyutils Documentation

[![PyPI Version](https://img.shields.io/pypi/v/fbpyutils.svg)](https://pypi.org/project/fbpyutils/)
[![License](https://img.shields.io/pypi/l/MIT.svg)](https://opensource.org/licenses/MIT)

## Overview

Francisco Bispo's Utilities for Python. This library provides a collection of utility functions for Python, including modules for:

- `calendar`: Functions to manipulate calendars.
- `datetime`: Utility functions to manipulate date and time.
- `debug`: Functions to support code debugging.
- `file`: Functions to read and/or process files and directories on the operating system.
- `logging`: Global logging system for the library. See Initialization section.
- `ofx`: Reads and processes OFX (Open Financial Exchange) files and data.
- `string`: Several functions to manipulate and process strings and/or produce strings from any kind of data.
- `xlsx`: Functions to read and MS Excel Spreadsheet files in xls or xlsx formats.

## Installation

```bash
pip install fbpyutils
```

## Usage

### Initialization and Configuration

The `fbpyutils` library must be initialized before use. This is done via the `setup()` function.

#### `setup(config: Optional[Union[Dict[str, Any], str]] = None)`
Initializes the global environment and logging system. This function should be called once when your application starts.

- **Args**:
    - `config`: Can be a dictionary containing configuration, a string path to a JSON configuration file, or `None` to use the default `app.json`.

#### `get_env() -> Env`
Returns the singleton `Env` instance after setup.

#### `get_logger() -> Logger`
Returns the singleton `Logger` instance after setup.

---

### calendar Module

#### Functions

##### `add_markers`

```python
def add_markers(x: List, reference_date: date = datetime.now().date()) -> List:
    '''
    Adds markers to past months from the reference date.
     Parameters:
        x (List): The calendar dict used to add markers.
        reference_date (date): The date used to calculate the markers. Defaults to the current date.
     Returns:
        List: The calendar with added markers. The markers indicate the number of months past from the reference date:
            - today (bool): True if the calendar date and the current date are the same.
            - current_year (bool): True if the calendar date's year is the current year.
            - last_day_of_month (bool): True if the calendar date is the last date of its month.
            - last_day_of_quarter (bool): True if the calendar date is the last date of its quarter.
            - last_day_of_half (bool): True if the calendar date is the last date of its half.
            - last_day_of_year (bool): True if the calendar date is the last date of its year.
            - last_24_months (bool): True if the calendar date is within the last 24 months from the current date.
            - last_12_months (bool): True if the calendar date is within the last 12 months from the current date.
            - last_6_months (bool): True if the calendar date is within the last 6 months from the current date.
            - last_3_months (bool): True if the calendar date is within the last 3 months from the current date.
    '''
```

##### `calendarize`

```python
def calendarize(x: DataFrame, date_column: str, with_markers: bool = False, reference_date: date = datetime.now().date()) -> DataFrame:
    '''
    Adds calendar columns to a dataframe.
     Parameters:
        x (DataFrame): The dataframe used to add calendar data.
        date_column (str): The datetime column used to build calendar data. Should be different from 'calendar_date'.
        with_markers (bool): Indicates whether to add calendar markers to the dataframe. Default is False.
        reference_date (date): The date used to calculate the markers. Defaults to the current date.
     Returns:
        DataFrame: A new dataframe with calendar columns and optional markers added to the passed dataframe.
    '''
```

##### `get_calendar`

```python
def get_calendar(x: date, y: date) -> List:
    '''
    Build a calendar to be used as a time dimension.
     Parameters:
        x (date): The initial date for the calendar.
        y (date): The final date for the calendar. Must be greater than the initial date.
     Returns:
        List: A calendar to be used as a time dimension with the following attributes:
            - date (date): The date.
            - date_time (datetime): The date and time.
            - year (int): The year.
            - half (int): The half of the year.
            - quarter (int): The quarter of the year.
            - month (int): The month.
            - day (int): The day.
            - week_day (int): The day of the week (Monday is 0 and Sunday is 6).
            - week_of_year (int): The week of the year.
            - date_iso (str): The date in ISO format.
            - date_str (str): The date in string format.
            - week_day_name (str): The name of the day of the week.
            - week_day_name_short (str): The short name of the day of the week.
            - week_month_name (str): The name of the month.
            - week_month_name_short (str): The short name of the month.
            - year_str (str): The year in string format.
            - year_half_str (str): The year and half of the year in string format.
            - year_quarter_str (str): The year and quarter of the year in string format.
            - year_month_str (str): The year and month in string format.
    '''
```

### datetime Module

#### Functions

##### `apply_timezone`

```python
def apply_timezone(x: datetime, tz: str) -> datetime:
    '''
    Apply the specified timezone to a datetime object.
     Parameters:
        x (datetime): The datetime to have the timezone applied.
        tz (str): The name of the timezone.
     Returns:
        datetime: The datetime object with the timezone information.
    '''
```

##### `delta`

```python
def delta(x: datetime, y: datetime, delta: str = 'months') -> int:
    '''
    Gets the time delta between two dates.
     Parameters:
        x (datetime): The last date.
        y (datetime): The first date. Must be greater than or equal to the last date.
        delta (str): The unit of time to return. Should be either 'months' for the number of
        months between both dates or 'years' for the number of years between both dates.
        Defaults to 'months'.
     Returns:
        int: The number of months or years between both dates.
    '''
```

##### `elapsed_time`

```python
def elapsed_time(x: datetime, y: datetime) -> tuple:
    '''
    Calculates and returns the elapsed time as a tuple (days, hours, minutes, seconds).
     Parameters:
        x (datetime): The last date.
        y (datetime): The first date. Must be greater than or equal to the last date.
     Returns:
        tuple: The elapsed time formatted as a tuple (days, hours, minutes, seconds).
    '''
```

### debug Module

#### Functions

##### `debug`

```python
def debug(func):
    '''
    Decorator function used to debug the execution of system functions.
    Prints all arguments used and the result value of the debugged functions.
     Usage:
     @debug
     def myFunc(x, y, z):
         pass
     Parameters:
        func: The function to be decorated.
     Returns:
        The function decorator.
    '''
```

##### `debug_info`

```python
def debug_info(x: Exception):
    '''
    Return extra exception/execution info for debug.
    '''
```

### file Module

#### Functions

##### `absolute_path`

```python
def absolute_path(x: str):
    '''
    Returns the absolute path for the file x.
     Parameters:
        x (str): The full name of the file to extract the absolute path from.
     Returns:
        str: The absolute path for the given file.
     Example:
        >>> absolute_path('file.txt')
        '/path/to/file.txt'
    '''
```

##### `build_platform_path`

```python
def build_platform_path(winroot: str, otherroot: str, pathparts: list) -> str:
    '''
    Builds a path for a specific file according to the operating system.
     Parameters:
        winroot (str): The root path for Windows operating systems.
        otherroot (str): The root path for other operating systems.
        pathparts (list): The elements to build the path. The last element should be the file.
     Returns:
        str: The path for the file according to the operating system.
     Example:
        >>> build_platform_path('C:\\\\', '/root/', ['folder', 'subfolder', 'file.txt'])
        'C:\\\\folder\\\\subfolder\\\\file.txt'
    '''
```

##### `contents`

```python
def contents(x: str) -> bytearray:
    '''
    Reads a file and returns its contents as an array of bytes.
     Parameters:
        x (str): The path of the file to be read.
     Returns:
        bytearray: The contents of the file as an array of bytes.
     Example:
        >>> contents('/path/to/file.txt')
        bytearray(b'This is the file contents.')
    '''
```

##### `creation_date`

```python
def creation_date(x: str) -> datetime:
    '''
    Tries to retrieve the datetime when a file was created, falling back to when it was last modified if that information is not available.
    See http://stackoverflow.com/a/39501288/1709587 for more details.
     Parameters:
        x (str): The path of the file for which the creation date is desired.
     Returns:
        datetime: The creation datetime for the file.
     Example:
        >>> creation_date('/path/to/file.txt')
        datetime.datetime(2022, 1, 1, 10, 30, 15)
    '''
```

##### `find`

```python
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
```

##### `load_from_json`

```python
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
```

##### `mime_type`

```python
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
```

##### `write_to_json`

```python
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
```

##### `_is_windows`

```python
def _is_windows() -> bool:
    """
    Returns whether the code is running on the Windows operating system.
     Returns:
        bool: True if the current operating system is Windows, False otherwise.
     Example:
        >>> _is_windows()
        True
    """
```

##### `describe_file`

```python
def describe_file(file_path: str) -> Dict:
    """
    Inspects a file and returns a dictionary containing its properties.
     Parameters:
        file_path (str): The path to the file.
     Returns:
        Dict: A dictionary with the following keys:
            - complete_filename (str): The full name of the file (e.g., "document.txt").
            - filename_no_ext (str): The filename without its extension (e.g., "document").
            - extension (str): The file extension (e.g., ".txt").
            - size_bytes (int): The size of the file in bytes.
            - creation_date (str): The creation date of the file in ISO 8601 format (e.g., "2023-10-27T10:30:00"). Note: This is a naive datetime.
            - mime_type_code (str): The detected MIME type code (e.g., "text/plain").
            - mime_type_description (str): A human-readable description of the MIME type (e.g., "Text file").
            - first_256_bytes_sha256_hex (str): The SHA256 hash (hexadecimal string) of the first 256 bytes of the file. If the file is smaller than 256 bytes, it hashes the entire content.
            - md5sum (str): The MD5 hash (hexadecimal string) of the entire file content.
     Example:
        >>> from fbpyutils.file import describe_file
        >>> file_info = describe_file("my_document.txt")
        >>> if file_info:
        >>>     print(f"Filename: {file_info['complete_filename']}")
        >>>     print(f"Size: {file_info['size_bytes']} bytes")
        >>>     print(f"MD5 Hash: {file_info['md5sum']}")
    """
```

##### `get_file_head_content`

```python
def get_file_head_content(file_path: str, num_bytes: int = 256, output_format: str = 'text', encoding: str = 'utf-8', errors: str = 'replace') -> Optional[Union[str, bytes]]:
    """
    Reads the first `num_bytes` of a file and returns its content in the specified format.
     Parameters:
        file_path (str): The path to the file.
        num_bytes (int): The number of bytes to read from the beginning of the file. Defaults to 256.
        output_format (str): The desired output format. Can be 'text', 'bytes', or 'base64'. Defaults to 'text'.
        encoding (str): The encoding to use if `output_format` is 'text'. Defaults to 'utf-8'.
        errors (str): The error handling scheme to use for decoding if `output_format` is 'text'. Defaults to 'replace'.
     Returns:
        Optional[Union[str, bytes]]: The content of the head of the file in the specified format (str, bytes, or None if an error occurs or format is invalid).
     Example:
        >>> from fbpyutils.file import get_file_head_content
        >>> # Get first 100 bytes as text
        >>> head_text = get_file_head_content("my_document.txt", num_bytes=100, output_format='text')
        >>> if head_text is not None:
        >>>     print(f"First 100 bytes (text): {head_text}")
        >>> # Get first 50 bytes as raw bytes
        >>> head_bytes = get_file_head_content("my_image.jpg", num_bytes=50, output_format='bytes')
        >>> if head_bytes is not None:
        >>>     print(f"First 50 bytes (raw): {head_bytes}")
        >>> # Get first 200 bytes as base64 string
        >>> head_base64 = get_file_head_content("my_archive.zip", num_bytes=200, output_format='base64')
        >>> if head_base64 is not None:
        >>>     print(f"First 200 bytes (base64): {head_base64}")
        >>> # Handle non-existent file
        >>> non_existent = get_file_head_content("non_existent_file.txt")
        >>> if non_existent is None:
        >>>     print("File not found or an error occurred.")
    """
```

### ofx Module

#### Functions

##### `format_date`

```python
def format_date(x: datetime, native: bool = True) -> Union[datetime, str]:
    """
    Formats a datetime for use in ofx data.
     Args:
        x (datetime): The datetime to be used.
        native (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Union[datetime, str]: The datetime formatted to be used in dict or string iso format.
            Example: "2020-03-10T03:00:00"
    """
```

##### `main`

```python
def main(argv):
    """
    Main function of the program.
     Parameters:
    - argv (list): A list of command-line arguments passed to the program.
     Returns:
    None
     Functionality:
    - Parses the command-line arguments using getopt.
    - If no arguments are provided or an invalid option is used, it prints a helper message and exits.
    - If the "--print" option is used, it sets the source_path variable to the provided argument.
    - If the source_path exists, it reads data from the file using the read_from_path function.
    - It then prints the data as a JSON string.
    - If an exception occurs during the process, it prints an error message indicating an invalid or corrupted file.
    - If the source_path does not exist, it prints a "File not found" message.
     Note:
    - The read_from_path function is not defined in the provided code snippet and should be implemented separately.
     Example Usage:
    $ python ofx.py --print myfile.ofx
     This will read the data from "myfile.ofx" and print it as a formatted JSON string.
    """
```

##### `read`

```python
def read(x: str, native_date: bool = True) -> Dict:
    """
    Reads ofx data into a dictionary.
     Args:
        x (str): The ofx data.
        native_date (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Dict: A dictionary with the ofx data.
    """
```

##### `read_from_path`

```python
def read_from_path(x: str, native_date: bool = True) -> Dict:
    """
    Reads ofx data from a file into a dictionary.
     Args:
        x (str): The ofx file path to be read.
        native_date (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Dict: A dictionary with the ofx data.
    """
```

### process Module

Provides classes for parallel or serial process execution with control mechanisms like timestamp-based file processing and session-based resumable processes.

#### Classes

##### `Process`

```python
class Process:
    """
    Base class for parallel or serial function processing.

    Attributes:
        _MAX_WORKERS: int
        _process: Callable
        _parallelize: bool
        _workers: int
        sleeptime: float
        _parallel_type: str
    """

    @staticmethod
    def get_available_cpu_count() -> int:
        """
        Determines the number of available CPU cores for processing.
        """

    @staticmethod
    def is_parallelizable(parallel_type: str = 'threads') -> bool:
        """
        Checks if the current system supports the specified parallel processing type.
        """

    @staticmethod
    def get_function_info(func: Callable) -> Dict[str, str]:
        """
        Gets detailed information about a function.
        """

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = _MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads') -> None:
        """
        Initializes a new Process instance.
        """

    def run(self, params: List[Tuple[Any, ...]]) -> List[Tuple[bool, Optional[str], Any]]:
        """
        Executes the processing function for each parameter set in the given list.
        """
```

##### `FileProcess`

```python
class FileProcess(Process):
    """
    Class for file processing with timestamp-based control to prevent reprocessing.
    """

    def __init__(self, process: Callable[..., ProcessingFilesFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0) -> None:
        """
        Initializes a new instance of FileProcess.
        """

    def run(self, params: List[Tuple[Any, ...]], controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes file processing for multiple files, optionally with timestamp control.
        """
```

##### `SessionProcess`

```python
class SessionProcess(Process):
    """
    Class for session-based process execution with resume capability.
    """

    @staticmethod
    def generate_session_id() -> str:
        """
        Generates a unique session ID with the prefix 'session_'.
        """

    @staticmethod
    def generate_task_id(params: Tuple[Any, ...]) -> str:
        """
        Generates a unique task ID based on the hash of the process parameters.
        """

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads') -> None:
        """
        Initializes a new instance of SessionProcess.
        """

    def run(self, params: List[Tuple[Any, ...]], session_id: Optional[str] = None, controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes processing for multiple parameter sets, optionally with session control.
        """
```


### process Module

Provides classes for parallel or serial process execution with control mechanisms like timestamp-based file processing and session-based resumable processes.

#### Classes

##### `Process`

```python
class Process:
    """
    Base class for parallel or serial function processing.
    
    Attributes:
        _MAX_WORKERS: int
        _process: Callable
        _parallelize: bool
        _workers: int
        sleeptime: float
        _parallel_type: str
    """

    @staticmethod
    def get_available_cpu_count() -> int:
        """
        Determines the number of available CPU cores for processing.
        """

    @staticmethod
    def is_parallelizable(parallel_type: str = 'threads') -> bool:
        """
        Checks if the current system supports the specified parallel processing type.
        """

    @staticmethod
    def get_function_info(func: Callable) -> Dict[str, str]:
        """
        Gets detailed information about a function.
        """

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = _MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads') -> None:
        """
        Initializes a new Process instance.
        """

    def run(self, params: List[Tuple[Any, ...]]) -> List[Tuple[bool, Optional[str], Any]]:
        """
        Executes the processing function for each parameter set in the given list.
        """
```

##### `FileProcess`

```python
class FileProcess(Process):
    """
    Class for file processing with timestamp-based control to prevent reprocessing.
    """

    def __init__(self, process: Callable[..., ProcessingFilesFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0) -> None:
        """
        Initializes a new instance of FileProcess.
        """

    def run(self, params: List[Tuple[Any, ...]], controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes file processing for multiple files, optionally with timestamp control.
        """
```

##### `SessionProcess`

```python
class SessionProcess(Process):
    """
    Class for session-based process execution with resume capability.
    """

    @staticmethod
    def generate_session_id() -> str:
        """
        Generates a unique session ID with the prefix 'session_'.
        """

    @staticmethod
    def generate_task_id(params: Tuple[Any, ...]) -> str:
        """
        Generates a unique task ID based on the hash of the process parameters.
        """

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads') -> None:
        """
        Initializes a new instance of SessionProcess.
        """

    def run(self, params: List[Tuple[Any, ...]], session_id: Optional[str] = None, controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes processing for multiple parameter sets, optionally with session control.
        """
```


### string Module

#### Functions

##### `hash_json`

```python
def hash_json(x: Dict) -> str:
    """
    Generates a hexadecimal hash string from a dictionary x using the MD5 algorithm.
     Args:
        x (Dict): A dictionary to be used to create the hash.
     Returns:
        str: An MD5 hash string created from x.
    """
```

##### `hash_string`

```python
def hash_string(x: str) -> str:
    """
    Generates a hexadecimal hash string from x using the MD5 algorithm.
     Args:
        x (str): The source string to be used to create the hash.
     Returns:
        str: An MD5 hash string created from x.
    """
```

##### `json_string`

```python
def json_string(x: Dict) -> str:
    """
    Converts a dictionary to a string encoded as UTF-8.
     Args:
        x (Dict): The dictionary to be converted.
     Returns:
        str: A string version of the dictionary encoded as UTF-8.
    """
```

##### `normalize_names`

```python
def normalize_names(names: List[str], normalize_specials: bool = True) -> List[str]:
    """
    Normalize string names to lower case, with spaces and slashes converted to underscores,
    and special characters translated.
     Args:
        names (list): The list of strings to be normalized.
        normalize_specials (bool, optional): If True, translates special characters into their regular ones.
            Default is True.
     Returns:
        list: The list of string names normalized.
    """
```

##### `normalize_value`

```python
def normalize_value(x: float, size: int = 4, decimal_places: int = 2) -> str:
    """
    Converts a float number into a string formatted with padding zeroes
    for the fixed length and decimal places.
     Args:
        x (float): The float number to convert.
        size (int, optional): The length of the result string. Default is 4.
        decimal_places (int, optional): Number of zeroes to fill in the decimal places. Default is 2.
     Returns:
        str: A fixed length string with zeroes padding on left and right.
     Example:
        normalize_value(1.2, size=5, decimal_places=2)
        will produce '00120'
         normalize_value(1.21, size=5, decimal_places=2)
        will produce '00121'
         normalize_value(12.3)
        will produce '1230'
    """
```

##### `random_string`

```python
def random_string(x: int = 32, include_digits: bool = True, include_special: bool = False) -> str:
    """
    Generates a random string with the combination of lowercase and uppercase
    letters and optionally digits and special characters.
     Args:
        x (int, optional): Set the random string's length. Default is 32.
        include_digits (bool, optional): If True, include random digits in the generated string.
            Default is True.
        include_special (bool, optional): If True, include special characters in the generated string.
            Default is False.
     Returns:
        str: A random string with the specified length, with or without digits or special characters.
    """
```

##### `similarity`

```python
def similarity(x: str, y: str, ignore_case: bool = True, compress_spaces: bool = True) -> float:
    """
    Calculates the similarity ratio between two strings.
    The result is in a range from 0 to 1 where 1 means both strings are equal.
     Args:
        x (str): The first string to compare.
        y (str): The second string to be compared with.
        ignore_case (bool, optional): If True, ignores the strings case. Default is True.
        compress_spaces (bool, optional): If True, removes extra space sequences in the strings. Default is True.
     Returns:
        float: The similarity ratio between the strings in a range from 0 to 1
            where 1 means that both strings are equal.
    """
```

##### `split_by_lengths`

```python
def split_by_lengths(string: str, lengths: List[int]) -> List[str]:
    """
    Splits a given string into multiple substrings based on the provided lengths.

    Args:
        string (str): The input string to be split.
        lengths (list): A list of integers representing the desired lengths of the substrings.

    Returns:
        list: A list of substrings obtained by splitting the input string based on the provided lengths.

    Raises:
        None

    Example:
        >>> split_by_lengths("HelloWorld", [5, 5])
        ['Hello', 'World']
    """
```

##### `translate_special_chars`

```python
def translate_special_chars(x) -> str:
    """
    Translates special (accented) characters in a string to regular characters.
     Args:
        x (str): The string to be translated.
     Returns:
        str: A new string with all special characters translated to regular ones.
    """
```

##### `uuid`

```python
def uuid() -> str:
    """
    Generates a standard uuid4 as string.
     Returns:
        str: A string with a standard uuid key.
    """
```

### xlsx Module

#### Classes

##### `ExcelWorkbook`

```python
class ExcelWorkbook:
    """Represents an Excel workbook."""

    def __init__(self, xl_file: Union[str, bytes]):
        \"\"\"
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
        \"\"\"

    def read_sheet(self, sheet_name: str = None) -> tuple[tuple[Union[str, float, int, bool, str, None], ...], ...]:
        \"\"\"
        Reads the contents of a sheet in the workbook.

        Args:
            sheet_name (str, optional): The name of the sheet to read.
                Defaults to None, which reads the first sheet.

        Returns:
            tuple[tuple[Union[str, float, int, bool, str, None], ...], ...]:
                A tuple of tuples representing the rows and columns of the sheet.

        Raises:
            NameError: If the sheet name is invalid or does not exist.
        \"\"\"

    def read_sheet_by_index(self, index: int = None) -> tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
        \"\"\"
        Reads the contents of a sheet in the workbook by index.

        Args:
            index (int, optional): The index of the sheet to read (0-based).
                Defaults to None, which reads the first sheet (index 0).

        Returns:
            tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
                A tuple of tuples representing the rows and columns of the sheet.

        Raises:
            NameError: If the sheet index is invalid or does not exist.
        \"\"\"
```

#### Functions

##### `get_all_sheets`

```python
def get_all_sheets(xl_file: Union[str, bytes]) -> Dict[str, tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]]:
    """
    Reads all sheets from an Excel file.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.

    Returns:
        dict[str, tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]]:
            Dictionary where keys are sheet names and values are sheet contents.
    """
```

##### `get_sheet_by_name`

```python
def get_sheet_by_name(xl_file: Union[str, bytes], sheet_name: str) -> tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
    """
    Reads a specific sheet from an Excel file by name.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.
        sheet_name (str): Name of the sheet to read.

    Returns:
        tuple[tuple[Union[str, float, int, bool, datetime, None], ...], ...]:
            Contents of the sheet as a tuple of tuples.
    """
```

##### `get_sheet_names`

```python
def get_sheet_names(xl_file: Union[str, bytes]) -> list[str]:
    """
    Retrieves sheet names from an Excel file.

    Args:
        xl_file (str or bytes): Path to the Excel file or bytes of the Excel file.

    Returns:
        list[str]: List of sheet names.
    """
```

##### `write_to_sheet`

```python
def write_to_sheet(df: pd.DataFrame, workbook_path: str, sheet_name: str) -> None:
    """
    Writes a pandas DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): DataFrame to write.
        workbook_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to write to.

    Returns:
        None
    """
```

## Contributing

Contributions are welcome! Please see the [contributing guidelines](CONTRIBUTING.md) for more information.

## Support

For support, please open an issue on [GitHub](https://github.com/franciscobispo/fbpyutils/issues).

## License

[MIT](LICENSE)
<<<<<<< HEAD
=======

### logging Module

Provides a global logging system for the `fbpyutils` library, configured to write logs to a file with automatic rotation.

#### Functions

##### `setup_logging`

```python
def setup_logging():
    """
    Configures a global file logging system for the fbpyutils library.

    Logs are rotated automatically, supporting concurrency, with a maximum of
    5 backup files and a maximum size of 256 KB per file.
    Logs are stored in a '.fbpyutils' folder within the user's HOME directory.
    """
>>>>>>> v1.6.2
