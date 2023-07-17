import pytest
import os

from fbpyutils.file import contents


@pytest.fixture(autouse=True)
def file_path(resources_path):
    return os.path.sep.join([resources_path, 'file4.txt'])


def test_contents_existing_file(file_path):
    # Arrange
    expected_content = b"Hello, World!"
    # Create a temporary file with content
    with open(file_path, 'wb') as file:
        file.write(expected_content)
    # Act
    result = contents(file_path)
    # Assert
    assert result == expected_content
    # Clean up the temporary file
    os.remove(file_path)


def test_contents_nonexisting_file(file_path):
    # Arrange
    file_path = "path/to/nonexisting_file.txt"
    # Act and Assert
    with pytest.raises(FileNotFoundError):
        contents(file_path)