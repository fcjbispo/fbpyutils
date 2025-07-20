# fbpyutils Documentation

[![PyPI Version](https://img.shields.io/pypi/v/fbpyutils.svg)](https://pypi.org/project/fbpyutils/)
[![License](https://img.shields.io/pypi/l/MIT.svg)](https://opensource.org/licenses/MIT)

## Overview

Francisco Bispo's Utilities for Python. This library provides a comprehensive collection of utility functions for Python applications, designed to simplify common development tasks across multiple domains.

It includes modules for:
- Advanced calendar manipulation (`calendar`)
- Enhanced date/time utilities (`datetime`)
- Debugging tools (`debug`)
- Environment configuration (`env`)
- File system operations (`file`)
- Image processing (`image`)
- Configurable logging (`logging`)
- OFX file parsing (`ofx`)
- Parallel and serial processing (`process`)
- Advanced string manipulation (`string`)
- Excel file operations (`xlsx`)

## Installation

```bash
pip install fbpyutils
```

## Quick Start

The library must be initialized before use via the `setup()` function.

```python
from fbpyutils import setup, get_env, get_logger

# Initialize with default configuration
setup()

# Access global instances
env = get_env()
logger = get_logger()

logger.info(f"Application {env.APP.name} started.")
```

### Initialization and Configuration

#### `setup(config: Optional[Union[Dict[str, Any], str]] = None) -> None`
Initializes the global environment and logging system. This function should be called once when your application starts.

**Parameters:**
- `config`: Configuration source - can be a dictionary, JSON file path, or `None` for defaults.

**Example:**
```python
# Using default configuration
setup()

# Using custom configuration dict
setup({
    "app": {
        "name": "MyApp",
        "version": "1.0.0"
    },
    "logging": {
        "log_level": "DEBUG"
    }
})

# Using configuration file
setup("config/app.json")
```

#### `get_env() -> Env`
Returns the singleton `Env` instance containing all configuration.

#### `get_logger() -> Logger`
Returns the singleton `Logger` instance for application-wide logging.

---

## Modules

### 1. calendar

Functions to manipulate calendars and create time dimensions.

#### `get_calendar(x: date, y: date) -> List`
Builds a calendar to be used as a time dimension.

- **Args**:
    - `x (date)`: The initial date for the calendar.
    - `y (date)`: The final date for the calendar. Must be greater than the initial date.
- **Returns**: A list of dictionaries, where each dictionary represents a day and contains various date-related attributes.
- **Raises**: `ValueError` if the end date is not greater than the start date.

#### `add_markers(x: List) -> List`
Adds temporal markers to a calendar list. This function enriches a calendar list with boolean markers for common time-based analysis.

- **Args**:
    - `x (List)`: A calendar list, typically from `get_calendar`.
- **Returns**: The input calendar list with added boolean marker fields.

#### `calendarize(x: DataFrame, date_column: str, with_markers: bool = False) -> DataFrame`
Enriches a DataFrame with calendar columns based on a date column.

- **Args**:
    - `x (DataFrame)`: The input DataFrame.
    - `date_column (str)`: The name of the datetime column to be used for joining.
    - `with_markers (bool)`: If True, adds temporal markers.
- **Returns**: A new DataFrame with the added calendar columns.
- **Raises**: `TypeError` if the input is not a Pandas DataFrame, `NameError` if the date column is not found.

---

### 2. datetime

Utility functions to manipulate date and time.

#### `delta(x: datetime, y: datetime, delta: str = 'months') -> int`
Calculates the time delta between two dates in months or years.

- **Args**:
    - `x (datetime)`: The later datetime object.
    - `y (datetime)`: The earlier datetime object.
    - `delta (str)`: The unit for the delta ('months' or 'years').
- **Returns**: The total number of months or years between the two dates.

#### `apply_timezone(x: datetime, tz: str) -> datetime`
Applies a specified timezone to a naive datetime object.

- **Args**:
    - `x (datetime)`: The naive datetime object.
    - `tz (str)`: The string name of the timezone (e.g., 'America/Sao_Paulo').
- **Returns**: A new datetime object with the specified timezone.

**Example:**
```python
from datetime import datetime
from fbpyutils.datetime import apply_timezone

naive_dt = datetime(2023, 10, 27, 10, 0, 0)
sp_dt = apply_timezone(naive_dt, 'America/Sao_Paulo')
print(sp_dt)
# Output: 2023-10-27 10:00:00-03:00
```

#### `elapsed_time(x: datetime, y: datetime) -> tuple`
Calculates the elapsed time between two datetime objects.

- **Args**:
    - `x (datetime)`: The later datetime object.
    - `y (datetime)`: The earlier datetime object.
- **Returns**: A tuple containing (days, hours, minutes, seconds).

---

### 3. debug

Functions to support code debugging.

#### `debug(func)`
A decorator that logs the execution of a function, its arguments, and its return value. The output includes function name, arguments, keyword arguments, execution time, and the result.

#### `debug_info(x: Exception) -> str`
Get detailed debug information from an exception object, including the traceback. The returned string contains the exception type, message, file name, line number, and function name.

---

### 4. env

Configuration class for the application environment. This class is a singleton and is immutable after initialization.

#### `class Env`
Manages application configuration. It loads settings from a JSON file or dictionary and provides access to environment-specific variables.

- **Key Attributes**:
    - `APP`: Application-specific configuration (`AppConfig`).
    - `LOG_LEVEL`, `LOG_FORMAT`, `LOG_FILE`: Logging settings.
    - `USER_FOLDER`, `USER_APP_FOLDER`: User-specific paths.

**Example:**
```python
from fbpyutils import setup, get_env

# Load from a dictionary
setup({"app": {"name": "MyTestApp"}, "custom_key": "custom_value"})
env = get_env()

print(env.APP.name)  # Output: MyTestApp
print(env.custom_key) # Output: custom_value
```

#### `Env.load_config_from(app_conf_file: str) -> 'Env'`
Loads configuration from a specified JSON file and returns a new `Env` instance.

---

### 5. file

Functions to read and/or process files and directories.

#### `find(x: str, mask: str = "*.*", recurse: bool = True, parallel: bool = False) -> list`
Finds files in a source folder using a specific mask. For large directories, `parallel=True` can significantly improve performance by using multiple CPU cores.

#### `creation_date(x: str) -> datetime`
Retrieves the creation datetime of a file.

#### `load_from_json(x: str, encoding="utf-8") -> Dict`
Loads data from a JSON file.

#### `write_to_json(x: Dict, path_to_file: str, prettify=True)`
Writes a dictionary to a JSON file.

#### `contents(x: str) -> bytearray`
Reads a file and returns its contents as a byte array.

#### `mime_type(x: str) -> str`
Guesses the mime type of a file.

#### `describe_file(file_path: str) -> Dict`
Describes a file, returning a dictionary with its properties (size, hashes, etc.).

#### `get_base64_data_from(file_uri: str, timeout: int = 300) -> str`
Converts file content from a local path or URL to a base64 string.

---

### 6. image

Image processing utilities.

#### `get_image_info(image_source: Union[str, bytes]) -> dict`
Extracts detailed information from an image, including EXIF metadata and geolocation.

#### `resize_image(image_source: Union[str, bytes], width: int, height: int, maintain_aspect_ratio: bool = True, quality: int = 85) -> bytes`
Resizes an image to specified dimensions.

**Example:**
```python
from fbpyutils.image import resize_image

with open('my_image.jpg', 'rb') as f:
    image_bytes = f.read()

# Resize to a width of 800px, maintaining aspect ratio
resized_bytes = resize_image(image_bytes, width=800, height=0)

with open('resized_image.jpg', 'wb') as f:
    f.write(resized_bytes)
```

#### `enhance_image_for_ocr(image_source: Union[str, bytes], contrast_factor: float = 2.0, threshold: int = 128) -> bytes`
Enhances an image for better OCR accuracy by converting to grayscale, increasing contrast, and applying a binary threshold.

---

### 7. logging

A singleton logging class that provides a static interface to the logging module.

#### `class Logger`
Manages logging for the application. It must be configured via `fbpyutils.setup()`. It supports different log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`) and can be configured to log to a file and/or the console.

- **Methods**:
    - `debug(message: str, ...)`
    - `info(message: str, ...)`
    - `warning(message: str, ...)`
    - `error(message: str, ...)`
    - `log(log_type: int, log_text: str, ...)`

**Configuration via `setup()`:**
```python
setup({
    "logging": {
        "log_level": "INFO",
        "log_file": "logs/app.log",
        "log_format": "%(asctime)s - %(levelname)s - %(message)s"
    }
})
```

---

### 8. ofx

Reads and processes OFX (Open Financial Exchange) files and data.

#### Constants
- `account_types`: A list of known account types: `['UNKNOWN', 'BANK', 'CREDIT_CARD', 'INVESTMENT']`.

#### `format_date(x: datetime, native: bool = True) -> Union[datetime, str]`
Formats a datetime object into a native `datetime` or an ISO-formatted string.

#### `read(x: str, native_date: bool = True) -> Dict`
Parses OFX data from a string into a dictionary.

- **Args**:
    - `x (str)`: A string containing the OFX data.
    - `native_date (bool)`: If True, dates are returned as native `datetime` objects.
- **Returns**: A dictionary containing the parsed OFX data.

#### `read_from_path(x: str, native_date: bool = True) -> Dict`
Reads and parses an OFX file from a given path.

**Programmatic Example:**
```python
from fbpyutils.ofx import read_from_path

data = read_from_path('bank_statement.ofx')
if data:
    print(f"Account ID: {data.get('id')}")
    print(f"Account Type: {data.get('type')}")
    for tx in data.get('statement', {}).get('transactions', []):
        print(f"  - Date: {tx['date']}, Amount: {tx['amount']}, Memo: {tx['memo']}")
```

#### `main(argv)`
Main function to handle command-line execution for printing OFX file content as JSON.

**CLI Example**:
```bash
python -m fbpyutils.ofx --print /path/to/your/file.ofx
```

---

### 9. process

Module for parallel or serial process execution with control mechanisms.

#### `class Process`
Base class for executing functions in parallel or serial.

- **`run(params: List[Tuple[Any, ...]]) -> List[Tuple[bool, Optional[str], Any]]`**: Executes the processing function for each parameter set.

#### `class FileProcess(Process)`
Extends `Process` to add timestamp-based control for file processing, preventing reprocessing of unmodified files.

#### `class SessionProcess(Process)`
Extends `Process` to provide session-based control, allowing resumption of processing sessions.

**Example:**
```python
from fbpyutils.process import SessionProcess
import time

def my_task(item_id, duration):
    print(f"Processing item {item_id}...")
    time.sleep(duration)
    return f"Item {item_id} done."

# Parameters for the tasks
params = [(1, 2), (2, 3), (3, 1), (4, 2)]

# Initialize SessionProcess
# It will create a .session file to track progress
session_runner = SessionProcess(
    id='my_session',
    function=my_task,
    parallel=True,
    max_workers=2
)

# Run the process
results = session_runner.run(params)
print(results)

# If you run it again, it will skip the completed tasks.
```

---

### 10. string

Functions to manipulate and process strings.

#### `uuid() -> str`
Generate a standard UUID4 string.

#### `similarity(x: str, y: str, ignore_case: bool = True, compress_spaces: bool = True) -> float`
Calculate the similarity ratio between two strings (0.0 to 1.0) using `difflib.SequenceMatcher`. Useful for fuzzy string matching and validation.

#### `random_string(x: int = 32, include_digits: bool = True, include_special: bool = False) -> str`
Generate a random string.

#### `json_string(x: Dict) -> str`
Convert a dictionary to a JSON string.

#### `hash_string(x: str) -> str`
Generate an MD5 hash from a string. Useful for creating consistent identifiers from string content.

#### `hash_json(x: Dict) -> str`
Generate an MD5 hash from a dictionary.

#### `normalize_value(x: float, size: int = 4, decimal_places: int = 2) -> str`
Convert a float to a zero-padded string.

#### `translate_special_chars(x: str) -> str`
Translate special (accented) characters to their basic counterparts (e.g., 'á' -> 'a').

#### `normalize_names(names: List[str], normalize_specials: bool = True) -> List[str]`
Normalize a list of strings to a consistent format (lowercase, underscores).

#### `split_by_lengths(string: str, lengths: List[int]) -> List[str]`
Split a string into substrings of specified lengths.

---

### 11. xlsx

Functions to read and write MS Excel Spreadsheet files.

#### `class ExcelWorkbook`
Represents an Excel workbook, supporting both `.xls` and `.xlsx` formats.

- **`__init__(self, xl_file: Union[str, bytes])`**: Initializes from a file path or bytes.
- **`read_sheet(self, sheet_name: str = None) -> tuple`**: Reads a sheet by name.
- **`read_sheet_by_index(self, index: int = 0) -> tuple`**: Reads a sheet by index.

#### `get_sheet_names(xl_file: Union[str, bytes]) -> list[str]`
Retrieves the names of all sheets from an Excel file.

#### `get_sheet_by_name(xl_file: Union[str, bytes], sheet_name: str) -> tuple`
Reads a specific sheet from an Excel file by its name.

#### `get_all_sheets(xl_file: Union[str, bytes]) -> Dict[str, tuple]`
Reads all sheets from an Excel file into a dictionary.

**Example:**
```python
from fbpyutils.xlsx import get_all_sheets
import pandas as pd

# Assuming 'my_workbook.xlsx' has sheets 'Sales' and 'Customers'
all_data = get_all_sheets('my_workbook.xlsx')

sales_df = pd.DataFrame(all_data['Sales'][1:], columns=all_data['Sales'][0])
print(sales_df.head())
```

#### `write_to_sheet(df: pd.DataFrame, workbook_path: str, sheet_name: str) -> None`
Writes a pandas DataFrame to a specified sheet in an Excel file.
