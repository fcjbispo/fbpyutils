# Release Plan: Version 1.6.3

This document outlines the detailed steps required to implement the "Next Steps" identified in `TODO.md` for the `fbpyutils` library.

---

## 1. Improve test coverage for the `ofx` and `xlsx` modules.

*   **Objective:** Increase the test coverage for the `ofx` and `xlsx` modules to ensure greater robustness and reliability, aiming for a target coverage percentage (e.g., >90%).
*   **Suggested Mode:** `DEBUG`
*   **Detailed Steps:**
    1.  Analyze the test coverage report (e.g., `coverage.xml`) to pinpoint uncovered lines and branches within the `fbpyutils/ofx.py` and `fbpyutils/xlsx.py` modules.
    2.  Review the source code of `fbpyutils/ofx.py` and `fbpyutils/xlsx.py` to understand the business logic and identify critical use cases.
    3.  Write new test cases or extend existing ones in `tests/test_ofx_ofx.py` and `tests/test_xlsx_xlsx.py` to cover the identified areas.
    4.  Execute the tests and verify the increase in coverage.
    5.  Repeat steps 1-4 until a satisfactory coverage percentage is achieved.

---

## 2. Consider adding modules to `__init__.py` for easier import.

*   **Objective:** Facilitate the import of `fbpyutils` modules by making them directly accessible from the main package, simplifying client code (e.g., `from fbpyutils import calendar` instead of `from fbpyutils import get_logger.calendar`).
*   **Suggested Mode:** `CODE`
*   **Detailed Steps:**
    1.  Open the `fbpyutils/__init__.py` file.
    2.  Add `from . import <module_name>` statements for each module intended for direct exposure (e.g., `calendar`, `datetime`, `debug`, `ofx`, `file`, `process`, `string`, `xlsx`, `logging`).
    3.  Test the new import paths in a development environment to ensure they function as expected.

---

## 3. Create a `SPEC.md` file to formally define specifications.

*   **Objective:** Establish a formal document to define the specifications and design of the library, serving as a comprehensive reference for development and maintenance.
*   **Suggested Mode:** `ARCHITECT`
*   **Detailed Steps:**
    1.  Create a new file named `SPEC.md` in the root directory of the project.
    2.  Define the document structure, including sections such as Introduction, Architecture Overview, Module Specifications, Code Conventions, etc.
    3.  Populate the document with existing specifications and outline future design considerations.

---

## 4. Implement the global logging system (`fbpyutils.logging`) as configurable via a client's `Env` class.

*   **Objective:** Implement a global logging system (`fbpyutils.logging`) configurable via an instance of a class `Env` from `fbpyutils` to make it reusable by API clients. The API clients should provide their own instances for the `Env` class to configure the logging system and if no one is provided, the default values are meant to be loaded from the own API `Env` class. Maybe the `Env` class should be refactored to be a singleton and data class to be used as a configuration class but keeping backward compatibility. The logging system should be thread-safe and provide a consistent interface for search and gather logging messages.
*   **Suggested Mode:** `CODE`
*   **Detailed Steps:**
    1.  **Define Configuration Interface:** In `fbpyutils/logging.py`, define a clear interface or a method (e.g., `logging.configure(env_instance=None)`) that the logging system can use to receive configuration parameters. This method should be able to accept an instance of a client's `Env` class.
    2.  **Access Client `Env`:** Implement logic within `fbpyutils/logging.py` to attempt to import or receive an `Env` class instance from the client's application context. This might involve:
        *   A global configuration function in `fbpyutils.logging` that clients call with their `Env` instance.
        *   A mechanism to dynamically load a client's `Env` class if a specific environment variable or configuration path is set.
    3.  **Extract Logging Parameters:** From the client's `Env` instance (if provided), extract relevant logging configurations such as `log_level`, `log_format`, `log_file_path`, etc.
    4.  **Apply Default Values:** If no client `Env` instance is provided, or if specific logging parameters are not defined within the client's `Env`, ensure that `fbpyutils.logging` uses predefined default values for these parameters.
    5.  **Initialize Logging System:** Use the extracted (or default) parameters to configure the underlying Python `logging` module.
    6.  **Client Implementation Guidance:** Add a section to `SPEC.md` (from Task 3) or a new `USAGE.md` file explaining how external clients can create their own `Env` class (mirroring the structure of `fbpyutils.Env` for logging-related attributes) and how to pass it to `fbpyutils.logging` for custom configuration.
    7.  **Testing:** Develop unit tests to verify that the logging system correctly applies configurations from a client's `Env` class and falls back to default values when no client configuration is present.

