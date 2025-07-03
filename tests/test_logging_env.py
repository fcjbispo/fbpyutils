import pytest
import os
import json
import logging
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Temporarily adjust sys.path to import modules from fbpyutils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fbpyutils.env import Env
from fbpyutils.logging import Logger

# Define a fixture for a temporary app.json content
@pytest.fixture
def temp_app_json_content():
    return {
        "app": {
            "name": "TestApp",
            "version": "1.0.0",
            "environment": "test",
            "appcode": "TEST",
            "year": 2024
        },
        "logging": {
            "log_level": "DEBUG",
            "log_format": "TEST_FORMAT - %(message)s",
            "log_file_path": "test_logs/test_app.log"
        }
    }

# Fixture to reset Logger configuration after each test
@pytest.fixture(autouse=True)
def reset_logger_config():
    Logger._is_configured = False
    Logger._logger.handlers.clear()
    yield
    Logger._is_configured = False
    Logger._logger.handlers.clear()

# Mock os.path.expanduser for consistent user folder paths
@pytest.fixture(autouse=True)
def mock_expanduser():
    with patch('os.path.expanduser', return_value='/mock/home/user'):
        yield

# Mock os.makedirs to prevent actual directory creation
@pytest.fixture(autouse=True)
def mock_makedirs():
    with patch('os.makedirs') as mock_make:
        yield mock_make

# Mock os.path.exists for file and directory checks
@pytest.fixture(autouse=True)
def mock_path_exists_and_isdir():
    # Paths that should exist
    _existing_paths = set()
    # Paths that should be considered directories
    _directory_paths = set()

    # Add the fbpyutils/app.json path to existing paths
    _existing_paths.add(os.path.normpath(os.path.join('fbpyutils', 'app.json')))

    def mock_exists(path):
        # Normalize path for consistent comparison
        normalized_path = os.path.normpath(path)
        if normalized_path in _existing_paths or normalized_path in _directory_paths:
            return True
        # Special handling for log directories that might be created
        if 'test_logs' in normalized_path or 'new_logs' in normalized_path:
            return True # Assume log directories exist for the purpose of these tests
        return False

    def mock_isdir(path):
        normalized_path = os.path.normpath(path)
        if normalized_path in _directory_paths:
            return True
        if 'test_logs' in normalized_path or 'new_logs' in normalized_path:
            return True # Assume log directories are directories
        return False

    with patch('os.path.exists', side_effect=mock_exists) as mock_e, \
         patch('os.path.isdir', side_effect=mock_isdir) as mock_d:
        yield mock_e, mock_d, _existing_paths, _directory_paths # Yield mocks and sets for test manipulation

# Mock open for reading app.json and writing log files
@pytest.fixture
def mock_file_operations(temp_app_json_content):
    m_open = mock_open()
    # Configure mock_open for app.json and log files
    # The first call to open will be for app.json (read mode)
    # Subsequent calls will be for log files (write mode)
    m_open.return_value.__enter__.return_value.read.side_effect = [
        json.dumps(temp_app_json_content).encode('utf-8') # For app.json read
    ]
    # For write operations, mock_open's default behavior is usually fine,
    # but we can explicitly set it if needed.
    # We need to ensure that the mock for read_data is only for the first call (app.json)
    # and subsequent calls to open (for log files) behave like normal file writes.
    # We will rely on the global patch of 'builtins.open' for log file writes.
    with patch('builtins.open', m_open):
        yield m_open

