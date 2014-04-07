# coding: utf-8

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import ClientCreator
from twisted.internet import reactor

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
import txamqp.spec

import common


@inlineCallbacks
def getQueue(conn, chan):
    yield chan.exchange_declare(exchange=common.EXCHANGE_NAME, type="direct", durable=True, auto_delete=False)
    yield chan.queue_declare(queue=common.QUEUE_NAME, durable=True, exclusive=False, auto_delete=False)
    yield chan.queue_bind(queue=common.QUEUE_NAME, exchange=common.EXCHANGE_NAME, routing_key=common.ROUTING_KEY)

    yield chan.basic_consume(queue=common.QUEUE_NAME, consumer_tag=common.CONSUMER_TAG)
    queue = yield conn.queue(common.CONSUMER_TAG)

    returnValue(queue)


@inlineCallbacks
def processMessage(chan, queue):
    msg = yield queue.get()
    print "Received: %s from channel #%s" % (msg.content.body, chan.id)

    processMessage(chan, queue)
    returnValue(None)


@inlineCallbacks
def main():
    delegate = TwistedDelegate()

    spec = txamqp.spec.load("spec/amqp0-9-1.stripped.xml")
    consumer = ClientCreator(reactor, AMQClient, delegate=delegate, vhost=common.VHOST, spec=spec)

    conn = yield common.getConnection(consumer)
    chan = yield common.getChannel(conn)
    queue = yield getQueue(conn, chan)
    while True:
        yield processMessage(chan, queue)


if __name__ == "__main__":
    main()
    reactor.run()
