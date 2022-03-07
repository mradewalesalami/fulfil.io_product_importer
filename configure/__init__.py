"""
This module provides all configuration for the application.
"""

import os

from dotenv import load_dotenv

from helpers import get_project_root

ROOT_DIR = get_project_root()

"""
For local development, we will use the .env file
We check if the .env is present and then use it.
In production where the .env will not be present,
it uses the environment variable from the cloud platform.
"""
dotenv_path = os.path.join(ROOT_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    """
    Base Config where other Config inherit from.
    This class provides common functionality for all Config classes.
    """
    SECRET_KEY = "mrfrIMEngCl0pAKqIIBS_g"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://fulfil:password@localhost/fulfil_db'
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_ECHO = False


class TestConfig(Config):
    ENV = "test"
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_ECHO = False


config_modes = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}

ALLOWED_CONFIGURATION_MODES = ['development', 'production']


def detect_configuration_mode():
    """
    Detect the config mode by looking for an environment variable 'config_mode'
    and checks if the config mode is allowed.
    :return: the configuration mode
    """
    from errors import ConfigNotFound
    config_mode = os.environ['CONFIG_MODE']
    if config_mode in ALLOWED_CONFIGURATION_MODES:
        print('("{}") configuration mode detected'.format(config_mode))
        return config_mode
    error_message = 'Invalid or no configuration mode ("{}") detected'.format(config_mode)
    raise ConfigNotFound(error_message)


def load_configuration(app, mode):
    """
    Load the application configuration
    :param app: the application
    :param mode: the mode signalling which configuration object to load
    :return: None
    """
    configuration = config_modes[mode]
    
    # Load pre-defined config by class/object
    app.config.from_object(configuration)
    
    # Load the instance config
    app.config.from_pyfile('config.py', silent=True)
