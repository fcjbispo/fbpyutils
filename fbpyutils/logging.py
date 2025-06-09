'''
    Logging system for fbpyutils
'''
import logging
import os
from typing import Dict, Any
from logging.handlers import RotatingFileHandler

class Logger:
    """
    A logging class that provides a static interface to the logging module,
    configurable via a dictionary.

    This class encapsulates the logging functionality, allowing for easy switching
    between different logging levels and output destinations (console, file).
    It provides a simple and consistent API for logging messages.

    Attributes:
        DEBUG (int): The logging level for debugging messages.
        INFO (int): The logging level for informational messages.
        WARNING (int): The logging level for warning messages.
        ERROR (int): The logging level for error messages.
    """

    DEBUG: int = logging.DEBUG
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING
    ERROR: int = logging.ERROR

    _logger: logging.Logger = logging.getLogger('fbpyutils')
    _is_configured: bool = False

    @staticmethod
    def configure(config_dict: Dict[str, Any] = None) -> None:
        """
        Configures the global logging system based on the provided dictionary.
        If no dictionary is provided, default values are used.

        Args:
            config_dict (Dict[str, Any], optional): A dictionary containing logging configurations.
                                                    Expected keys: 'log_level', 'log_format', 'log_file_path'.
                                                    Defaults to None.
        """
        if Logger._is_configured:
            return

        config_dict = config_dict or {}

        log_level_str = config_dict.get("log_level", "INFO").upper()
        log_format = config_dict.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_file_path = config_dict.get("log_file_path")

        numeric_level = getattr(logging, log_level_str, logging.INFO)
        Logger._logger.setLevel(numeric_level)

        # Clear existing handlers to prevent duplicate logs
        if Logger._logger.handlers:
            for handler in Logger._logger.handlers:
                Logger._logger.removeHandler(handler)
            Logger._logger.handlers.clear()

        formatter = logging.Formatter(log_format)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        Logger._logger.addHandler(console_handler)

        # File Handler with rotation
        if log_file_path:
            try:
                log_dir = os.path.dirname(log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                # Use RotatingFileHandler as per original logging.py
                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=256 * 1024, # 256 KB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setLevel(numeric_level)
                file_handler.setFormatter(formatter)
                Logger._logger.addHandler(file_handler)
            except Exception as e:
                Logger._logger.error(f"Error setting up file logger at {log_file_path}: {e}")
        
        Logger._is_configured = True
        Logger._logger.info("Logging system configured.")

    @staticmethod
    def debug(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a debug message."""
        if not Logger._is_configured:
            Logger.configure()
        Logger._logger.debug(message, *args, **kwargs)

    @staticmethod
    def info(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs an info message."""
        if not Logger._is_configured:
            Logger.configure()
        Logger._logger.info(message, *args, **kwargs)

    @staticmethod
    def warning(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a warning message."""
        if not Logger._is_configured:
            Logger.configure()
        Logger._logger.warning(message, *args, **kwargs)

    @staticmethod
    def error(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs an error message."""
        if not Logger._is_configured:
            Logger.configure()
        Logger._logger.error(message, *args, **kwargs)

    @staticmethod
    def log(log_type: int, log_text: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with the specified type and text.
        This method is kept for API compatibility.
        """
        if not Logger._is_configured:
            Logger.configure()

        if log_type == Logger.DEBUG:
            Logger.debug(log_text, *args, **kwargs)
        elif log_type == Logger.INFO:
            Logger.info(log_text, *args, **kwargs)
        elif log_type == Logger.WARNING:
            Logger.warning(log_text, *args, **kwargs)
        elif log_type == Logger.ERROR:
            Logger.error(log_text, *args, **kwargs)

# Initial configuration of the logger (can be re-configured later)
Logger.configure()
