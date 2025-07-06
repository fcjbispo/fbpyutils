import logging
import os
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler

# Forward declaration of Env to avoid circular import
class Env:
    pass

class Logger:
    """
    A singleton logging class that provides a static interface to the logging module.
    It must be configured via an Env instance using the get_from_env class method.
    """
    _instance: Optional['Logger'] = None

    DEBUG: int = logging.DEBUG
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING
    ERROR: int = logging.ERROR

    _logger: logging.Logger = logging.getLogger('fbpyutils')
    _is_configured: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _configure_internal(config_dict: Dict[str, Any]) -> None:
        """
        Internal method to configure the logging system.
        This can be called multiple times to reconfigure the logger.
        """
        log_level_str = config_dict.get("log_level", "INFO").upper()
        log_format = config_dict.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_file_path = config_dict.get("log_file_path")

        numeric_level = getattr(logging, log_level_str, logging.INFO)
        Logger._logger.setLevel(numeric_level)

        # Clear existing handlers to prevent duplicate logs on re-configuration
        if Logger._logger.handlers:
            for handler in Logger._logger.handlers[:]:
                handler.close()
                Logger._logger.removeHandler(handler)

        formatter = logging.Formatter(log_format)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        Logger._logger.addHandler(console_handler)

        # File Handler
        if log_file_path:
            try:
                log_dir = os.path.dirname(log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=256 * 1024, # 256 KB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                Logger._logger.addHandler(file_handler)
            except Exception as e:
                print(f"Error setting up file logger at {log_file_path}: {e}")
        
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
        }
        Logger._configure_internal(config_dict)
        Logger._logger.info("Logging system re-configured from Env.")

    @staticmethod
    def configure(config_dict: Dict[str, Any]) -> None:
        """
        Public method to re-configure the logger at runtime if needed.
        """
        Logger._configure_internal(config_dict)
        Logger._logger.info("Logging system re-configured.")

    @staticmethod
    def _check_configured():
        if not Logger._is_configured:
            raise RuntimeError(
                "Logger not configured. "
                "Please call fbpyutils.setup() before using the logger."
            )

    @staticmethod
    def debug(message: str, *args: Any, **kwargs: Any) -> None:
        Logger._check_configured()
        Logger._logger.debug(message, *args, **kwargs)

    @staticmethod
    def info(message: str, *args: Any, **kwargs: Any) -> None:
        Logger._check_configured()
        Logger._logger.info(message, *args, **kwargs)

    @staticmethod
    def warning(message: str, *args: Any, **kwargs: Any) -> None:
        Logger._check_configured()
        Logger._logger.warning(message, *args, **kwargs)

    @staticmethod
    def error(message: str, *args: Any, **kwargs: Any) -> None:
        Logger._check_configured()
        Logger._logger.error(message, *args, **kwargs)

    @staticmethod
    def log(log_type: int, log_text: str, *args: Any, **kwargs: Any) -> None:
        Logger._check_configured()
        Logger._logger.log(log_type, log_text, *args, **kwargs)
