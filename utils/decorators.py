# coding: utf-8

from twisted.internet import threads


# Wrapper for twisted deferToThread
def toThread(f):
    def wrapper(*args, **kwargs):
        return threads.deferToThread(f, *args, **kwargs)

    return wrapper
