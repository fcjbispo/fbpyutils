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

@TODO

## Documentation

For complete API documentation, including all modules, classes, and functions, please see the **[Full Documentation](DOC.md)**.

- **[TODO List](TODO.md)** - Implementation status and development roadmap
- **[Project Specifications](SPEC.md)** - Detailed feature specifications

## Requirements

@TODO

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/fcjbispo/fbpyutils/issues).