# Test Env class initialization and property precedence
def test_env_initialization_with_config(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, temp_app_json_content):
    # Unpack the mock_path_exists_and_isdir fixture
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir

    # The user_app_folder should NOT exist initially for makedirs to be called
    user_app_folder = os.path.normpath(os.path.join('/mock/home/user', '.testapp'))
    _directory_paths.discard(user_app_folder) # Ensure it's not in mocked directories
    _existing_paths.discard(user_app_folder) # Ensure it's not in mocked existing paths

    # Simulate loading config from fbpyutils/app.json
    with patch('fbpyutils.env.load_config', return_value=temp_app_json_content):
        # Re-initialize Env to pick up the mocked config
        Env._instance = None # Reset singleton instance
        env = Env(temp_app_json_content)

        assert env.APP['name'] == "TestApp"
        assert env.APP['appcode'] == "TEST"
        assert env.APP['year'] == 2024
        assert env.LOG_LEVEL == "DEBUG"
        assert os.path.normpath(env.LOG_FILE) == os.path.normpath("test_logs/test_app.log")
        assert os.path.normpath(env.USER_FOLDER) == os.path.normpath("/mock/home/user")
        assert os.path.normpath(env.USER_APP_FOLDER) == os.path.normpath(os.path.join("/mock/home/user", ".testapp"))
        mock_makedirs.assert_called_with(env.USER_APP_FOLDER)

def test_env_precedence_environment_variable_over_config(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, temp_app_json_content):
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir
    user_app_folder = os.path.normpath(os.path.join('/mock/home/user', '.testapp'))
    _directory_paths.add(user_app_folder)
    _existing_paths.add(user_app_folder)

    with patch.dict(os.environ, {'LOG_LEVEL': 'WARNING', 'LOG_TEXT_SIZE': '512'}):
        with patch('fbpyutils.env.load_config', return_value=temp_app_json_content):
            Env._instance = None
            env = Env(temp_app_json_content)

            assert env.LOG_LEVEL == "WARNING"
            assert env.LOG_TEXT_SIZE == 512

def test_env_precedence_default_if_not_in_config_or_env(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir):
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir
    user_app_folder = os.path.normpath(os.path.join('/mock/home/user', '.fbpyutils')) # Default appname
    _directory_paths.add(user_app_folder)
    _existing_paths.add(user_app_folder)

    # Simulate empty config and no env vars
    with patch.dict(os.environ, {}, clear=True):
        with patch('fbpyutils.env.load_config', return_value={}):
            Env._instance = None
            env = Env({})

            assert env.APP['appcode'] == "FBPYUTILS" # Default
            assert env.LOG_LEVEL == "INFO" # Default
            assert env.LOG_TEXT_SIZE == 256 # Default
            # LOG_FILE should use USER_APP_FOLDER default if not in config
            assert os.path.normpath(env.LOG_FILE) == os.path.normpath(os.path.join(env.USER_APP_FOLDER, 'fbpyutils.log'))

# Test Logger configuration
def test_logger_configure_with_config(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, temp_app_json_content, caplog):
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir
    
    # Add the log file directory to mocked existing directories
    log_file_dir = os.path.normpath(os.path.dirname(temp_app_json_content["logging"]["log_file_path"]))
    _directory_paths.add(log_file_dir)
    _existing_paths.add(log_file_dir)

    caplog.set_level(logging.DEBUG)
    Logger.configure(config_dict=temp_app_json_content["logging"])

    assert Logger._is_configured is True
    assert Logger._logger.level == logging.DEBUG
    assert len(Logger._logger.handlers) == 2 # Console and File handler

    # Check console handler format
    console_handler = next(h for h in Logger._logger.handlers if isinstance(h, logging.StreamHandler))
    assert console_handler.formatter._fmt == "TEST_FORMAT - %(message)s"

    # Check file handler path and format
    file_handler = next(h for h in Logger._logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler))
    assert os.path.normpath(file_handler.baseFilename).endswith(os.path.normpath("test_logs/test_app.log"))
    assert file_handler.formatter._fmt == "TEST_FORMAT - %(message)s"

    Logger.log(Logger.INFO, "Test message")
    assert "Test message" in caplog.text

