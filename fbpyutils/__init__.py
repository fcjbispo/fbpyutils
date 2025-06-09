'''
    Francisco Bispo's Utilities for Python
'''
import os
import logging
import json
from typing import Dict, Any

from . import calendar
from . import datetime
from . import debug
from . import ofx
from . import file
from . import process
from . import string
from . import xlsx
from .env import Env, load_config # Import Env and load_config from the new env module
from .logging import Logger # Import the Logger from the new module


# Function to initialize the global environment and logging system
def initialize_fbpyutils():
    """
    Initializes the global environment configuration and the logging system
    for the fbpyutils library. This function should be called once when the
    library is loaded or when the application starts.
    """
    _config = load_config()
    Env(_config)
    Logger.configure(config_dict=_config.get("logging", {}))

# Call the initialization function when the package is imported
initialize_fbpyutils()
