import pytest
import os
import platform
from datetime import datetime

from fbpyutils.file import creation_date


@pytest.fixture(autouse=True)
def file_path(resources_path):
    return os.path.sep.join([resources_path, 'file.txt'])


def test_creation_date_windows(file_path):
    creation_time = 1234567890
    os.path.getctime = lambda x: creation_time
    expected_datetime = datetime.fromtimestamp(creation_time)
    # Act
    result = creation_date(file_path)
    # Assert
    assert result == expected_datetime


def test_creation_date_linux(file_path):
    creation_time = 1234567890
    modification_time = 9876543210
    os.path.getctime = lambda x: modification_time
    os.stat = lambda x: os.stat_result((0, 0, 0, 0, 0, 0, modification_time, 0, 0, creation_time))
    expected_datetime = datetime.fromtimestamp(modification_time)
    # Act
    result = creation_date(file_path)
    # Assert
    assert result == expected_datetime


def test_creation_date_linux_no_birthtime(file_path):
    modification_time = 9876543210
    os.path.getctime = lambda x: modification_time
    os.stat = lambda x: os.stat_result((0, 0, 0, 0, 0, 0, modification_time, 0, 0, modification_time))
    expected_datetime = datetime.fromtimestamp(modification_time)
    # Act
    result = creation_date(file_path)
    # Assert
    assert result == expected_datetime