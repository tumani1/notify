# coding: utf-8

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#############################################################################
# Models for Users
class UsersModel(Base):
    __tablename__ = 'user'

    id   = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return u'[%s] %s' % (self.id, self.username)
