import os
import json
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

# Pydantic models for configuration validation
class AppConfig(BaseModel):
    name: str = "fbpyutils"
    version: str = "1.6.10"
    environment: str = "dev"
    appcode: str = "FBPYUTILS"
    year: int = 2025

class LoggingConfig(BaseModel):
    log_level: str = Field("INFO", alias="log_level")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: Optional[str] = None
    log_text_size: int = 256
    log_handlers: Optional[list] = Field(default_factory=lambda: ["file"])
class RootConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    config: Dict[str, Any] = Field(default_factory=dict)


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
    LOG_HANDLERS: Optional[list] = None
    CONFIG: Dict[str, Any]

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
        self.LOG_LEVEL = os.getenv('FBPY_LOG_LEVEL', parsed_config.logging.log_level)
        self.LOG_FORMAT = parsed_config.logging.log_format
        self.LOG_TEXT_SIZE = int(os.getenv('FBPY_LOG_TEXT_SIZE', parsed_config.logging.log_text_size))
        
        log_file_from_config = parsed_config.logging.log_file_path
        if log_file_from_config:
            self.LOG_FILE = log_file_from_config
        else:
            default_log_path = os.getenv('FBPY_LOG_PATH', self.USER_APP_FOLDER)
            self.LOG_FILE = os.path.join(default_log_path, 'fbpyutils.log')

        self.LOG_HANDLERS = parsed_config.logging.log_handlers

        # Set the configuration dictionary
        self.CONFIG = parsed_config.config

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
            raise FileNotFoundError(f"Configuration file '{app_conf_file}' not found. Cannot create Env instance.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Error decoding JSON from '{app_conf_file}'.")            
