# fbpyutils

Francisco Bispo's Utilities for Python

## Description

This project provides a collection of Python utility functions for various tasks, including:

- String manipulation
- Date and time operations
- Debugging tools
- File handling
- Excel file processing
- OFX parsing
- Process management with parallel execution and control mechanisms

## Documentation

- [DOC.md](DOC.md): Detailed documentation of all modules and functions.
- [TODO.md](TODO.md): Current status comparing documentation, implementation, and test coverage.

## License

Apache-2.0

## Authors

- Francisco C J Bispo (fcjbispo@franciscobispo.net)

## Dependencies

- pandas
- ofxparse
- pytz
- openpyxl
- xlrd
- python-magic-bin

## Development Dependencies

- pytest
- pytest-cov
- pytest-mock

## Installation

```bash
uv pip install .
```

## Tests

```bash
pytest tests
