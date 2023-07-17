import pytest
import os
from unittest.mock import patch

from fbpyutils.file import mime_type


@pytest.fixture(autouse=True)
def file_path(resources_path):
    return os.path.sep.join([resources_path, 'file4.txt'])


@pytest.fixture(autouse=True)
def directory_path(resources_path):
    return os.path.sep.join([resources_path, 'pasta3'])


def test_mime_type_existing_file(file_path):
    # Arrange
    expected_mime_type = "text/plain"
    # Create a temporary file
    with open(file_path, 'w') as file:
        file.write("Hello, World!")
    # Act
    result = mime_type(file_path)
    # Assert
    assert result == expected_mime_type
    # Clean up the temporary file
    # os.remove(file_path)


def test_mime_type_directory(directory_path):
    # Create a temporary directory
    os.makedirs(directory_path)
    # Act
    result = mime_type(directory_path)
    # Assert
    assert result == "directory"
    # Clean up the temporary directory
    os.rmdir(directory_path)


def test_mime_type_nonexisting_file():
    # Arrange
    file_path = "path/to/nonexisting_file.txt"
    # Act
    result = mime_type(file_path)
    # Assert
    assert result == "file_not_found"


@patch('magic.from_file')
@pytest.mark.parametrize('exception', (IsADirectoryError, FileNotFoundError))
def test_mime_type_exception(mock_from_file, file_path, exception):
    # Mock the magic.from_file function to raise an IsADirectoryError
    mock_from_file.side_effect = exception
    # Act
    result = mime_type(file_path)
    # Assert
    expected_result = "directory" if exception is IsADirectoryError else "file_not_found" 
    assert result == expected_result