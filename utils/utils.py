# coding: utf-8

from models import Base
from connectors import db_connect


# Create table in the database
def create_all_tables(**kwargs):
    Base.metadata.create_all(bind=db_connect(), **kwargs)


# Drop table in the database
def drop_all_tables(**kwargs):
    Base.metadata.drop_all(bind=db_connect(), **kwargs)
