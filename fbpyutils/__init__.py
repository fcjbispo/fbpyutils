'''
    Francisco Bispo's Utilities for Python
'''
import os
import logging


# mock class to fake logging system
class Logger:
    """
    A logging class that provides a static interface to the logging module.

    This class encapsulates the logging functionality, allowing for easy switching
    between different logging levels. It also provides a simple and consistent API
    for logging messages.

    Attributes:
        DEBUG (int): The logging level for debugging messages.
        INFO (int): The logging level for informational messages.
        WARNING (int): The logging level for warning messages.
        ERROR (int): The logging level for error messages.

    Methods:
        log(log_type, log_text): Logs a message with the specified type and text.
    """

    # Maintain existing constants for backward compatibility
    DEBUG: int = logging.DEBUG
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING
    ERROR: int = logging.ERROR

    _logger = logging.getLogger('fbpyutils')
    _logger.setLevel(logging.DEBUG)
    
    # Configure console handler if not already configured
    if not _logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)

    @staticmethod
    def log(log_type: int, log_text: str) -> None:
        """
        Logs a message with the specified type and text.
        """
        if log_type == Logger.DEBUG:
            Logger._logger.debug(log_text)
        elif log_type == Logger.INFO:
            Logger._logger.info(log_text)
        elif log_type == Logger.WARNING:
            Logger._logger.warning(log_text)
        elif log_type == Logger.ERROR:
            Logger._logger.error(log_text)


class Env:
    """
    Configuration class for the application environment variables.
    """

    APP: dict = {
        "appcode": "FBPYUTILS",
        "appname": "fbpyutils",
        "version": "1.6.1",
        "year": "2025"
    }

    USER_FOLDER: str = os.path.expanduser('~')
    USER_APP_FOLDER: str = os.path.sep.join([USER_FOLDER, f".{APP['appname'].lower()}"])

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_TEXT_SIZE: int = int(os.getenv('LOG_TEXT_SIZE', 256))
    LOG_FILE: str = os.path.sep.join([
        os.getenv('LOG_PATH', USER_APP_FOLDER), 'mymoney.log'])


if not os.path.exists(Env.USER_APP_FOLDER):
    os.makedirs(Env.USER_APP_FOLDER)
