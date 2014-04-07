# coding: utf-8

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import ClientCreator
from twisted.internet import reactor

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import txamqp.spec

import common


@inlineCallbacks
def pushText(chan, body):
    msg = Content(body)
    msg['delivery-mode'] = 2
    msg['content-type'] = 'application/json'
    yield chan.basic_publish(exchange=common.EXCHANGE_NAME, content=msg, routing_key=common.ROUTING_KEY)

    returnValue(None)


@inlineCallbacks
def cleanUp(conn, chan):
    yield chan.channel_close()
    chan = yield conn.channel(0)

    yield chan.connection_close()
    reactor.stop()

    returnValue(None)


@inlineCallbacks
def main():
    delegate = TwistedDelegate()

    # create the Twisted producer client
    spec = txamqp.spec.load("spec/amqp0-9-1.stripped.xml")
    producer = ClientCreator(reactor, AMQClient, delegate=delegate, vhost=common.VHOST, spec=spec)

    # connect to the RabbitMQ server
    conn = yield common.getConnection(producer)

    # get the channel
    chan = yield common.getChannel(conn)

    # create queue, exchange, binding
    yield chan.exchange_declare(exchange=common.EXCHANGE_NAME, type="direct", durable=True, auto_delete=False)
    yield chan.queue_declare(queue=common.QUEUE_NAME, durable=True, exclusive=False, auto_delete=False)
    yield chan.queue_bind(queue=common.QUEUE_NAME, exchange=common.EXCHANGE_NAME, routing_key=common.ROUTING_KEY)

    # send the text to the RabbitMQ server
    yield pushText(chan, "test")

    # shut everything down
    yield cleanUp(conn, chan)


if __name__ == "__main__":
    main()
    reactor.run()
