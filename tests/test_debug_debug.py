import pytest
from fbpyutils import debug


def test_debug_decorator(mocker):
    mock_logger_debug = mocker.patch('fbpyutils.debug.Logger.debug')

    @debug.debug
    def example_function(a, b):
        return a + b

    result = example_function(3, 5)

    assert result == 8
    
    mock_logger_debug.assert_any_call("Calling function: example_function with args: (3, 5), kwargs: {}")
    mock_logger_debug.assert_any_call("Function example_function returned: 8")


def test_debug_info():
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        info = debug.debug_info(e)
        assert info.startswith("Test exception:")
