import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any

# Import Logger here to avoid circular dependency with __init__.py
# Logger is configured by __init__.py after Env is initialized.
from fbpyutils.logging import Logger

@dataclass(frozen=True)
class Env:
    """
    Configuration class for the application environment variables.
    This class is designed to be a singleton and immutable.
    """
    _instance = None

    app_config: Dict[str, Any] = field(default_factory=dict)

    APP: Dict[str, Any] = field(init=False)
    USER_FOLDER: str = field(init=False)
    USER_APP_FOLDER: str = field(init=False)
    LOG_LEVEL: str = field(init=False)
    LOG_TEXT_SIZE: int = field(init=False)
    LOG_FILE: str = field(init=False)

    def __post_init__(self):
        # Set APP values from app_config, with defaults
        object.__setattr__(self, 'APP', {
            "appcode": self.app_config.get("app", {}).get("appcode", "FBPYUTILS"),
            "name": self.app_config.get("app", {}).get("name", "fbpyutils"),
            "version": self.app_config.get("app", {}).get("version", "1.6.3"),
            "year": self.app_config.get("app", {}).get("year", "2025")
        })

        # Construct USER_FOLDER and USER_APP_FOLDER
        object.__setattr__(self, 'USER_FOLDER', os.path.expanduser('~'))
        object.__setattr__(self, 'USER_APP_FOLDER', os.path.sep.join([self.USER_FOLDER, f".{self.APP['name'].lower()}"]))

        # Configure other properties with precedence: environment variable, dictionary value, default value
        object.__setattr__(self, 'LOG_LEVEL', os.getenv('LOG_LEVEL', self.app_config.get("logging", {}).get("log_level", 'INFO')))
        object.__setattr__(self, 'LOG_TEXT_SIZE', int(os.getenv('LOG_TEXT_SIZE', self.app_config.get("logging", {}).get("log_text_size", 256))))
        
        log_file_path_from_config = self.app_config.get("logging", {}).get("log_file_path")
        if log_file_path_from_config:
            # If log_file_path is provided in app.json, use it directly
            object.__setattr__(self, 'LOG_FILE', log_file_path_from_config)
        else:
            # Otherwise, use the existing logic with USER_APP_FOLDER
            object.__setattr__(self, 'LOG_FILE', os.path.sep.join([
                os.getenv('LOG_PATH', self.USER_APP_FOLDER), 'fbpyutils.log']))

        # Ensure USER_APP_FOLDER exists
        if not os.path.exists(self.USER_APP_FOLDER):
            os.makedirs(self.USER_APP_FOLDER)
            # Log this action using the Logger class
            Logger.info(f"Created user application folder: {self.USER_APP_FOLDER}")

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Env, cls).__new__(cls)
        return cls._instance

# Load configuration from app.json
def load_config(file_name: str = 'app.json') -> Dict[str, Any]:
    """Loads configuration from a JSON file."""
    # Construct the path relative to the current file (fbpyutils/env.py)
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, file_name)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Configuration file '{file_path}' not found. Using default settings.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from '{file_path}'. Using default settings.")
        return {}
