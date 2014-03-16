# coding: utf-8

from zope.interface import implements
from twisted.python import usage
from twisted.application.service import IServiceMaker, MultiService
from twisted.plugin import IPlugin
from twisted.application import internet


class BaseOptions(usage.Options):
    """
    Base options.
    """

    optFlags = [
        ['help', 'h', "Display usage information"],
    ]

#############################################################################
#
class TestOptions(BaseOptions):
    """
    Options global to everything.
    """

    optParameters = [
        ['port', 'p', 8000, 'The port number to listen on.'],
        ['iface', None, 'localhost', 'The interface to listen on.'],
    ]


#############################################################################
#
class TestServiceMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = "test"
    description = "Test twisted server."
    options = TestOptions

    def makeService(self, options):
        """
        Создается объект TCPServer с помощью фабрики из модуля проекта.
        """

        top_service = MultiService()

        # poetry_service = PoetryService(options['poem'])
        # poetry_service.setServiceParent(top_service)
        #
        # factory = PoetryFactory(poetry_service)
        # tcp_service = internet.TCPServer(int(options['port']), factory, interface=options['iface'])
        # tcp_service.setServiceParent(top_service)

        return top_service
        # return internet.TCPServer(int(options["port"]), EchoFactory())

service_maker = TestServiceMaker()
