# coding: utf-8

import settings

from models import *
from connectors import *

dbdefer = DBDefer()

@dbdefer
def update_or_create_status(user_id, host, status=settings.APP_USER_LOGINED, users=[], session=None):
    instance = session.query(StatesModel).filter_by(user_id=user_id).first()
    if not instance is None:
        instance.host   = host
        instance.status = status

        if not users is None:
            instance.users = users

        session.commit()
        session.flush()
    else:
        instance = StatesModel(user_id=user_id, host=host, status=status)
        session.add(instance)
        session.commit()

        instance = session.query(StatesModel).filter_by(id=instance.id).first()
        session.flush()

    return instance


@dbdefer
def getUser(username, session=None, **kwargs):
    return session.query(UsersModel).filter_by(username=username, **kwargs)

@dbdefer
def getStatus(session=None, **kwargs):
    return session.query(StatesModel).filter_by(**kwargs)