---

## 5. Integrate the global logging system (`fbpyutils.logging`) into the following modules: `calendar`, `datetime`, `debug`, `file`, `ofx`, `process`, `string`, `xlsx`.

*   **Objective:** Replace any existing logging mechanisms or add new logging calls to utilize the global `fbpyutils.logging` system within the specified modules.
*   **Suggested Mode:** `CODE`
*   **Detailed Steps:**
    1.  For each module listed (`calendar`, `datetime`, `debug`, `file`, `ofx`, `process`, `string`, `xlsx`):
        a.  Open the corresponding `.py` file (e.g., `fbpyutils/calendar.py`).
        b.  Import the global logging system (e.g., `from fbpyutils import logging`).
        c.  Identify key points in the code where logging is appropriate (e.g., function entry/exit, error handling, warnings).
        d.  Replace legacy logging calls or add new calls using the `fbpyutils.logging` system (e.g., `logging.info()`, `logging.error()`).
        e.  Test the logging behavior within each module.

---

## 6. Move the legacy Logger class from `fbpyutils` into `fbpyutils.logging` and refactor it to use the global logging system in order to keep the API compatible. This will allow the removal of the legacy Logger class from `fbpyutils`. To logging system used in this library, refactor all use from Logger to the new logging system.

*   **Objective:** Consolidate logging functionality by relocating the legacy `Logger` class into the `fbpyutils.logging` module and refactoring it to leverage the new global logging system, thereby maintaining API compatibility and enabling the removal of the legacy class from the main package.
*   **Suggested Mode:** `CODE`
*   **Detailed Steps:**
    1.  Identify the current location of the legacy `Logger` class within `fbpyutils` (likely in `fbpyutils/__init__.py` or a separate file).
    2.  Move the definition of the `Logger` class to `fbpyutils/logging.py`.
    3.  Within the relocated `Logger` class, refactor its method implementations to internally utilize the global `fbpyutils.logging` system.
    4.  Ensure that the external API of the `Logger` class remains unchanged to prevent breaking compatibility for existing users.
    5.  Remove the legacy `Logger` class from its original location in `fbpyutils`.
    6.  Search the entire project for all occurrences of the legacy `Logger` class usage and refactor them to directly use the new global logging system, or through the refactored `Logger` class if strict compatibility is required.
    7.  Execute tests to confirm that all logging functionalities continue to operate correctly after the refactoring.

---

## 7. Add `get_base64_data_from` function to `file` module.

*   **Objective:** Add a new function to the `file` module that can retrieve data from a local file, a remote URL, or a base64-encoded string and return it as a base64-encoded string. This function will enhance the library's capability to handle different data sources seamlessly.
*   **Suggested Mode:** `CODE`
*   **Detailed Steps:**
    1.  **Add `requests` dependency:** Add the `requests` library to the `pyproject.toml` file to handle HTTP requests.
    2.  **Implement `get_base64_data_from`:**
        *   Create the function in `fbpyutils/file.py`.
        *   It should accept a `file_uri` (string) and an optional `timeout` (integer).
        *   Handle three cases for `file_uri`:
            *   If it's a valid local file path, read the file, encode it to base64, and return the string.
            *   If it's a URL (starts with `http://` or `https://`), download the content, encode it to base64, and return the string.
            *   Otherwise, assume the string is already base64 and validate it. If valid, return it; otherwise, log an error and return an empty string.
    3.  **Integrate Logging:** Add `fbpyutils.logging` calls for debugging, information, and error handling throughout the function.
    4.  **Add Unit Tests:**
        *   In `tests/test_file_file.py`, create new tests for `get_base64_data_from`.
        *   Test all three input scenarios (local file, URL, base64 string).
        *   Test error conditions (file not found, invalid URL, invalid base64 string).
        *   Use mocking for the `requests.get` call to avoid actual network requests during tests.
    5.  **Update Documentation:**
        *   Add the new function's specification to `SPEC.md`.
        *   Update `TODO.md` to mark this task as complete.
        *   Update the memory bank (`activeContext.md`, `progress.md`).
