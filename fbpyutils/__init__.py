'''
    Francisco Bispo's Utilities for Python
'''
import os
import json
from typing import Dict, Any, Optional, Union

from . import calendar
from . import datetime
from . import debug
from . import ofx
from . import file
from . import process
from . import string
from . import xlsx
from .env import Env
from .logging import Logger

# Variáveis globais para armazenar as instâncias singleton
_env_instance: Optional[Env] = None
_logger_instance: Optional[Logger] = None

def setup(config: Optional[Union[Dict[str, Any], str]] = None) -> None:
    """
    Initializes the global environment and logging system for the fbpyutils library.

    This function should be called once when the application starts. It allows for
    configuration via a dictionary, a file path, or falls back to the default
    'app.json' if no configuration is provided.

    Args:
        config (Optional[Union[Dict[str, Any], str]]): 
            - A dictionary containing the configuration.
            - A string path to a JSON configuration file.
            - If None, loads from the default 'fbpyutils/app.json'.
    """
    global _env_instance, _logger_instance

    if isinstance(config, str):
        # Se config é uma string, é um caminho de arquivo
        _env_instance = Env.load_config_from(config)
    elif isinstance(config, dict):
        # Se é um dicionário, passa diretamente para o construtor
        _env_instance = Env(config=config)
    else:
        # Se for None ou outro tipo, usa o construtor padrão
        _env_instance = Env()

    # Configura o logger usando a instância do Env
    _logger_instance = Logger.get_from_env(_env_instance)
    _logger_instance.info("fbpyutils setup completed.")

def get_env() -> Env:
    """Returns the singleton Env instance."""
    if _env_instance is None:
        raise RuntimeError("fbpyutils is not initialized. Call fbpyutils.setup() first.")
    return _env_instance

def get_logger() -> Logger:
    """Returns the singleton Logger instance."""
    if _logger_instance is None:
        raise RuntimeError("fbpyutils is not initialized. Call fbpyutils.setup() first.")
    return _logger_instance


setup()
