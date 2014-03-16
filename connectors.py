# coding: utf-8

from sqlalchemy import create_engine, pool
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

import settings
from exceptions import *
from utils.decorators import toThread

# Create connection to the database
def db_connect(type='mysql', **kwargs):
    db_settings = settings.DB_CONFIG
    if not type in db_settings:
        raise NoExistTypeDatabase

    if not 'drivername' in db_settings[type]:
        raise NoExistDriverName

    return create_engine(URL(**db_settings[type]), **kwargs)


#############################################################################################################
# Class singleton decorator for call in the database
class DBDefer(object):
    _instance = None

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(DBDefer, self).__new__(self, *args, **kwargs)

        return self._instance

    def __init__(self, engine=None, poolclass=None):
        poolclass = poolclass or pool.SingletonThreadPool

        if engine is None:
            self.engine = db_connect(poolclass=poolclass)
        else:
            self.engine = create_engine(engine, poolclass=poolclass)


    def __call__(self, func):
        @toThread
        def wrapper(*args, **kwargs):
            session = sessionmaker(bind=self.engine)()
            try:
                return func(session=session, *args, **kwargs)
            except:
                session.rollback()
                raise
            finally:
                session.close()

        return wrapper
