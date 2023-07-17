import sys
from fbpyutils.file import _is_windows


def test_is_windows():
    if sys.platform.upper().startswith('WIN'):
        assert _is_windows() == True


def test_is_not_windows():
    if not sys.platform.upper().startswith('WIN'):
        assert _is_windows() == False


def test_is_windows_with_different_platform():
    sys.platform = 'linux'
    assert _is_windows() == False


def test_is_windows_with_different_platform_2():
    sys.platform = 'darwin'
    assert _is_windows() == False


def test_is_windows_with_different_platform_3():
    sys.platform = 'win32'
    assert _is_windows() == True


def test_is_windows_with_different_platform_4():
    sys.platform = 'windows'
    assert _is_windows() == True