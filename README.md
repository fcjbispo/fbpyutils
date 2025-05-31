# fbpyutils

Francisco Bispo's Utilities for Python

## Description

This project provides a collection of Python utility functions for various tasks, including:

- String manipulation
- Date and time operations
- Debugging tools
- File handling
  -   `describe_file(file_path: str)`: Inspects a file and returns a dictionary containing its properties.
      -   **Parameter:**
          -   `file_path (str)`: The path to the file.
      -   **Returns:** A dictionary with the following keys:
          -   `complete_filename (str)`: The full name of the file (e.g., "document.txt").
          -   `filename_no_ext (str)`: The filename without its extension (e.g., "document").
          -   `extension (str)`: The file extension (e.g., ".txt").
          -   `size_bytes (int)`: The size of the file in bytes.
          -   `creation_date (str)`: The creation date of the file in ISO 8601 format (e.g., "2023-10-27T10:30:00"). Note: This is a naive datetime.
          -   `mime_type_code (str)`: The detected MIME type code (e.g., "text/plain").
          -   `mime_type_description (str)`: A human-readable description of the MIME type (e.g., "Text file").
          -   `first_256_bytes_sha256_hex (str)`: The SHA256 hash (hexadecimal string) of the first 256 bytes of the file. If the file is smaller than 256 bytes, it hashes the entire content.
          -   `md5sum (str)`: The MD5 hash (hexadecimal string) of the entire file content.
      -   **Example:**
      ```python
      from fbpyutils.file import describe_file
      
      file_info = describe_file("my_document.txt")
      if file_info:
          print(f"Filename: {file_info['complete_filename']}")
          print(f"Size: {file_info['size_bytes']} bytes")
          print(f"MD5 Hash: {file_info['md5sum']}")
      ```
  -   `get_file_head_content(file_path: str, num_bytes: int = 256, output_format: str = 'text', encoding: str = 'utf-8', errors: str = 'replace')`: Reads the first `num_bytes` of a file and returns its content in the specified format.
      -   **Parameters:**
          -   `file_path (str)`: The path to the file.
          -   `num_bytes (int)`: The number of bytes to read from the beginning of the file. Defaults to 256.
          -   `output_format (str)`: The desired output format. Can be 'text', 'bytes', or 'base64'. Defaults to 'text'.
          -   `encoding (str)`: The encoding to use if `output_format` is 'text'. Defaults to 'utf-8'.
          -   `errors (str)`: The error handling scheme to use for decoding if `output_format` is 'text'. Defaults to 'replace'.
      -   **Returns:** The content of the head of the file in the specified format (`str`, `bytes`, or `None` if an error occurs or format is invalid).
      -   **Example:**
      ```python
      from fbpyutils.file import get_file_head_content
      
      # Get first 100 bytes as text
      head_text = get_file_head_content("my_document.txt", num_bytes=100, output_format='text')
      if head_text is not None:
          print(f"First 100 bytes (text): {head_text}")
      
      # Get first 50 bytes as raw bytes
      head_bytes = get_file_head_content("my_image.jpg", num_bytes=50, output_format='bytes')
      if head_bytes is not None:
          print(f"First 50 bytes (raw): {head_bytes}")
      
      # Get first 200 bytes as base64 string
      head_base64 = get_file_head_content("my_archive.zip", num_bytes=200, output_format='base64')
      if head_base64 is not None:
          print(f"First 200 bytes (base64): {head_base64}")
      
      # Handle non-existent file
      non_existent = get_file_head_content("non_existent_file.txt")
      if non_existent is None:
          print("File not found or an error occurred.")
      ```
- Excel file processing
- OFX parsing
- Process management with parallel execution and control mechanisms

## Documentation

- [DOC.md](DOC.md): Detailed documentation of all modules and functions.
- [TODO.md](TODO.md): Current status comparing documentation, implementation, and test coverage.

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
````

## License
This project is licensed under the MIT License. For the full text of the license, see [the official MIT License](https://opensource.org/licenses/MIT).

---
## MIT License Disclaimer

Copyright (c) 2025 Francisco C J Bispo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**
