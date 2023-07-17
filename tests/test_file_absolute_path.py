import os

from fbpyutils.file import absolute_path


def xcut(x):
    return os.path.sep.join(
        x.split(os.path.sep)[:-1]
    )

def test_absolute_path_with_file_name():
    file_name = "test_file.txt"
    expected_path = os.path.realpath(
        __file__
    ).rsplit(os.path.sep, 1)[0]
    expected_path = os.path.sep.join(
        expected_path.split(os.path.sep)[:-1]
    )
    assert absolute_path(file_name) == expected_path


def test_absolute_path_with_empty_file_name():
    expected_path = os.path.realpath(
        __file__
    ).rsplit(os.path.sep, 1)[0]
    assert xcut(absolute_path("")) == xcut(expected_path)


def test_absolute_path_with_none_file_name():
    expected_path = os.path.realpath(
        __file__
    ).rsplit(os.path.sep, 1)[0]
    assert xcut(absolute_path(None)) == xcut(expected_path)
    