'''
Functions support code debugging.
'''
import traceback

from fbpyutils import get_logger


_logger = get_logger()


def debug(func):
    """
    A decorator that logs the execution of a function.

    This decorator logs the function name, its arguments, and its return value
    at the DEBUG level.

    Args:
        func: The function to be decorated.

    Returns:
        The wrapped function with debugging logs.
    """
    def _debug(*args, **kwargs):
        _logger.debug(f"Calling function: {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        _logger.debug(f"Function {func.__name__} returned: {result}")
        return result

    return _debug


def debug_info(x: Exception) -> str:
    """
    Get detailed debug information from an exception object.

    This function extracts the exception message and formats the traceback
    into a single string for logging or debugging purposes.

    Args:
        x: The exception object.

    Returns:
        A formatted string containing the exception message and traceback.
        Format: "{exception_message}: {traceback_info}."
    """
    _logger.debug(f"Getting debug info for exception: {x.__str__()}")
    try:
        info = f"{x.__str__()}: {traceback.format_exc()}."
        _logger.debug(f"Successfully retrieved debug info: {info}")
    except Exception as e:
        info = f"{x.__str__()}: Unable to get debug info: {e}"
        _logger.error(f"Failed to retrieve debug info for exception {x.__str__()}: {e}")

    return info
