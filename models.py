# coding: utf-8

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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


#############################################################################
# Models for States
class StatesModel(Base):
    __tablename__ = 'states'

    id      = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    host    = Column(String(50), nullable=True)
    status  = Column(Integer, nullable=True)
    users   = Column(PickleType)

    def __repr__(self):
        return u'%s[%s] - %s' % (self.id, self.user_id, self.status)


def _create_database():
    from connectors import db_connect

    Base.metadata.create_all(db_connect())


if __name__ == '__main__':
    _create_database()
