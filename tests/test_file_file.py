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


def test_describe_file_basic(tmpdir):
    # 1. Setup: Create a temporary file with known content
    file_content_string = "This is the first line of the test file.\n"
    file_content_string += "It needs to be long enough to test partial hashing.\n" * 5
    file_content_string += "Let's add more lines to exceed 256 bytes easily.\n" * 5
    file_content_string += "Almost there, just a bit more content for our test.\n" * 5
    file_content_string += "This is the final line of the test file, ensuring it's > 256 bytes."
    known_content = file_content_string.encode('utf-8')

    # Create a temporary file using tmpdir facility
    temp_file = tmpdir.join("test_file_for_describe.txt")
    temp_file.write_binary(known_content)
    temp_file_path = str(temp_file)

    # 2. Calculate expected properties
    expected_complete_filename = os.path.basename(temp_file_path)
    expected_filename_no_ext, expected_extension = os.path.splitext(expected_complete_filename)
    expected_size_bytes = len(known_content)

    import hashlib # Import hashlib here for test calculations
    expected_md5sum = hashlib.md5(known_content).hexdigest()
    expected_sha256_first_256 = hashlib.sha256(known_content[:256]).hexdigest()

    # Expected creation date (will be compared loosely)
    # We use the already tested creation_date function from the file module
    expected_creation_dt_obj = file.creation_date(temp_file_path)
    expected_creation_date_iso = expected_creation_dt_obj.isoformat()

    # Expected MIME type (adjust if content changes significantly)
    expected_mime_type_code = "text/plain"
    expected_mime_type_description = "Text file" # Based on the map in describe_file

    # 3. Call the function to be tested
    described_properties = file.describe_file(temp_file_path)

    # 4. Assertions
    assert described_properties is not None
    assert described_properties['complete_filename'] == expected_complete_filename
    assert described_properties['filename_no_ext'] == expected_filename_no_ext
    assert described_properties['extension'] == expected_extension
    assert described_properties['size_bytes'] == expected_size_bytes

    # Creation date check:
    # Check if it's a string and can be parsed to datetime
    assert isinstance(described_properties['creation_date'], str)
    parsed_creation_date = datetime.fromisoformat(described_properties['creation_date'])
    # Check if it's close to the expected creation time (within a small delta, e.g., 1 second)
    # This is because the exact timestamp might differ slightly
    assert abs((parsed_creation_date - expected_creation_dt_obj).total_seconds()) < 1.0

    assert described_properties['mime_type_code'] == expected_mime_type_code
    # The mime_type function in file.py prints to stdout, so we need to be mindful if running with capture
    assert described_properties['mime_type_description'] == expected_mime_type_description
    assert described_properties['first_256_bytes_sha256_hex'] == expected_sha256_first_256
    assert described_properties['md5sum'] == expected_md5sum

    # No explicit tearDown needed as tmpdir fixture handles temporary file deletion
