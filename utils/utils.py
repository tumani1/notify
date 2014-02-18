# coding: utf-8

from ..models import *
from ..connectors import db_connect

# Create table in the database
def create_database():
    Base.metadata.create_all(db_connect())


if __name__ == '__main__':
    create_database()
