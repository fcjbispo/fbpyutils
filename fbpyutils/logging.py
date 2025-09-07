import logging
import os
from typing import Dict, Any, Optional
from concurrent_log_handler import ConcurrentRotatingFileHandler

# Forward declaration of Env to avoid circular import
class Env:
    pass

class Logger:
    """
    A singleton logging class that provides a static interface to the logging module.

    This class ensures that only one instance of the logger is created. It must be
    configured by calling `fbpyutils.setup()` before use, which internally calls
    `Logger.get_from_env(env)`.

    Configuration options are sourced from an `Env` object and can be reconfigured
    at runtime.

    Attributes:
        DEBUG (int): Constant for the DEBUG log level.
        INFO (int): Constant for the INFO log level.
        WARNING (int): Constant for the WARNING log level.
        ERROR (int): Constant for the ERROR log level.
    """
    _instance: Optional['Logger'] = None

    # Log levels available as class attributes for convenience.
    DEBUG: int = logging.DEBUG
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING
    ERROR: int = logging.ERROR
    CRITICAL: int = logging.CRITICAL

    _logger: logging.Logger = logging.getLogger('fbpyutils')
    _is_configured: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _configure_internal(config_dict: Dict[str, Any]) -> None:
        """
        Internal method to configure the logging system based on a dictionary.

        This method sets up the logger's level, format, and handlers (console and file).
        It clears existing handlers to prevent duplication on reconfiguration.

        Args:
            config_dict (Dict[str, Any]): A dictionary with configuration keys:
                - 'app_name' (str): The name of the logger.
                - 'log_level' (str): The minimum log level (e.g., 'INFO').
                - 'log_format' (str): The log message format.
                - 'log_file_path' (str): Optional path to the log file.
        """
        app_name = config_dict.get("app_name")
        if app_name and isinstance(app_name, str):
            Logger._logger = logging.getLogger(app_name.lower())

        log_level_str = config_dict.get("log_level", "INFO").upper()
        log_format = config_dict.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Only use file logging if explicitly configured
        if config_dict:
            log_file_path = config_dict.get("log_file_path", os.path.sep.join(["~", ".fbpyutils", "logs", "app.log"]))
            log_file_path = os.path.expanduser(log_file_path)
            log_handlers = config_dict.get("log_handlers", ["file", "console"])
        else:
            # When config_dict is empty, use only file handler
            log_file_path = None
            log_handlers = ["file"]

        numeric_level = getattr(logging, log_level_str, logging.INFO)
        Logger._logger.setLevel(numeric_level)

        # Clear existing handlers to prevent duplicate logs on re-configuration
        if Logger._logger.handlers:
            for handler in Logger._logger.handlers[:]:
                handler.close()
                Logger._logger.removeHandler(handler)

        formatter = logging.Formatter(log_format)

        # File Handler
        if "file" in log_handlers:
            if log_file_path:
                try:
                    log_dir = os.path.dirname(log_file_path)
                    if log_dir and not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                    
                    file_handler = ConcurrentRotatingFileHandler(
                        log_file_path,
                        maxBytes=256 * 1024,  # 256 KB
                        backupCount=5,
                        encoding='utf-8'
                    )
                    file_handler.setFormatter(formatter)
                    Logger._logger.addHandler(file_handler)
                except Exception as e:
                    print(f"Error setting up file logger at {log_file_path}: {e}")

        # Console Handler
        if "console" in log_handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            Logger._logger.addHandler(console_handler)

        # check if at least one handler is added
        if not Logger._logger.hasHandlers():
            raise ValueError("No valid log handlers configured. Please check 'log_handlers' in the configuration. Valid options are 'console' and 'file'.")
        
        Logger._is_configured = True

    @classmethod
    def get_from_env(cls, env: 'Env') -> 'Logger':
        """
        Gets the singleton Logger instance, configured from an Env object.
        This is the primary method for obtaining a configured logger.
        """
        config = {
            "log_level": env.LOG_LEVEL,
            "log_format": env.LOG_FORMAT,
            "log_file_path": env.LOG_FILE,
            "app_name": getattr(env.APP, 'appcode', None)
        }
        cls._configure_internal(config)
        return cls()

    @staticmethod
    def configure_from_env(env: 'Env') -> None:
        """
        Public method to re-configure the logger at runtime from an Env object, if needed.
        """
        config_dict = {
            "log_level": env.LOG_LEVEL,
            "log_format": env.LOG_FORMAT,
            "log_file_path": env.LOG_FILE,
            "app_name": getattr(env.APP, 'appcode', None)
        }
        Logger._configure_internal(config_dict)
        Logger._logger.info("Logging system re-configured from Env.")

    @staticmethod
    def configure_from_config_dict(config_dict: Dict[str, Any]) -> None:
        """
        Public method to re-configure the logger at runtime if needed.
        """
        Logger._configure_internal(config_dict)
        Logger._logger.info("Logging system re-configured.")

    @staticmethod
    def configure(app_name: str, log_level: str, log_format: str = None, log_file_path = None) -> None:
        Logger.configure_from_config_dict({
            "log_level": log_level,
            "log_format": log_format,
            "log_file_path": log_file_path,
            "app_name": app_name
        })

    @staticmethod
    def _check_configured():
        """
        Checks if the logger has been configured, raising an error if not.
        """
        if not Logger._is_configured:
            raise RuntimeError(
                "Logger not configured. "
                "Please call fbpyutils.setup() before using the logger."
            )

    @staticmethod
    def debug(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a message with severity 'DEBUG'."""
        Logger._check_configured()
        Logger._logger.debug(message, *args, **kwargs)

    @staticmethod
    def info(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a message with severity 'INFO'."""
        Logger._check_configured()
        Logger._logger.info(message, *args, **kwargs)

    @staticmethod
    def warning(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a message with severity 'WARNING'."""
        Logger._check_configured()
        Logger._logger.warning(message, *args, **kwargs)

    @staticmethod
    def error(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a message with severity 'ERROR'."""
        Logger._check_configured()
        Logger._logger.error(message, *args, **kwargs)

    @staticmethod
    def critical(message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a message with severity 'CRITICAL'."""
        Logger._check_configured()
        Logger._logger.critical(message, *args, **kwargs)

    @staticmethod
    def log(log_type: int, log_text: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with a custom log level.

        Args:
            log_type (int): The integer value of the log level.
            log_text (str): The message to log.
        """
        Logger._check_configured()
        Logger._logger.log(log_type, log_text, *args, **kwargs)
