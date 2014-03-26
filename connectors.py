# coding: utf-8

from sqlalchemy import create_engine, pool
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

import settings
from exceptions import *
from utils.decorators import toThread

# Create connection to the database
def db_connect(type=settings.DB_DRIVER, **kwargs):
    db_settings = settings.DB_CONFIG
    if not type in db_settings:
        raise NoExistTypeDatabase

    if not 'drivername' in db_settings[type]:
        raise NoExistDriverName

    return create_engine(URL(**db_settings[type]), **kwargs)


#############################################################################################################
# Class decorator for call in the database
class DBDefer(object):
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
