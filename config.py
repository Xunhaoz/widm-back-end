import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_KEY = os.getenv("OPENAI_KEY")

    PORT = 5025
    HOST = '0.0.0.0'

    SWAGGER = {
        "title": "widm-back-end",
        "description": "Nation Central University WIDM LAB back-end API",
        "version": "1.0.0",
    }

    BASIC_AUTH = os.getenv("BASIC_AUTH")
    DASH_BOARD_URL = os.getenv("DASH_BOARD_URL")
    HOME_PAGE_URL = os.getenv("HOME_PAGE_URL")

    WHITE_LIST = [
        "110502528", "110502528", "112522087", "F443693", "112522049", "112522102", "112522051", "112522092",
        "113522140", "113522139", "113922002", "113522079", "113522152"
    ]
