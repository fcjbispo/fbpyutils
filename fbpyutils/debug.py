'''
Functions support code debugging.
'''
import traceback

from fbpyutils.logging import Logger


def debug(func):
    '''
    Decorator function used to debug the execution of system functions.
    Prints all arguments used and the result value of the debugged functions.
     Usage:
     @debug
     def myFunc(x, y, z):
         pass
     Parameters:
        func: The function to be decorated.
     Returns:
        The function decorator.
    '''
    def _debug(*args, **kwargs):
        Logger.debug(f"Calling function: {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        Logger.debug(f"Function {func.__name__} returned: {result}")
        return result

    return _debug


def debug_info(x: Exception):
    '''
    Return extra exception/execution info for debug.
    '''
    Logger.debug(f"Getting debug info for exception: {x.__str__()}")
    try:
        info = f"{x.__str__()}: {traceback.format_exc()}."
        Logger.debug(f"Successfully retrieved debug info: {info}")
    except Exception as e:
        info = f"{x.__str__()}: Unable to get debug info: {e}"
        Logger.error(f"Failed to retrieve debug info for exception {x.__str__()}: {e}")

    return info
