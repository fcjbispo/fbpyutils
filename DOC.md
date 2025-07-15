# fbpyutils Documentation

[![PyPI Version](https://img.shields.io/pypi/v/fbpyutils.svg)](https://pypi.org/project/fbpyutils/)
[![License](https://img.shields.io/pypi/l/MIT.svg)](https://opensource.org/licenses/MIT)

## Overview

Francisco Bispo's Utilities for Python. This library provides a comprehensive collection of utility functions for Python applications, designed to simplify common development tasks across multiple domains.

### Core Modules

- **`calendar`**: Advanced calendar manipulation and time dimension creation
- **`datetime`**: Enhanced date/time utilities with timezone support
- **`debug`**: Debugging tools and decorators for development
- **`env`**: Environment configuration and management system
- **`file`**: Comprehensive file system operations and metadata extraction
- **`image`**: Image processing and manipulation utilities
- **`logging`**: Configurable logging system with rotation
- **`ofx`**: OFX (Open Financial Exchange) file parser
- **`process`**: Parallel and serial processing with session management
- **`string`**: Advanced string manipulation and hashing utilities
- **`xlsx`**: Excel file operations with pandas integration

## Installation

```bash
pip install fbpyutils
```

## Quick Start

```python
from fbpyutils import setup

# Initialize the library
setup()

# Access global instances
from fbpyutils import get_env, get_logger
env = get_env()
logger = get_logger()
```

## Usage Guide

### Initialization and Configuration

The `fbpyutils` library must be initialized before use via the `setup()` function.

#### `setup(config: Optional[Union[Dict[str, Any], str]] = None) -> None`
Initializes the global environment and logging system. This function should be called once when your application starts.

**Parameters:**
- `config`: Configuration source - can be a dictionary, JSON file path, or None for defaults

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
        "level": "DEBUG"
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

### calendar Module

Advanced calendar operations for time dimension creation and date analysis.

#### Functions

##### `get_calendar(start_date: date, end_date: date) -> List[Dict[str, Any]]`
Creates a comprehensive calendar between two dates with detailed time attributes.

**Parameters:**
- `start_date`: Starting date
- `end_date`: Ending date (must be > start_date)

**Returns:** List of dictionaries with calendar attributes:
- `date`: Date object
- `date_time`: Datetime object
- `year`: Year as integer
- `half`: Half of year (1 or 2)
- `quarter`: Quarter (1-4)
- `month`: Month (1-12)
- `day`: Day of month
- `week_day`: Day of week (0=Monday, 6=Sunday)
- `week_of_year`: ISO week number
- `date_iso`: ISO format string
- `date_str`: Formatted date string
- `week_day_name`: Full weekday name
- `week_day_name_short`: Abbreviated weekday
- `week_month_name`: Full month name
- `week_month_name_short`: Abbreviated month
- `year_str`: Year as string
- `year_half_str`: Year-half string
- `year_quarter_str`: Year-quarter string
- `year_month_str`: Year-month string

**Example:**
```python
from fbpyutils.calendar import get_calendar
from datetime import date

calendar = get_calendar(date(2024, 1, 1), date(2024, 12, 31))
print(f"Created calendar with {len(calendar)} days")
```

##### `add_markers(calendar_data: List, reference_date: date = None) -> List`
Adds temporal markers to calendar data for analysis.

**Markers Added:**
- `today`: True if date equals reference
- `current_year`: True if in current year
- `last_day_of_month`: True if month's last day
- `last_day_of_quarter`: True if quarter's last day
- `last_day_of_half`: True if half's last day
- `last_day_of_year`: True if year's last day
- `last_24_months`: True if within last 24 months
- `last_12_months`: True if within last 12 months
- `last_6_months`: True if within last 6 months
- `last_3_months`: True if within last 3 months

##### `calendarize(df: DataFrame, date_column: str, with_markers: bool = False, reference_date: date = None) -> DataFrame`
Adds calendar columns to a pandas DataFrame.

**Example:**
```python
import pandas as pd
from fbpyutils.calendar import calendarize

df = pd.DataFrame({'date': pd.date_range('2024-01-01', periods=100)})
df = calendarize(df, 'date', with_markers=True)
```

---

### datetime Module

Enhanced datetime utilities with timezone support and duration calculations.

#### Functions

##### `apply_timezone(dt: datetime, tz: str) -> datetime`
Applies timezone information to a datetime object.

**Example:**
```python
from fbpyutils.datetime import apply_timezone
from datetime import datetime

dt = datetime.now()
tz_dt = apply_timezone(dt, 'America/Sao_Paulo')
```

##### `delta(start: datetime, end: datetime, unit: str = 'months') -> int`
Calculates time difference between two dates.

**Units:**
- `months`: Number of months
- `years`: Number of years

**Example:**
```python
from fbpyutils.datetime import delta
from datetime import datetime

months_diff = delta(datetime(2024, 1, 1), datetime(2024, 12, 31))
```

##### `elapsed_time(start: datetime, end: datetime) -> tuple`
Calculates elapsed time as (days, hours, minutes, seconds).

---

### debug Module

Development debugging utilities.

#### Functions

##### `debug(func)`
Decorator for automatic function debugging.

**Usage:**
```python
from fbpyutils.debug import debug

@debug
def calculate_total(items):
    return sum(items)

# Automatically logs inputs and outputs
result = calculate_total([1, 2, 3, 4, 5])
```

##### `debug_info(exception: Exception) -> str`
Returns formatted exception information for debugging.

---

### env Module

Environment configuration management system.

#### Classes

##### `Env`
Singleton configuration manager with automatic file loading.

**Features:**
- Automatic configuration from JSON files
- Environment variable integration
- Nested configuration access
- Hot-reload support

**Usage:**
```python
from fbpyutils import get_env

env = get_env()
app_name = env.config.app.name
log_level = env.config.logging.level
```

---

### file Module

Comprehensive file system operations with metadata extraction.

#### Functions

##### `find(directory: str, mask: str = '*.*') -> List[str]`
Recursively finds files matching a pattern.

**Example:**
```python
from fbpyutils.file import find

# Find all Python files
py_files = find('/project', '*.py')

# Find all images
images = find('/photos', '*.jpg')
```

##### `describe_file(file_path: str) -> Dict[str, Any]`
Extracts comprehensive file metadata.

**Returns:**
- `complete_filename`: Full filename
- `filename_no_ext`: Name without extension
- `extension`: File extension
- `size_bytes`: File size in bytes
- `creation_date`: Creation date (ISO format)
- `mime_type_code`: MIME type
- `mime_type_description`: Human-readable MIME type
- `first_256_bytes_sha256_hex`: SHA256 of first 256 bytes
- `md5sum`: MD5 hash of entire file

**Example:**
```python
from fbpyutils.file import describe_file

info = describe_file('document.pdf')
print(f"File: {info['complete_filename']}")
print(f"Size: {info['size_bytes']} bytes")
print(f"MD5: {info['md5sum']}")
```

##### `get_file_head_content(file_path: str, num_bytes: int = 256, output_format: str = 'text', encoding: str = 'utf-8') -> Union[str, bytes, None]`
Reads file header content in various formats.

**Output Formats:**
- `text`: UTF-8 decoded string
- `bytes`: Raw bytes
- `base64`: Base64 encoded string

**Example:**
```python
# Get first 100 bytes as text
header = get_file_head_content('data.csv', 100, 'text')

# Get raw bytes for binary analysis
raw_bytes = get_file_head_content('image.jpg', 512, 'bytes')
```

##### `get_base64_data_from(file_uri: str, timeout: int = 300) -> str`
Converts file content to base64 string from local path or URL.

**Example:**
```python
# Local file
b64_data = get_base64_data_from('/path/to/file.pdf')

# Remote file
b64_data = get_base64_data_from('https://example.com/file.jpg')
```

##### File I/O Utilities
- `load_from_json(path: str, encoding: str = 'utf-8') -> Dict`
- `write_to_json(data: Dict, path: str, prettify: bool = True)`
- `contents(path: str) -> bytearray`
- `creation_date(path: str) -> datetime`
- `mime_type(path: str) -> str`
- `absolute_path(path: str) -> str`
- `build_platform_path(winroot: str, otherroot: str, pathparts: List[str]) -> str`

---

### image Module

Image processing utilities with OCR enhancement support.

#### Functions

##### `get_image_info(image_source: Union[str, bytes]) -> Dict[str, Any]`
Extracts comprehensive image metadata.

**Returns:**
- `filename`: Original filename
- `format`: Image format (JPEG, PNG, etc.)
- `mode`: Color mode (RGB, RGBA, etc.)
- `size`: (width, height) tuple
- `width`: Image width
- `height`: Image height
- `file_size_bytes`: File size
- `dpi`: Dots per inch
- `gps_info`: GPS coordinates if available
- `has_transparency`: Boolean
- `is_animated`: Boolean
- `frame_count`: Number of frames

**Example:**
```python
from fbpyutils.image import get_image_info

info = get_image_info('photo.jpg')
print(f"Image: {info['width']}x{info['height']} pixels")
print(f"Format: {info['format']}")
```

##### `resize_image(image_source: Union[str, bytes], width: int, height: int, maintain_aspect: bool = True) -> bytes`
Resizes images while maintaining quality.

**Example:**
```python
from fbpyutils.image import resize_image

# Resize to specific dimensions
resized = resize_image('large.jpg', 800, 600)

# Resize with aspect ratio maintained
thumbnail = resize_image('photo.jpg', 200, 200)
```

##### `enhance_image_for_ocr(image_source: Union[str, bytes], contrast_factor: float = 2.0, threshold: int = 128) -> bytes`
Optimizes images for OCR processing.

**Example:**
```python
from fbpyutils.image import enhance_image_for_ocr

# Enhance for better OCR results
enhanced = enhance_image_for_ocr('scanned_document.jpg')
```

---

### logging Module

Advanced logging system with rotation and configuration.

#### Classes

##### `Logger`
Singleton logging system with file rotation.

**Features:**
- Automatic log rotation (256KB max, 5 backups)
- Thread-safe concurrent logging
- Configurable log levels
- Structured JSON logging support

**Usage:**
```python
from fbpyutils import get_logger

logger = get_logger()
logger.info("Application started")
logger.debug("Debug information")
logger.error("Error occurred", extra={"error_code": 500})
```

---

### ofx Module

OFX (Open Financial Exchange) file parser for financial data.

#### Functions

##### `read_from_path(file_path: str, native_date: bool = True) -> Dict[str, Any]`
Reads OFX file and returns structured financial data.

**Returns:**
- `header`: OFX header information
- `signon`: Signon response
- `transactions`: List of transactions
- `balances`: Account balances
- `status`: Processing status

**Example:**
```python
from fbpyutils.ofx import read_from_path

data = read_from_path('bank_statement.ofx')
transactions = data.get('transactions', [])
for tx in transactions:
    print(f"{tx['date']}: {tx['amount']} - {tx['memo']}")
```

##### `read(ofx_content: str, native_date: bool = True) -> Dict[str, Any]`
Parses OFX content string directly.

---

### process Module

Advanced processing framework with parallel execution support.

#### Classes

##### `Process`
Base class for parallel/serial processing.

**Features:**
- Automatic CPU core detection
- Thread/process pool management
- Progress tracking
- Error handling and retry logic

**Example:**
```python
from fbpyutils.process import Process

def process_item(item_id, data):
    # Process single item
    return f"Processed {item_id}"

# Create processor
processor = Process(process_item, parallelize=True, workers=4)

# Process multiple items
params = [(1, "data1"), (2, "data2"), (3, "data3")]
results = processor.run(params)
```

##### `FileProcess`
File-based processing with timestamp control.

**Features:**
- Prevents duplicate processing
- Timestamp-based file filtering
- Batch processing support

**Example:**
```python
from fbpyutils.process import FileProcess
import os

def process_file(file_path, output_dir):
    # Process file
    return f"Processed {os.path.basename(file_path)}"

processor = FileProcess(process_file)
files_to_process = [("file1.txt", "/output"), ("file2.txt", "/output")]
results = processor.run(files_to_process, controlled=True)
```

##### `SessionProcess`
Session-based processing with resume capability.

**Features:**
- Session persistence
- Resume interrupted processes
- Task-level retry logic
- Progress tracking

**Example:**
```python
from fbpyutils.process import SessionProcess

def long_running_task(task_id, data):
    # Simulate long process
    return f"Completed task {task_id}"

processor = SessionProcess(long_running_task)
params = [(1, "large_dataset1"), (2, "large_dataset2")]

# Start with session control
results = processor.run(params, session_id="batch_001", controlled=True)
```

---

### string Module

Advanced string manipulation and hashing utilities.

#### Functions

##### `similarity(str1: str, str2: str, ignore_case: bool = True, compress_spaces: bool = True) -> float`
Calculates string similarity ratio (0.0 to 1.0).

**Example:**
```python
from fbpyutils.string import similarity

ratio = similarity("hello world", "hello  world!")
print(f"Similarity: {ratio:.2%}")
```

##### `normalize_names(names: List[str], normalize_specials: bool = True) -> List[str]`
Normalizes strings for consistent naming.

**Features:**
- Lowercase conversion
- Space/slash to underscore
- Special character translation
- Unicode normalization

**Example:**
```python
from fbpyutils.string import normalize_names

names = ["Hello World!", "Café/Bar", "Test-Case"]
normalized = normalize_names(names)
# Result: ["hello_world", "cafe_bar", "test_case"]
```

##### `random_string(length: int = 32, include_digits: bool = True, include_special: bool = False) -> str`
Generates cryptographically secure random strings.

**Example:**
```python
from fbpyutils.string import random_string

# Simple random string
token = random_string(16)

# Complex password
password = random_string(24, include_digits=True, include_special=True)
```

##### Hashing Functions
- `hash_string(text: str) -> str`: MD5 hash
- `hash_json(data: Dict) -> str`: JSON-stable MD5 hash
- `uuid() -> str`: UUID4 generation

##### String Utilities
- `json_string(data: Dict) -> str`: JSON to string
- `normalize_value(value: float, size: int = 4, decimals: int = 2) -> str`: Zero-padded numbers
- `translate_special_chars(text: str) -> str`: Accent removal
- `split_by_lengths(text: str, lengths: List[int]) -> List[str]`: Fixed-width splitting

---

### xlsx Module

Excel file operations with pandas integration.

#### Classes

##### `ExcelWorkbook`
High-level Excel workbook interface.

**Features:**
- XLS/XLSX support
- Sheet enumeration
- Data extraction
- Memory-efficient reading

**Example:**
```python
from fbpyutils.xlsx import ExcelWorkbook

# Load workbook
wb = ExcelWorkbook('data.xlsx')

# Get sheet names
sheets = wb.sheet_names
print(f"Available sheets: {sheets}")

# Read specific sheet
data = wb.read_sheet('SalesData')
for row in data:
    print(row)
```

#### Functions

##### `get_all_sheets(file_path: Union[str, bytes]) -> Dict[str, Tuple]`
Reads all sheets into a dictionary.

**Example:**
```python
from fbpyutils.xlsx import get_all_sheets

all_data = get_all_sheets('report.xlsx')
for sheet_name, data in all_data.items():
    print(f"Sheet: {sheet_name}, Rows: {len(data)}")
```

##### `write_to_sheet(df: pd.DataFrame, file_path: str, sheet_name: str) -> None`
Writes pandas DataFrame to Excel sheet.

**Features:**
- Creates new files or appends to existing
- Automatic sheet naming for duplicates
- Format preservation

**Example:**
```python
import pandas as pd
from fbpyutils.xlsx import write_to_sheet

df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
write_to_sheet(df, 'output.xlsx', 'MyData')
```

---

## Best Practices

### Error Handling
All functions include comprehensive error handling. Always wrap operations in try-catch blocks:

```python
from fbpyutils import get_logger

logger = get_logger()

try:
    result = some_fbpyutils_function()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

### Performance Optimization
- Use parallel processing for CPU-intensive tasks
- Leverage file timestamp control to avoid reprocessing
- Implement session-based processing for long-running tasks

### Configuration Management
Store configuration in JSON files:

```json
{
  "app": {
    "name": "MyApplication",
    "version": "1.0.0"
  },
  "logging": {
    "level": "INFO",
    "file": "app.log"
  }
}
```

### Testing
The library includes comprehensive test coverage. Run tests with:

```bash
# Run all tests
uv run pytest tests/

# Run specific module tests
uv run pytest tests/test_file_file.py

# Run with coverage
uv run pytest --cov=fbpyutils tests/
```

---

## Troubleshooting

### Common Issues

**Import Errors**
```python
# Ensure proper initialization
from fbpyutils import setup
setup()  # Must be called before using other modules
```

**File Not Found Errors**
```python
from fbpyutils.file import absolute_path

# Get absolute path for relative files
full_path = absolute_path('data/file.txt')
```

**Memory Issues with Large Files**
```python
from fbpyutils.file import get_file_head_content

# Process files in chunks
header = get_file_head_content('large_file.dat', 1024)
```

### Debug Mode
Enable debug logging for troubleshooting:

```python
from fbpyutils import setup

setup({
    "logging": {
        "level": "DEBUG"
    }
})
```

---

## Contributing

Contributions are welcome! Please see the [contributing guidelines](CONTRIBUTING.md) for more information.

### Development Setup

1. Clone the repository
2. Create virtual environment: `uv venv`
3. Install dependencies: `uv sync`
4. Run tests: `uv run pytest`

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Maintain test coverage above 90%

---

## Support

For support, please:
1. Check the [troubleshooting section](#troubleshooting)
2. Search existing [issues](https://github.com/franciscobispo/fbpyutils/issues)
3. Create a new issue with:
   - Minimal reproduction example
   - Expected vs actual behavior
   - Environment details (Python version, OS)

## License

[MIT](LICENSE) - See LICENSE file for details.
