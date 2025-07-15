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

- **[Full Documentation](DOC.md)** - Complete API documentation and usage examples
- **[TODO List](TODO.md)** - Implementation status and development roadmap
- **[Project Specifications](SPEC.md)** - Detailed feature specifications

## Features

### Core Modules

| Module | Description | Status |
|--------|-------------|--------|
| `calendar.py` | Calendar and date range utilities | ✅ Complete |
| `datetime.py` | Date/time manipulation functions | ✅ Complete |
| `debug.py` | Debugging utilities and decorators | ✅ Complete |
| `file.py` | File system operations | ✅ Complete |
| `image.py` | Image processing utilities | ✅ Complete |
| `logging.py` | Logging configuration | ✅ Complete |
| `ofx.py` | OFX file processing | ✅ Complete |
| `process.py` | System and process utilities | ✅ Complete |
| `string.py` | String manipulation utilities | ✅ Complete |
| `xlsx.py` | Excel file operations | ✅ Complete |

### Key Features

- **Type Hints**: Full type annotation support
- **Comprehensive Testing**: 140+ tests with 90%+ coverage target
- **Logging Integration**: Built-in logging support
- **Error Handling**: Robust error handling throughout
- **Cross-platform**: Windows, macOS, and Linux support

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
