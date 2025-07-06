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
    # Test known file type
    text_file = tmpdir.join("test.txt")
    text_file.write("content")
    assert file.mime_type(str(text_file)) == "text/plain"

    # Test unknown file type
    unknown_file = tmpdir.join("test.xyz")
    unknown_file.write("content")
    assert file.mime_type(str(unknown_file)) == "application/octet-stream"

    # Test non-existent file
    non_existent_file = str(tmpdir.join("non_existent.file"))
    assert file.mime_type(non_existent_file) == "file_not_found"

    # Test directory
    dir_path = str(tmpdir.mkdir("test_dir"))
    assert file.mime_type(dir_path) == 'directory'



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


def test_get_file_head_content_text_format(tmpdir):
    # Test with text output format
    file_content = "This is a test file with some content."
    test_file = tmpdir.join("head_test_text.txt")
    test_file.write(file_content)

    # Read less than full content
    head_content = file.get_file_head_content(str(test_file), num_bytes=10, output_format='text')
    assert head_content == file_content[:10]
    assert isinstance(head_content, str)

    # Read more than full content (should return full content)
    head_content_full = file.get_file_head_content(str(test_file), num_bytes=100, output_format='text')
    assert head_content_full == file_content
    assert isinstance(head_content_full, str)

    # Test with specific encoding and errors
    # Test with specific encoding and errors
    # Create a file with invalid UTF-8 characters
    # A valid UTF-8 string with an invalid byte (0xff) inserted
    invalid_utf8_content = b"Hello \xff World"
    invalid_utf8_file = tmpdir.join("invalid_utf8.txt")
    invalid_utf8_file.write_binary(invalid_utf8_content)

    # Test 'replace' error handling
    head_replace = file.get_file_head_content(str(invalid_utf8_file), output_format='text', encoding='utf-8', errors='replace')
    assert '�' in head_replace # Expect replacement characters
    assert "Hello � World" == head_replace # Ensure the valid parts are there

    # Test 'ignore' error handling
    head_ignore = file.get_file_head_content(str(invalid_utf8_file), output_format='text', encoding='utf-8', errors='ignore')
    assert 'Hello  World' == head_ignore # Expect problematic chars to be ignored

    # Test 'strict' error handling (should raise UnicodeDecodeError)
    # The function now catches the exception and returns None, so we check for that
    assert file.get_file_head_content(str(invalid_utf8_file), output_format='text', encoding='utf-8', errors='strict') is None


def test_get_file_head_content_bytes_format(tmpdir):
    # Test with bytes output format
    file_content = b"This is raw bytes content."
    test_file = tmpdir.join("head_test_bytes.bin")
    test_file.write_binary(file_content)

    head_content = file.get_file_head_content(str(test_file), num_bytes=10, output_format='bytes')
    assert head_content == file_content[:10]
    assert isinstance(head_content, bytes)

    head_content_full = file.get_file_head_content(str(test_file), num_bytes=100, output_format='bytes')
    assert head_content_full == file_content
    assert isinstance(head_content_full, bytes)


def test_get_file_head_content_base64_format(tmpdir):
    # Test with base64 output format
    import base64
    file_content = b"Binary data for base64 encoding."
    test_file = tmpdir.join("head_test_base64.bin")
    test_file.write_binary(file_content)

    expected_base64 = base64.b64encode(file_content[:10]).decode('ascii')
    head_content = file.get_file_head_content(str(test_file), num_bytes=10, output_format='base64')
    assert head_content == expected_base64
    assert isinstance(head_content, str)

    expected_base64_full = base64.b64encode(file_content).decode('ascii')
    head_content_full = file.get_file_head_content(str(test_file), num_bytes=100, output_format='base64')
    assert head_content_full == expected_base64_full
    assert isinstance(head_content_full, str)


def test_get_file_head_content_non_existent_file(tmpdir):
    # Test with a non-existent file
    non_existent_file = tmpdir.join("non_existent.txt")
    head_content = file.get_file_head_content(str(non_existent_file))
    assert head_content is None


