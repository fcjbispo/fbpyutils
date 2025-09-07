# FBPyUtils Library - TODO List

This document tracks the implementation status of features defined in SPEC.md compared to the actual implementation.

- Make logger uses the home user dir as log file storage by default or by expanding the char ~ on the log path config if present.
- Refactor SPEC using HIGH LEVEL SPECIFICATION
- Refactor README
- Refactor DOC or create other document to use unified format suitable to used as resource in MCP server (context7)
- **logger**
  - Remove output log on console
  - Increase coverage tests
  - Implement functional tests
  - Overwrite log level, log dir with env vars FBPY_LOG_LEVEL, etc.
  - Add suport to write logs to databases, queues..