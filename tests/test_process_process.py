import os
import time
import pytest
import tempfile
import pickle
import multiprocessing
from unittest import mock
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from fbpyutils import process
from fbpyutils.env import Env  # Import Env from its new module
from fbpyutils.file import creation_date  # Re-added import
from fbpyutils.string import hash_string

def dummy_process_func(param):
    return True, None, f"processed {param}"

def dummy_file_process_func(file_path):
    return file_path, True, None, f"processed {file_path}"

def dummy_session_process_func(param1, param2):
    return (True, None, f"processed {param1}, {param2}", "result_data")

def error_process_func(param):
    raise ValueError("Processing error")

def error_file_process_func(file_path):
    return file_path, False, "processing failed", None

def error_file_process_func_remove_control(file_path):
    return file_path, False, "processing failed", None

def error_session_process_func(param1, param2):
    return False, "session processing failed", None

def error_session_process_func_remove_control(param1, param2):
    return False, "session processing failed", None

@pytest.fixture
def mock_env_fixture(tmpdir):
    """Provides a mock Env instance where USER_APP_FOLDER is set to tmpdir."""
    with mock.patch('fbpyutils.process.Env', autospec=True) as MockEnvClass:
        mock_env_instance = MockEnvClass.return_value
        mock_env_instance.USER_APP_FOLDER = str(tmpdir)

        yield mock_env_instance

def test_get_available_cpu_count():
    with mock.patch("multiprocessing.cpu_count") as mock_cpu_count:
        mock_cpu_count.return_value = 4
        assert process.Process.get_available_cpu_count() == 4

    with mock.patch("multiprocessing.cpu_count", side_effect=NotImplementedError):
        assert process.Process.get_available_cpu_count() == 1

def test_is_parallelizable(caplog):
    import logging

    # Configure root logger to capture messages
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set root logger level to DEBUG or INFO
    root_logger.addHandler(logging.StreamHandler())  # Add a basic handler
