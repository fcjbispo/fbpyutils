# FBPyUtils Guide for Claude

## Build, Lint, and Test Commands
- Install: `uv pip install .`
- Run all tests: `pytest tests`
- Run single test: `pytest tests/test_file_name.py::test_function_name -v`
- Run tests with coverage: `pytest tests --cov=fbpyutils`

## Code Style Guidelines
- Python 3.11+ compatible code
- Use type hints consistently (param and return types)
- Follow PEP 8 style guidelines with descriptive naming
- Use comprehensive docstrings with Args/Returns sections
- Error handling via appropriate exceptions with messages
- Imports organization: standard lib, third-party, local
- Prefer logging over print statements
- Tests should be comprehensive with clear assertions
- Use Protocol types for interface definitions
- Use dataclasses for data containers when appropriate

## Conventions
- Functions use snake_case naming
- Classes use PascalCase naming
- Constants use UPPERCASE naming
- Use descriptive variable names
- Class methods should be type-annotated
- Always include proper exception handling