def test_logger_configure_with_defaults(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, caplog):
    # No specific paths to add for defaults, as it uses user_app_folder which is mocked by mock_expanduser
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir
    user_app_folder = os.path.normpath(os.path.join('/mock/home/user', '.fbpyutils'))
    _directory_paths.add(user_app_folder)
    _existing_paths.add(user_app_folder)

    caplog.set_level(logging.INFO)
    Logger.configure(config_dict={}) # Configure with empty dict to force defaults

    assert Logger._is_configured is True
    assert Logger._logger.level == logging.INFO
    assert len(Logger._logger.handlers) == 1 # Only console handler by default

    console_handler = next(h for h in Logger._logger.handlers if isinstance(h, logging.StreamHandler))
    assert console_handler.formatter._fmt == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    Logger.log(Logger.INFO, "Default test message")
    assert "Default test message" in caplog.text

def test_logger_log_before_explicit_configure(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, caplog):
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir
    user_app_folder = os.path.normpath(os.path.join('/mock/home/user', '.fbpyutils'))
    _directory_paths.add(user_app_folder)
    _existing_paths.add(user_app_folder)

    # Ensure logger is not configured initially
    Logger._is_configured = False
    Logger._logger.handlers.clear()

    caplog.set_level(logging.INFO)
    Logger.log(Logger.INFO, "Message before explicit configure")

    assert Logger._is_configured is True # Should be configured with defaults
    assert Logger._logger.level == logging.INFO
    assert "Message before explicit configure" in caplog.text

def test_logger_file_path_creation_failure(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, caplog):
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir
    
    # Simulate that the directory for the log file does not exist and cannot be created
    log_file_dir = os.path.normpath("/no/permission/logs")
    _existing_paths.discard(log_file_dir) # Ensure it's not considered existing
    _directory_paths.discard(log_file_dir) # Ensure it's not considered a directory
    mock_makedirs.side_effect = OSError("Permission denied")

    caplog.set_level(logging.ERROR)

    config = {
        "log_level": "INFO",
        "log_format": "%(message)s",
        "log_file_path": "/no/permission/logs/app.log"
    }
    Logger.configure(config_dict=config)

    assert "Error setting up file logger" in caplog.text
    # Should still have console handler
    assert any(isinstance(h, logging.StreamHandler) for h in Logger._logger.handlers)
    # Should not have file handler
    assert not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in Logger._logger.handlers)

def test_logger_no_duplicate_handlers_on_reconfigure(mock_file_operations, mock_makedirs, mock_path_exists_and_isdir, temp_app_json_content):
    mock_exists, mock_isdir, _existing_paths, _directory_paths = mock_path_exists_and_isdir

    # Add initial log directory to mocks
    initial_log_dir = os.path.normpath(os.path.dirname(temp_app_json_content["logging"]["log_file_path"]))
    _directory_paths.add(initial_log_dir)
    _existing_paths.add(initial_log_dir)

    # First configuration
    Logger.configure(config_dict=temp_app_json_content["logging"])
    initial_handlers_count = len(Logger._logger.handlers)
    assert initial_handlers_count == 2 # Console and File handler

    # Add new log directory to mocks for reconfigure test
    new_log_dir = os.path.normpath(os.path.dirname("new_logs/new_app.log"))
    _directory_paths.add(new_log_dir)
    _existing_paths.add(new_log_dir)

    # Reconfigure with different settings (should clear old handlers)
    new_config = {
        "log_level": "WARNING",
        "log_format": "NEW_FORMAT - %(message)s",
        "log_file_path": "new_logs/new_app.log"
    }
    Logger._is_configured = False # Reset flag to allow re-configuration
    Logger.configure(config_dict=new_config)
    
    # The number of handlers should be the same as initial, not doubled
    assert len(Logger._logger.handlers) == initial_handlers_count
    assert Logger._logger.level == logging.WARNING
    
    # Verify new format is applied
    console_handler = next(h for h in Logger._logger.handlers if isinstance(h, logging.StreamHandler))
    assert console_handler.formatter._fmt == "NEW_FORMAT - %(message)s"

    file_handler = next(h for h in Logger._logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler))
    assert os.path.normpath(file_handler.baseFilename).endswith(os.path.normpath("new_logs/new_app.log"))
