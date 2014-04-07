# coding: utf-8

from twisted.internet.defer import inlineCallbacks, returnValue


RABBIT_MQ_HOST = "127.0.0.1"
RABBIT_MQ_PORT = 5672

VHOST = "/"
EXCHANGE_NAME = "test_twisted"
QUEUE_NAME = "log_queue"
ROUTING_KEY = "log_routing_key"
CONSUMER_TAG = "log_consumer_tag"


credentials = {"LOGIN": "guest", "PASSWORD": "guest"}


@inlineCallbacks
def getConnection(client):
    conn = yield client.connectTCP(RABBIT_MQ_HOST, RABBIT_MQ_PORT)
    yield conn.start(credentials)

    returnValue(conn)


@inlineCallbacks
def getChannel(conn):
    chan = yield conn.channel(3)
    yield chan.channel_open()

    returnValue(chan)
