import pytest
from fbpyutils import debug


def test_debug_decorator(capsys):
    @debug.debug
    def example_function(a, b):
        return a + b

    result = example_function(3, 5)
    captured = capsys.readouterr()
    assert "example_function(args: (3, 5), kwargs: {}) -> 8" in captured.out
    assert result == 8


def test_debug_info():
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        info = debug.debug_info(e)
        assert info.startswith("Test exception:")
