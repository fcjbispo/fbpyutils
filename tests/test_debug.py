import pytest
from fbpyutils.debug import debug


def test_debug():
    # test debug function
    @debug
    def my_func(x, y, z):
        return x + y + z

    result = my_func(1, 2, 3)
    assert result == 6


def test_debug_with_kwargs():
    # test debug function with kwargs
    @debug
    def my_func(x, y, z):
        return x + y + z

    result = my_func(x=1, y=2, z=3)
    assert result == 6
