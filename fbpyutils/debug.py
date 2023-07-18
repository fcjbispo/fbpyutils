'''
Functions support code debugging.
'''


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
        result = func(*args, **kwargs)
        print(
            f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}"
        )
        return result

    return _debug
