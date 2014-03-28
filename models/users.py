# coding: utf-8

from sqlalchemy import Column, Integer, String

from db import Base



#############################################################################
# Models for Users
class UsersModel(Base):
    __tablename__ = 'users'

    id       = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return u'[%s] %s' % (self.id, self.username)
