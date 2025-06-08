# TODO List - Documentation vs Implementation Comparison

This file compares the features documented in `README.md` and `DOC.md` against the current implementation status and test coverage.

| Module     | Initialized? | Implemented? | Tested? (% Coverage) | Notes                                            |
| :--------- | :----------: | :----------: | :------------------: | :----------------------------------------------- |
| calendar   | No           | Yes          | Yes (94.6%)          |                                                  |
| datetime   | No           | Yes          | Yes (100%)           |                                                  |
| debug      | No           | Yes          | Yes (84.6%)          |                                                  |
| ofx        | No           | Yes          | Yes (55.7%)          | Low test coverage                                |
| file       | No           | Yes          | Yes (90.0%)          | Documented in README.md and DOC.md               |
| process    | No           | Yes          | Yes (86.1%)          | Documented in README.md and DOC.md               |
| string     | No           | Yes          | Yes (100%)           |                                                  |
| xlsx       | No           | Yes          | Yes (62.3%)          | Test coverage could be improved                  |
| logging    | Yes          | Yes          | N/A                  | Global logging system implemented and documented |

**Legend:**

*   **Initialized?**: Indicates if the module is directly exposed via `fbpyutils/__init__.py`. Currently, no modules are explicitly imported in `__init__.py`.
*   **Implemented?**: Indicates if the corresponding `.py` file for the module exists in the `fbpyutils` directory.
*   **Tested? (% Coverage)**: Indicates if tests exist and the line coverage percentage reported by `coverage.xml`.

**Next Steps:**

*   [ ] Improve test coverage for the `ofx` and `xlsx` modules.
*   [ ] Consider adding modules to `__init__.py` for easier import (`import fbpyutils.calendar` vs `from fbpyutils import calendar`).
*   [ ] Create a `SPEC.md` file to formally define specifications.
*   [ ] Implement the global logging system.
*   [ ] Integrate the global logging system into the following modules:
    *   [ ] `calendar`
    *   [ ] `datetime`
    *   [ ] `debug`
    *   [X] `file` (Completed)
    *   [ ] `ofx`
    *   [ ] `process`
    *   [ ] `string`
    *   [ ] `xlsx`
*   [ ] Refactor the legacy Logger class.


**Next Steps Details:**

*   Implement the global logging system:
    *  Implement a global logging system (`fbpyutils.logging`) as configurable via an instance of a class Env from `fbpyutils` in order to make it reusable by API clients. The API clients should be provide its own instances for the Env class to configure the logging system and if no one is provided, the Default values are meant to be loaded from the own api Env class. Maybe the Env class should be refactored to be a singleton and data class to be used as a configuration class but keeping backward compatibility. The logging system should be thread-safe and provide a consistent interface for search and gather logging messages.
*   Refactor the legacy Logger class:
    *  Refactor the existing Logger class to use the global logging system but keeping its methods and functionalities in order to keep backward compatibility. Check to avoid circular dependencies.
