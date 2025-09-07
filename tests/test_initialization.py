import unittest
import os
import json
import fbpyutils
from fbpyutils.env import Env
from fbpyutils.logging import Logger
from unittest.mock import patch, mock_open

class TestInitialization(unittest.TestCase):

    def setUp(self):
        """Reset singletons before each test."""
        fbpyutils._env_instance = None
        fbpyutils._logger_instance = None
        Env._instance = None
        Logger._instance = None
        Logger._is_configured = False

        os.environ.pop('FBPY_LOG_LEVEL', None)
        os.environ.pop('FBPY_LOG_PATH', None)
        os.environ.pop('FBPY_LOG_TEXT_SIZE', None)

    def test_setup_with_defaults(self):
        """Test setup() using the default app.json."""
        fbpyutils.setup()
        
        env = fbpyutils.get_env()
        logger = fbpyutils.get_logger()

        self.assertIsInstance(env, Env)
        self.assertIsInstance(logger, Logger)
        self.assertEqual(env.APP.name, "FBPyUtils")
        self.assertTrue(Logger._is_configured)

    def test_setup_with_dict(self):
        """Test setup() with a configuration dictionary."""
        test_config = {
            "app": {"name": "TestApp", "version": "1.0"},
            "logging": {"log_level": "DEBUG"}
        }
        
        fbpyutils.setup(config=test_config)
        
        env = fbpyutils.get_env()
        logger = fbpyutils.get_logger()

        self.assertEqual(env.APP.name, "TestApp")
        self.assertEqual(env.LOG_LEVEL, "DEBUG")
        self.assertIsInstance(logger, Logger)

    @patch("fbpyutils.env.open", new_callable=mock_open, read_data=json.dumps({
        "app": {"name": "FileApp", "version": "2.0"},
        "logging": {"log_level": "WARNING", "log_file_path": None}
    }))
    def test_setup_with_file_path(self, mock_file_open):
        """
        Test setup() with a configuration file path.
        We patch open in the env module to avoid interfering with the logger's file handler.
        We also set log_file_path to None to prevent the logger from trying to open a file.
        """
        test_file_path = "/fake/path/to/config.json"
        
        fbpyutils.setup(config=test_file_path)
        
        env = fbpyutils.get_env()
        logger = fbpyutils.get_logger()

        mock_file_open.assert_called_once_with(test_file_path, 'r', encoding='utf-8')
        self.assertEqual(env.APP.name, "FileApp")
        self.assertEqual(env.LOG_LEVEL, "WARNING")
        self.assertIsInstance(logger, Logger)

    def test_get_env_before_setup_raises_error(self):
        """Test that get_env() raises RuntimeError if called before setup."""
        with self.assertRaises(RuntimeError):
            fbpyutils.get_env()

    def test_get_logger_before_setup_raises_error(self):
        """Test that get_logger() raises RuntimeError if called before setup."""
        with self.assertRaises(RuntimeError):
            fbpyutils.get_logger()

if __name__ == '__main__':
    unittest.main()
