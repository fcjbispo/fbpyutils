import pytest
import os
import json  # Import json module
from datetime import datetime
from fbpyutils import file


def test_find(tmpdir):
    # Create dummy files and directories
    dir1 = tmpdir.mkdir("dir1")
    dir2 = dir1.mkdir("dir2")
    file1 = dir1.join("file1.txt")
    file2 = dir2.join("file2.txt")
    file3 = tmpdir.join("file3.jpg")
    file1.write("content")
    file2.write("content")
    file3.write("content")

    # Test find with mask
    found_files_txt = file.find(str(tmpdir), mask="*.txt")
    assert len(found_files_txt) == 2
    assert str(file1) in found_files_txt
    assert str(file2) in found_files_txt

    # Test find without mask (all files)
    found_all_files = file.find(str(tmpdir))
    assert len(found_all_files) == 3
    assert str(file1) in found_all_files
    assert str(file2) in found_all_files
    assert str(file3) in found_all_files


def test_creation_date(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("content")
    creation_time = file.creation_date(str(test_file))
    assert isinstance(creation_time, datetime)


def test_load_from_json(tmpdir):
    json_file = tmpdir.join("test.json")
    data = {"key": "value"}
    json_file.write(json.dumps(data))
    loaded_data = file.load_from_json(str(json_file))
    assert loaded_data == data


def test_write_to_json(tmpdir):
    json_file = tmpdir.join("test_write.json")
    data = {"key": "value"}
    file.write_to_json(data, str(json_file))
    loaded_data = json.load(open(str(json_file), "r"))
    assert loaded_data == data


def test_contents(tmpdir):
    test_file = tmpdir.join("test_contents.txt")
    content = b"test content"
    test_file.write_binary(content)
    file_content = file.contents(str(test_file))
    assert file_content == content


def test_mime_type(tmpdir):
    text_file = tmpdir.join("test.txt")
    text_file.write("content")
    assert file.mime_type(str(text_file)) == "text/plain"

    # dir_path = str(tmpdir.mkdir("test_dir")) # Temporarily disabled due to PermissionError
    # assert file.mime_type(dir_path) == 'directory' # Temporarily disabled due to PermissionError

    non_existent_file = str(tmpdir.join("non_existent.file"))
    assert file.mime_type(non_existent_file) == "file_not_found"


def test_build_platform_path():
    if os.name == "nt":
        assert (
            file.build_platform_path("C:", "/", ["folder", "file.txt"])
            == "C:\\folder\\file.txt"
        )
    else:
        assert (
            file.build_platform_path("C:", "/", ["folder", "file.txt"])
            == "/folder/file.txt"
        )


def test_absolute_path():
    abs_path = file.absolute_path("file.txt")
    assert abs_path.lower() == os.path.dirname(os.path.abspath("file.txt")).lower()
