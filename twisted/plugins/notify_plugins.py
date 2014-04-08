# coding: utf-8

import os
import logging

from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.cred.portal import Portal
from twisted.application import internet, service

from notify import settings as settings
from notify.amqp import AmqpFactory
from notify.notify import NotifyFactory
from notify.credentials import DBCredentialsChecker, ServerRealm


#############################################################################
class BaseOptions(usage.Options):
    """
    Base options.
    """

    optFlags = [
        ['help', 'h', "Display usage information"],
    ]


#############################################################################
class NotifyOptions(BaseOptions):
    """
    Options global to everything.
    """

    optParameters = [
        ['port', 'p', 8000, 'The port number to listen on.'],
        ['iface', None, 'localhost', 'The interface to listen on.'],
    ]


#############################################################################
class NotifyServiceMaker(object):
    implements(service.IServiceMaker, IPlugin)

    tapname = 'notify'
    description = 'Notification server'
    options = NotifyOptions

    def makeService(self, options):
        """
        Создается объект TCPServer с помощью фабрики из модуля проекта.
        """

        # Logging
        file = open(os.path.join(settings.LOG_PATH, 'server.log'), 'w')
        observer = log.FileLogObserver(file)
        log.addObserver(observer.emit)

        # Setup Top Service
        top_service = service.MultiService()

        # Setup service
        notify_service = service.Service()
        notify_service.setServiceParent(top_service)

        #Class for authenticate
        checker = DBCredentialsChecker()

        # Set Portal and Realm
        realm = ServerRealm()
        server_portal = Portal(realm)
        server_portal.registerChecker(checker)

        # Init AMQP Factory
        amqp_factory = AmqpFactory(**settings.AMQP_CONFIG['rabbitmq'])

        # Init Notify Factory
        notify_factory = NotifyFactory(notify_service)
        notify_factory.portal = server_portal
        notify_factory.amqp = amqp_factory

        tcp_service = internet.TCPServer(int(options['port']), notify_factory, interface=options['iface'])
        tcp_service.setServiceParent(top_service)

        # this hooks the collection we made to the application
        application = service.Application('notify')
        top_service.setServiceParent(application)

        return top_service


service_maker = NotifyServiceMaker()
