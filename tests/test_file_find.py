import os
import pytest
from pathlib import Path

from fbpyutils.file import find


def test_find_with_default_mask(resources_path, expected_files):
   result = find(resources_path)
   # Assert
   assert result == expected_files


def test_find_with_custom_mask(resources_path, expected_files):
   # Arrange
   expected_files = [
      f for f in expected_files if f.endswith('.txt')
   ]
   # Act
   result = find(resources_path, '*.txt')
   # Assert
   assert result == expected_files


def test_find_with_nonexistent_folder():
   # Arrange
   expected_files = []
   # Act
   result = find('nonexistent/folder')
   # Assert
   assert result == expected_files


def test_find_with_empty_folder(resources_path):
   # Arrange
   expected_files = []
   # Act
   result = find(os.path.sep.join([resources_path, 'pasta2']))
   # Assert
   assert result == expected_files
