# FBPyUtils

A comprehensive Python utility library providing helper functions and classes for common development tasks.

## Overview

FBPyUtils is a collection of utility modules designed to simplify common development tasks including:

- 📅 **Calendar operations** - Date range generation and calendar formatting
- 🕐 **Date/time manipulation** - Advanced date/time utilities
- 🔍 **Debugging tools** - Debug decorators and utilities
- 📁 **File operations** - Comprehensive file system utilities
- 🖼️ **Image processing** - Image manipulation and utilities
- 📝 **Logging configuration** - Centralized logging setup
- 💰 **OFX processing** - Open Financial Exchange file parsing
- ⚙️ **Process utilities** - System and process information
- 📝 **String manipulation** - Advanced string utilities
- 📊 **Excel operations** - Excel file reading and processing

## Quick Start

```python
from fbpyutils import string, file, datetime

# Generate UUID
uuid_str = string.uuid()

# Read file content
content = file.contents("example.txt")

# Calculate date differences
from datetime import datetime
elapsed = datetime.elapsed_time(datetime(2024, 1, 1), datetime(2024, 1, 2))
```

## Installation

```bash
pip install fbpyutils
```

## Documentation

For complete API documentation, including all modules, classes, and functions, please see the **[Full Documentation](DOC.md)**.

- **[TODO List](TODO.md)** - Implementation status and development roadmap
- **[Project Specifications](SPEC.md)** - Detailed feature specifications

## Available Modules

Below is an overview of the available modules and quick examples of their use.

### `calendar`
Advanced calendar operations for time dimension creation and date analysis.
```python
from fbpyutils.calendar import get_calendar
from datetime import date
calendar = get_calendar(date(2024, 1, 1), date(2024, 12, 31))
print(f"Created calendar with {len(calendar)} days")
```

### `datetime`
Enhanced datetime utilities with timezone support and duration calculations.
```python
from fbpyutils.datetime import elapsed_time
from datetime import datetime
elapsed = elapsed_time(datetime(2024, 1, 1), datetime.now())
print(f"Elapsed time: {elapsed[0]} days, {elapsed[1]} hours")
```

### `debug`
Decorators and utilities for development and debugging.
```python
from fbpyutils.debug import debug

@debug
def my_function(a, b):
    return a + b

my_function(1, 2)
```

### `file`
Comprehensive file system operations with metadata extraction.
```python
from fbpyutils.file import describe_file
info = describe_file("README.md")
print(f"File size: {info['size_bytes']} bytes")
```

### `image`
Image processing utilities, including resizing and OCR enhancement.
```python
from fbpyutils.image import get_image_info
# Assuming 'logo.png' exists
# info = get_image_info('logo.png')
# print(f"Image dimensions: {info['width']}x{info['height']}")
```

### `logging`
Advanced logging system with rotation and simple configuration.
```python
from fbpyutils import get_logger
logger = get_logger()
logger.info("This is an informational message.")
```

### `ofx`
OFX (Open Financial Exchange) file parser for financial data.
```python
from fbpyutils.ofx import read_from_path
# Assuming 'statement.ofx' exists
# data = read_from_path('statement.ofx')
# print(f"Found {len(data.get('transactions', []))} transactions.")
```

### `process`
Advanced processing framework with parallel execution support.
```python
from fbpyutils.process import Process
def task(item):
    return item * 2
processor = Process(task, parallelize=True)
results = processor.run([1, 2, 3, 4])
print(results)
```

### `string`
Advanced string manipulation and hashing utilities.
```python
from fbpyutils.string import uuid
random_uuid = uuid()
print(f"Generated UUID: {random_uuid}")
```

### `xlsx`
Excel file operations with pandas integration.
```python
from fbpyutils.xlsx import read_file
# Assuming 'data.xlsx' exists
# df = read_file('data.xlsx')
# print(df.head())
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/fcjbispo/fbpyutils.git
cd fbpyutils

# Install dependencies
uv sync

# Run tests
uv run pytest

# Check coverage
uv run pytest --cov=fbpyutils --cov-report=html
```

### Testing

The project uses pytest for testing with a target of 90%+ code coverage:

```bash
# Run all tests
uv run pytest -s -vv

# Run with coverage
uv run pytest -s -vv --cov=fbpyutils --cov-report=xml --cov-report=html
```

## Requirements

- Python 3.8+
- pandas
- openpyxl
- Pillow
- python-dateutil
- requests

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/fcjbispo/fbpyutils/issues).
