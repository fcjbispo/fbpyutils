import pytest
import json
import os
from typing import Dict

from fbpyutils.file import load_from_json, write_to_json


@pytest.fixture(autouse=True)
def file_path(resources_path):
    return os.path.sep.join([resources_path, 'file1.json'])


def test_load_from_json(file_path):
    # Arrange
    expected_data = {"key": "value"}
    # Create a temporary JSON file
    with open(file_path, 'w') as json_file:
        json.dump(expected_data, json_file)
    # Act
    result = load_from_json(file_path)
    # Assert
    assert result == expected_data
    # Clean up the temporary file
    os.remove(file_path)


def test_write_to_json(file_path):
    # Arrange
    data = {"key": "value"}
    # Act
    write_to_json(data, file_path)
    # Assert
    assert os.path.exists(file_path)
    # Clean up the created file
    os.remove(file_path)


def test_write_to_json_with_prettify(file_path):
    # Arrange
    data = {"key": "value"}
    # Act
    write_to_json(data, file_path, prettify=True)
    # Assert
    assert os.path.exists(file_path)
    # Clean up the created file
    os.remove(file_path)


def test_write_to_json_without_prettify(file_path):
    # Arrange
    data = {"key": "value"}
    # Act
    write_to_json(data, file_path, prettify=False)
    # Assert
    assert os.path.exists(file_path)
    # Clean up the created file
    os.remove(file_path)