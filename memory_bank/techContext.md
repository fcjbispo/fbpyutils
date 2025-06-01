# Technical Context

This document details the technologies used, development setup, technical constraints, dependencies, and tool usage patterns for the project. It provides essential information for developers working on the system.

## Technologies Used
- **Programming Language:** Python 3.10+
- **Core Libraries:**
    - `pandas`: For data manipulation, especially in `calendar` and `xlsx` modules.
    - `ofxparse`: For parsing OFX financial files.
    - `pytz`: For timezone handling in `datetime` module.
    - `openpyxl`: For reading/writing `.xlsx` files.
    - `xlrd`: For reading older `.xls` files.
    - `python-magic-bin` (Windows) / `python-magic` (Linux/macOS): For MIME type detection in `file` module.
    - `pathlib`: For object-oriented filesystem paths.
    - `logging`: Python's standard logging library for the global logging system.
    - `concurrent.futures`: For parallel processing in the `process` module.
    - `hashlib`: For hashing operations.
    - `uuid`: For generating UUIDs.
    - `json`: For JSON serialization/deserialization.
    - `base64`: For Base64 encoding/decoding.
    - `difflib`: For string similarity calculations.
    - `platform`: For OS detection.
    - `os`: For operating system interactions.
    - `sys`: For system-specific parameters and functions.
    - `datetime`: Python's built-in datetime module.

## Development Setup
1.  **Python Installation:** Ensure Python 3.10 or higher is installed.
2.  **`uv` Installation:** Install `uv` (a fast Python package installer and resolver) if not already present:
    ```bash
    pip install uv
    ```
3.  **Virtual Environment:** Create and activate a virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate     # On Windows
    ```
4.  **Install Dependencies:** Install project dependencies using `uv`:
    ```bash
    uv pip install .
    ```
    For development dependencies (e.g., `pytest`, `pytest-cov`, `pytest-mock`):
    ```bash
    uv add --group dev pytest pytest-cov pytest-mock
    ```
5.  **Code Editor:** VS Code with Python extensions is recommended.

## Technical Constraints
- **Python Version Compatibility:** The library is developed and tested against Python 3.10+. Compatibility with older versions is not guaranteed.
- **External Library Dependencies:** Reliance on third-party libraries means their stability and performance directly impact `fbpyutils`.
- **Operating System Specifics:** While efforts are made for cross-platform compatibility, some functionalities (e.g., `python-magic-bin` vs `python-magic` for MIME types, file path formats) require OS-specific handling.
- **File Size Limitations:** Processing extremely large files (e.g., multi-GB Excel files) might be constrained by available memory, although `xlsx` module aims for efficiency.
- **OFX Format Variations:** OFX parsing might encounter issues with highly non-standard OFX file formats.

## Dependencies
Dependencies are managed via `pyproject.toml` and `uv.lock`.
- **Runtime Dependencies:**
    - `pandas`
    - `ofxparse`
    - `pytz`
    - `openpyxl`
    - `xlrd`
    - `python-magic-bin` (for Windows, `python-magic` for others)
- **Development Dependencies (managed in `[tool.uv.dev-dependencies]`):**
    - `pytest`
    - `pytest-cov`
    - `pytest-mock`

## Tool Usage Patterns
- **`uv`:** Used for all package installations (`uv pip install .`, `uv add --group dev <package>`) and running Python commands (`uv run pytest`). This ensures consistent dependency resolution and environment management.
- **`pytest`:** The primary testing framework. Tests are organized in the `tests/` directory, following `test_<module>_<scenario>.py` naming conventions.
- **`pytest-cov`:** Used with `pytest` to generate code coverage reports (XML and HTML formats), enforcing the 90% coverage requirement.
- **`git`:** Used for version control, including staging, committing, branching, and merging changes. Commit messages are in Brazilian Portuguese.
- **VS Code:** The primary IDE for development, leveraging its Python extensions for linting, debugging, and code navigation.

## Deployment Information (Optional)
The library is intended to be packaged and distributed via PyPI. Users can install it using `pip install fbpyutils` or `uv pip install fbpyutils`.

## API Endpoints (Optional)
N/A - This is a utility library, not a service with API endpoints.

## Date Created
2023-10-27

## Last Updated
2025-05-31
