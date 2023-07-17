import os
import platform
import pytest
from datetime import datetime

from fbpyutils.file import creation_date


@pytest.fixture(autouse=True)
def file_path(resources_path):
    return os.path.sep.join([resources_path, 'file1.txt'])

@pytest.fixture(autouse=True)
def file_timestamp():
    return 1689548343.3923748


@pytest.mark.parametrize('platform', ('Windows', 'Linux'))
def test_creation_date(mocker, file_path, file_timestamp, platform):
    mocker.patch('platform.system', return_value=platform)

    if platform == 'Windows':
        mocker.patch('os.path.getctime', return_value=file_timestamp)
    elif platform == 'Linux':
        class stat_result:
            st_birthtime = file_timestamp
        stat = stat_result()
        mocker.patch('os.stat', return_value=stat)
    
    expected_datetime = datetime.fromtimestamp(file_timestamp)
    # Act
    result = creation_date(file_path)
    # Assert
    assert result == expected_datetime


def test_creation_date_linux_no_birthtime(mocker, file_path, file_timestamp):
    mocker.patch('platform.system', return_value='Linux')
    class stat_result:
        st_mtime = file_timestamp
    stat = stat_result()
    mocker.patch('os.stat', return_value=stat)
    expected_datetime = datetime.fromtimestamp(file_timestamp)
    # Act
    result = creation_date(file_path)
    # Assert
    assert result == expected_datetime