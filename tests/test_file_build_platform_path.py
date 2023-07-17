import os
import pytest

from fbpyutils.file import _is_windows, build_platform_path


def test_build_platform_path_on_windows(mocker):
    mocker.patch('fbpyutils.file._is_windows', return_value=True)
    os.path.sep = '\\'
    winroot = r"C:\Windows"
    otherroot = "/usr/local/"
    pathparts = ["folder", "file.txt"]
    expected_path = r"C:\Windows\folder\file.txt"
    assert build_platform_path(winroot, otherroot, pathparts) == expected_path


def test_build_platform_path_on_linux(mocker):
    mocker.patch('fbpyutils.file._is_windows', return_value=False)
    os.path.sep = '/'
    winroot = "C:\\Windows\\"
    otherroot = "/usr/local"
    pathparts = ["folder", "file.txt"]
    expected_path = "/usr/local/folder/file.txt"
    assert build_platform_path(winroot, otherroot, pathparts) == expected_path


def test_build_platform_path_with_empty_pathparts():
    winroot = "C:\\Windows\\"
    otherroot = "/usr/local/"
    pathparts = []
    expected_path = "C:\\Windows\\" if _is_windows() else "/usr/local/"
    assert build_platform_path(winroot, otherroot, pathparts) == expected_path


def test_build_platform_path_with_single_pathpart():
    winroot = "C:\\Windows\\"
    otherroot = "/usr/local"
    pathparts = ["file.txt"]
    expected_path = "C:\\Windows\\file.txt" if _is_windows() else "/usr/local/file.txt"
    assert build_platform_path(winroot, otherroot, pathparts) == expected_path