def test_get_file_head_content_empty_file(tmpdir):
    # Test with an empty file
    empty_file = tmpdir.join("empty.txt")
    empty_file.write("")

    head_content_text = file.get_file_head_content(str(empty_file), output_format='text')
    assert head_content_text == ""
    assert isinstance(head_content_text, str)

    head_content_bytes = file.get_file_head_content(str(empty_file), output_format='bytes')
    assert head_content_bytes == b""
    assert isinstance(head_content_bytes, bytes)

    head_content_base64 = file.get_file_head_content(str(empty_file), output_format='base64')
    assert head_content_base64 == ""
    assert isinstance(head_content_base64, str)


def test_get_file_head_content_invalid_output_format(tmpdir):
    # Test with an invalid output format
    test_file = tmpdir.join("invalid_format.txt")
    test_file.write("some content")

    head_content = file.get_file_head_content(str(test_file), output_format='invalid_format')
    assert head_content is None



def test_get_base64_data_from_local_file(tmpdir):
    """
    Tests if get_base64_data_from correctly processes a local file.
    """
    # Setup: Create a temporary file with known content
    file_content = b"test content for local file"
    test_file = tmpdir.join("test_local.txt")
    test_file.write_binary(file_content)
    
    # Expected base64 encoding
    import base64
    expected_base64 = base64.b64encode(file_content).decode('utf-8')

    # Call the function
    result = file.get_base64_data_from(str(test_file))

    # Assert
    assert result == expected_base64


def test_get_base64_data_from_remote_url(mocker):
    """
    Tests if get_base64_data_from correctly processes a remote URL.
    """
    # Setup: Mock requests.get
    file_content = b"test content from remote url"
    import base64
    expected_base64 = base64.b64encode(file_content).decode('utf-8')
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = file_content
    mock_response.raise_for_status.return_value = None
    
    import requests
    mocker.patch('requests.get', return_value=mock_response)

    # Call the function
    remote_url = "http://example.com/test.txt"
    result = file.get_base64_data_from(remote_url)

    # Assert
    assert result == expected_base64
    requests.get.assert_called_once_with(remote_url, timeout=300)


def test_get_base64_data_from_base64_string():
    """
    Tests if get_base64_data_from correctly handles a valid base64 string.
    """
    # Setup: A valid base64 string
    base64_string = "dGVzdCBjb250ZW50IGZvciBiYXNlNjQgc3RyaW5n" # "test content for base64 string"
    
    # Call the function
    result = file.get_base64_data_from(base64_string)

    # Assert
    assert result == base64_string


def test_get_base64_data_from_invalid_base64_string():
    """
    Tests if get_base64_data_from returns an empty string for an invalid base64 string.
    """
    # Setup: An invalid base64 string
    invalid_base64_string = "this is not base64"
    
    # Call the function
    result = file.get_base64_data_from(invalid_base64_string)

    # Assert
    assert result == ""


def test_get_base64_data_from_file_not_found():
    """
    Tests if get_base64_data_from returns an empty string for a non-existent file.
    """
    # Call the function with a path that does not exist
    result = file.get_base64_data_from("non_existent_file.txt")

    # Assert
    assert result == ""


def test_get_base64_data_from_remote_url_error(mocker):
    """
    Tests if get_base64_data_from returns an empty string when a remote URL request fails.
    """
    # Setup: Mock requests.get to raise an exception
    import requests
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Test error"))

    # Call the function
    remote_url = "http://example.com/non_existent.txt"
    result = file.get_base64_data_from(remote_url)

    # Assert
    assert result == ""



def test_get_base64_data_from_io_error(mocker):
    """
    Tests if get_base64_data_from handles IOError when reading a local file.
    """
    mocker.patch('builtins.open', side_effect=IOError("Test I/O Error"))
    result = file.get_base64_data_from("any_local_file.txt")
    assert result == ""


def test_get_base64_data_from_unexpected_error_local(mocker):
    """
    Tests if get_base64_data_from handles unexpected errors for local files.
    """
    mocker.patch('builtins.open', side_effect=Exception("Unexpected Test Error"))
    result = file.get_base64_data_from("any_local_file.txt")
    assert result == ""


def test_get_base64_data_from_unexpected_error_remote(mocker):
    """
    Tests if get_base64_data_from handles unexpected errors for remote files.
    """
    import requests
    mocker.patch('requests.get', side_effect=Exception("Unexpected Remote Test Error"))
    result = file.get_base64_data_from("http://example.com/file.txt")
    assert result == ""


