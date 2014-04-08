# coding: utf-8

from notify.models import Base
from notify.connectors import db_connect


# Create table in the database
def create_all_tables(**kwargs):
    Base.metadata.create_all(bind=db_connect(), **kwargs)


# Drop table in the database
def drop_all_tables(**kwargs):
    Base.metadata.drop_all(bind=db_connect(), **kwargs)
