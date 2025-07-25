import os
import json
import logging
import warnings
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

# Pydantic models for configuration validation
class AppConfig(BaseModel):
    name: str = "fbpyutils"
    version: str = "1.6.6"
    environment: str = "dev"
    appcode: str = "FBPYUTILS"
    year: int = 2025

class LoggingConfig(BaseModel):
    log_level: str = Field("INFO", alias="log_level")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: Optional[str] = None
    log_text_size: int = 256

class RootConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class Env:
    """
    Configuration class for the application environment.
    This class is a singleton and is immutable after initialization.
    """
    _instance: Optional['Env'] = None

    APP: AppConfig
    USER_FOLDER: str
    USER_APP_FOLDER: str
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILE: str
    LOG_TEXT_SIZE: int

    def __new__(cls, config: Optional[Dict[str, Any]] = None):
        if cls._instance is None:
            instance = super().__new__(cls)
            cls._instance = instance
            instance._initialize(config)
        return cls._instance

    def _initialize(self, config: Optional[Dict[str, Any]] = None):
        """Initializes the Env instance attributes."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        if config is None:
            # If no config is provided, load from the default app.json
            current_dir = os.path.dirname(__file__)
            default_config_path = os.path.join(current_dir, 'app.json')
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config_data = {}
        else:
            config_data = config

        # Validate and parse the configuration using Pydantic models
        parsed_config = RootConfig.model_validate(config_data)

        self.APP = parsed_config.app
        self.USER_FOLDER = os.path.expanduser('~')
        self.USER_APP_FOLDER = os.path.join(self.USER_FOLDER, f".{self.APP.name.lower()}")

        # Configure logging properties with precedence: environment variable -> config file -> default
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', parsed_config.logging.log_level)
        self.LOG_FORMAT = parsed_config.logging.log_format
        self.LOG_TEXT_SIZE = int(os.getenv('LOG_TEXT_SIZE', parsed_config.logging.log_text_size))
        
        log_file_from_config = parsed_config.logging.log_file_path
        if log_file_from_config:
            self.LOG_FILE = log_file_from_config
        else:
            default_log_path = os.getenv('LOG_PATH', self.USER_APP_FOLDER)
            self.LOG_FILE = os.path.join(default_log_path, 'fbpyutils.log')

        # Ensure USER_APP_FOLDER exists
        if not os.path.exists(self.USER_APP_FOLDER):
            os.makedirs(self.USER_APP_FOLDER)
        
        self._initialized = True

    @classmethod
    def load_config_from(cls, app_conf_file: str) -> 'Env':
        """
        Loads configuration from a specified JSON file and returns a configured Env instance.
        This will replace the existing singleton instance.
        """
        try:
            with open(app_conf_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            cls._instance = None  # Reset singleton to allow re-initialization
            return cls(config=config)
        except FileNotFoundError:
            logging.error(f"Configuration file '{app_conf_file}' not found. Cannot create Env instance.")
            raise
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from '{app_conf_file}'.")
            raise

def load_config(file_name: str = 'app.json') -> Dict[str, Any]:
    """
    DEPRECATED: This function is obsolete and will be removed in a future version.
    Use Env.load_config_from(path) or pass a config dict to the Env constructor instead.
    """
    warnings.warn(
        "load_config is deprecated. Use fbpyutils.setup() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Configuration file '{file_path}' not found. Using default settings.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from '{file_path}'. Using default settings.")
        return {}
