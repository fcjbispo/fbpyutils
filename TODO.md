# TODO List - Documentation vs Implementation Comparison

This file compares the features documented in `README.md` and `DOC.md` against the current implementation status and test coverage.

| Module     | Initialized? | Implemented? | Tested? (% Coverage) | Notes                                      |
| :--------- | :----------: | :----------: | :------------------: | :----------------------------------------- |
| calendar   | No           | Yes          | Yes (94.6%)          |                                            |
| datetime   | No           | Yes          | Yes (100%)           |                                            |
| debug      | No           | Yes          | Yes (84.6%)          |                                            |
| ofx        | No           | Yes          | Yes (55.7%)          | Low test coverage                          |
| process    | No           | Yes          | Yes (86.1%)          | Documented in README.md and DOC.md         |
| string     | No           | Yes          | Yes (100%)           |                                            |
| xlsx       | No           | Yes          | Yes (62.3%)          | Test coverage could be improved            |

**Legend:**

*   **Initialized?**: Indicates if the module is directly exposed via `fbpyutils/__init__.py`. Currently, no modules are explicitly imported in `__init__.py`.
*   **Implemented?**: Indicates if the corresponding `.py` file for the module exists in the `fbpyutils` directory.
*   **Tested? (% Coverage)**: Indicates if tests exist and the line coverage percentage reported by `coverage.xml`.

**Next Steps:**

*   [ ] Improve test coverage for the `ofx` and `xlsx` modules.
*   [ ] Consider adding modules to `__init__.py` for easier import (`import fbpyutils.calendar` vs `from fbpyutils import calendar`).
*   [ ] Create a `SPEC.md` file to formally define specifications.
