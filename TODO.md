# TODO List

This file tracks the project's releases, detailing completed tasks and outlining future work.

---

## Release History

### **[v1.6.3] - 2025-07-03**

**Status: Ready for Deploy**

This release focused on improving test coverage, formalizing specifications, and implementing a robust, configurable logging system.

**Completed Tasks:**

*   **[X] Improve test coverage for `ofx` and `xlsx` modules:**
    *   Increased test coverage for `ofx` to >90%.
    *   Increased test coverage for `xlsx` to >90%.
*   **[X] Add modules to `__init__.py`:**
    *   Modules are now directly accessible (e.g., `from fbpyutils import file`).
*   **[X] Create `SPEC.md` file:**
    *   A formal specification document has been created and populated.
*   **[X] Implement and Integrate Global Logging System:**
    *   The `fbpyutils.logging` system is now configurable via a client's `Env` class.
    *   Logging has been integrated into `calendar`, `datetime`, `debug`, `file`, `ofx`, `process`, `string`, and `xlsx`.
*   **[X] Refactor Legacy Logger:**
    *   The legacy `Logger` class was moved to `fbpyutils.logging` and refactored to maintain API compatibility.
*   **[X] Add `get_base64_data_from` to `file` module:**
    *   New function implemented with full test coverage and documentation.

---

## **Next Release (v1.7.0) - Pending**

**Goals:**
*   Achieve 100% test coverage for all modules.
*   Refine documentation and examples.

**Pending Tasks:**

*   [ ] **Improve test coverage for remaining modules:**
    *   [ ] `debug` (Current: 84.6%)
    *   [ ] `process` (Current: 86.1%)
*   [ ] **Review and enhance documentation:**
    *   [ ] Add more usage examples to `DOC.md` and `SPEC.md`.
    *   [ ] Review all docstrings for clarity and completeness.
