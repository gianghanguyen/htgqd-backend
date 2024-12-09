from pymongo import MongoClient

from app.constants.mongodb_constants import MongoCollections
from app.utils.logger_utils import get_logger
from config import MongoDBConfig

logger = get_logger('MongoDB')


class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            # connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'
            connection_url = f'mongodb://{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'

        self.connection_url = connection_url.split('@')[-1]
        self.client = MongoClient(connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]

        self._point_col = self.db[MongoCollections.point]
        self._job_col = self.db[MongoCollections.job]
        self._company_col = self.db[MongoCollections.company]

    
    def get_job(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._job_col.find_one(filter_, projection=projection)
            return cursor
        except Exception as ex:
            logger.exception(ex)
        return None
    
    def get_job_list(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._job_col.find(filter_, projection=projection)
            return list(cursor)
        except Exception as ex:
            logger.exception(ex)
        return None
    
    def get_company(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._company_col.find_one(filter_, projection=projection)
            return cursor
        except Exception as ex:
            logger.exception(ex)
        return None
    
    def get_company_list(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._company_col.find(filter_, projection=projection)
            return list(cursor)
        except Exception as ex:
            logger.exception(ex)
        return None
    
    def get_point_list(self, filter_=None, projection=None, page_size=None, page=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._point_col.find(filter_, projection=projection).sort("point", -1).limit(page_size).skip((page-1)*page_size)
            return list(cursor)
        except Exception as ex:
            logger.exception(ex)
        return []
    
    def delete_point(self, filter_):
        try:
            self._point_col.delete_many(filter_)
        except Exception as ex:
            logger.exception(ex)

    def insert_point(self, data):
        try:
            self._point_col.insert_many(data)
        except Exception as ex:
            logger.exception(ex)