import logging


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///DevelopmentConfig.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PORT = 5003
    HOST = '0.0.0.0'

    LOGGING_FILENAME = './logs/development.log'
    LOGGING_LEVEL = logging.DEBUG
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    SWAGGER = {
        "title": "widm-back-end",
        "description": "Nation Central University WIDM LAB back-end API",
        "version": "1.0.0",
    }

    DEBUG = False
    RESET_DB = True


class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///TestConfig.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PORT = 5003
    HOST = '0.0.0.0'

    LOGGING_FILENAME = './logs/test.log'
    LOGGING_LEVEL = logging.DEBUG
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    SWAGGER = {
        "title": "widm-back-end",
        "description": "Nation Central University WIDM LAB back-end API",
        "version": "1.0.0",
    }

    DEBUG = False
    RESET_DB = False


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PORT = 5003
    HOST = '0.0.0.0'

    LOGGING_FILENAME = './logs/production.log'
    LOGGING_LEVEL = logging.DEBUG
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    SWAGGER = {
        "title": "widm-back-end",
        "description": "Nation Central University WIDM LAB back-end API",
        "version": "1.0.0",
    }

    DEBUG = False
    RESET_DB = False
