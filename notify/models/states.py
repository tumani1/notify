# coding: utf-8

from sqlalchemy import Column, Integer, String, PickleType, ForeignKey
from db import Base


__all__ = ['StatesModel']


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