def test_get_base64_data_from_invalid_base64_padding():
    """
    Tests if get_base64_data_from correctly handles base64 with missing padding.
    """
    # A valid base64 string with padding removed
    base64_string_no_padding = "dGVzdA" # "test"
    result = file.get_base64_data_from(base64_string_no_padding)
    assert result == "dGVzdA=="



def test_load_from_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        file.load_from_json("non_existent.json")


def test_load_from_json_decode_error(tmpdir):
    json_file = tmpdir.join("invalid.json")
    json_file.write("{'key': 'value'}") # Invalid JSON
    with pytest.raises(json.JSONDecodeError):
        file.load_from_json(str(json_file))


def test_write_to_json_io_error(mocker):
    mocker.patch('builtins.open', side_effect=IOError("Disk full"))
    with pytest.raises(IOError):
        file.write_to_json({"a": 1}, "any/path/file.json")


def test_contents_file_not_found():
    with pytest.raises(FileNotFoundError):
        file.contents("non_existent.txt")


def test_mime_type_directory(tmpdir):
    dir_path = str(tmpdir.mkdir("test_dir"))
    assert file.mime_type(dir_path) == 'directory'

def test_get_base64_data_from_unexpected_error_base64(mocker):
    """
    Tests if get_base64_data_from handles unexpected errors during base64 validation.
    """
    mocker.patch('base64.b64decode', side_effect=Exception("Unexpected Base64 Error"))
    result = file.get_base64_data_from("dGVzdA==")
    assert result == ""


def test_find_non_recursive(tmpdir):
    # Create a nested structure
    dir1 = tmpdir.mkdir("dir1")
    dir2 = dir1.mkdir("dir2")
    file1 = tmpdir.join("file1.txt")
    file2 = dir1.join("file2.txt")
    file3 = dir2.join("file3.txt")
    file1.write("content")
    file2.write("content")
    file3.write("content")

    # Non-recursive search in the root
    found_files = file.find(str(tmpdir), mask="*.txt", recurse=False)
    assert len(found_files) == 1
    assert str(file1) in found_files
    assert str(file2) not in found_files
    assert str(file3) not in found_files

    # Non-recursive search in a subdirectory
    found_files_dir1 = file.find(str(dir1), mask="*.txt", recurse=False)
    assert len(found_files_dir1) == 1
    assert str(file2) in found_files_dir1


def test_find_recursive_and_parallel(tmpdir):
    # Create a more complex structure for parallel testing
    dir1 = tmpdir.mkdir("dir1")
    dir2 = tmpdir.mkdir("dir2")
    dir3 = dir1.mkdir("dir3")

    f1 = tmpdir.join("f1.log")
    f2 = dir1.join("f2.log")
    f3 = dir2.join("f3.log")
    f4 = dir3.join("f4.log")
    f5 = dir3.join("f5.txt") # Different extension

    for f in [f1, f2, f3, f4, f5]:
        f.write("log content")

    # Run parallel recursive search
    found_files = file.find(str(tmpdir), mask="*.log", recurse=True, parallel=True)
    
    expected_files = sorted([str(f1), str(f2), str(f3), str(f4)])
    
    assert found_files == expected_files


def test_find_returns_sorted_and_unique_list(tmpdir):
    # Create files with names that would be out of order if not sorted
    tmpdir.join("c.txt").write("c")
    tmpdir.join("a.txt").write("a")
    tmpdir.join("b.txt").write("b")

    # Create a duplicate entry scenario for parallel execution
    dir1 = tmpdir.mkdir("dir1")
    dir1.join("a.txt").write("a_dupe") # Same filename as in root

    found_files_seq = file.find(str(tmpdir), mask="*.txt", recurse=True, parallel=False)
    found_files_par = file.find(str(tmpdir), mask="*.txt", recurse=True, parallel=True)

    expected = sorted([
        str(tmpdir.join("a.txt")),
        str(tmpdir.join("b.txt")),
        str(tmpdir.join("c.txt")),
        str(dir1.join("a.txt"))
    ])

    assert found_files_seq == expected
    assert found_files_par == expected


def test_find_empty_directory(tmpdir):
    empty_dir = tmpdir.mkdir("empty")
    assert file.find(str(empty_dir)) == []
    assert file.find(str(empty_dir), recurse=False) == []
    assert file.find(str(empty_dir), parallel=True) == []


def test_find_non_existent_directory(tmpdir):
    non_existent_path = str(tmpdir.join("non_existent"))
    assert file.find(non_existent_path) == []

