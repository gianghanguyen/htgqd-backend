import os

from dotenv import load_dotenv
from textwrap import dedent

load_dotenv()


class Config:
    RUN_SETTING = {
        'host': os.environ.get('SERVER_HOST', 'localhost'),
        'port': int(os.environ.get('SERVER_PORT', 8080)),
        'debug': os.getenv('DEBUG', False),
        "access_log": False,
        "auto_reload": True,
        'workers': int(os.getenv('SERVER_WORKERS', 4))
    }
    # uWSGI를 통해 배포되어야 하므로, production level에선 run setting을 건드리지 않음
    FALLBACK_ERROR_FORMAT = 'json'

    OAS_UI_DEFAULT = 'swagger'
    SWAGGER_UI_CONFIGURATION = {
        'apisSorter': "alpha",
        'docExpansion': "list",
        'operationsSorter': "alpha"
    }

    SECRET_KEY = os.getenv('SECRET_KEY', 'example project')
    EXPIRATION_JWT = 2592000  # 1 month

    # SERVER_NAME = os.getenv('SERVER_NAME')
    #
    # # To reorder swagger tags
    # raw = {}
    # if SERVER_NAME:
    #     raw['servers'] = [{'url': SERVER_NAME}]
    #
    # REDIS = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    API_HOST = os.getenv('API_HOST', '127.0.0.1:8080')
    # API_BASEPATH = os.getenv('API_BASEPATH', '')
    API_SCHEMES = os.getenv('API_SCHEMES', 'http')
    API_VERSION = os.getenv('API_VERSION', '0.1.0')
    API_TITLE = os.getenv('API_TITLE', 'HTGQD API')
    API_CONTACT_EMAIL = os.getenv('API_CONTACT_EMAIL', 'example@gmail.com')

    API_DESCRIPTION = os.getenv('API_DESCRIPTION', dedent(
        """
        ## Explore the API
        """
    ))

class LocalDBConfig:
    pass


class RemoteDBConfig:
    pass


class MongoDBConfig:
    USERNAME = os.environ.get("MONGO_USERNAME") or "just_for_dev"
    PASSWORD = os.environ.get("MONGO_PASSWORD") or "password_for_dev"
    HOST = os.environ.get("MONGO_HOST") or "localhost"
    PORT = os.environ.get("MONGO_PORT") or "27017"
    DATABASE = os.environ.get("MONGO_DATABASE") or "job_db"
