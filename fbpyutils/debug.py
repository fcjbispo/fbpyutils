'''
Functions support code debuggin
'''


def debug(func):
    '''
    Decorator function to be used to debug execution of system functions.
    Prints all arguments used and the result value of the debugged functions.

    Use:

    @debug
    def myFunc(x, y, z):
        pass

        x
            The function to be decorated

        Return function decorator
    '''

    def _debug(*args, **kwargs):
        result = func(*args, **kwargs)
        print(
            f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}"
        )
        return result

    return _debug
