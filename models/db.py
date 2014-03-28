# coding: utf-8

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# class MyBase(object):
#     _instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super(MyBase, cls).__new__(cls, *args, **kwargs)
#
#         return cls._instance
#
#     def __init__(self):
#         self.base = declarative_base()
#
# Base = MyBase().base

__all__ = ['Base']
