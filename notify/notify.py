# coding: utf-8

import json

from twisted.internet import protocol, defer
from twisted.protocols.basic import LineReceiver
from twisted.cred.credentials import UsernamePassword

from queries import *
from credentials import IPortocolAvatar


#############################################################################
# Protocol
class NotifyProtocol(LineReceiver):
    avatar = None
    logout = None

    def __init__(self, factory):
        self.factory = factory
        self.amqp = {
            'log': ('test-twisted', 'log-queue', 'log_routing_key'),
        }

    def connectionMade(self):
        self.sendLine("User@Passwd:")

    @defer.inlineCallbacks
    def connectionLost(self, reason):
        if not self.avatar is None:
            name = self.avatar.username
            if name in self.factory.users:
                args = (self.avatar.pk, self.transport.getPeer().host, settings.APP_DISCONECTED, None)
                try:
                    result = yield update_or_create_status(*args)

                    if not result is None:
                        self.sendBroadcastMessage(self.avatar.username, result)

                except Exception as err:
                    self.message(**{"error": err.__str__()})
                    defer.returnValue(False)

        self.avatar = None
        self.logout = None
        defer.returnValue(True)

    def lineReceived(self, line):
        if not self.avatar:
            self.tryAuthUser(line)
        else:
            self.getStates(line)

    @defer.inlineCallbacks
    def tryAuthUser(self, line):
        # Default success return value
        return_value = True

        try:
            # Try logined on the portal
            username, password = line.strip().split("@", 1)
            interface, avatar, logout = yield self.factory.portal.\
                login(UsernamePassword(username, password), None, IPortocolAvatar)

            # Update DB information
            result = yield update_or_create_status(avatar.pk, self.transport.getPeer().host)

            # Update Info
            self.avatar = avatar
            self.logout = logout
            self.factory.users[avatar.username] = self

            # send message
            self.factory.amqp.send_message(*self.amqp['log'], msg='User ID:%s loggined' % self.avatar.pk)

            # Send message
            self.message(**{"success": "User logged successfully. Insert users list:"})
        except Exception as err:
            return_value = False
            self.manualCloseConnection(err)

        defer.returnValue(return_value)

    @defer.inlineCallbacks
    def getStates(self, data):
        return_value = False

        # send message
        self.factory.amqp.send_message(*self.amqp['log'], msg='Get states User ID:%s' % self.avatar.pk)

        try:
            list_users = json.loads(data)

            if not isinstance(list_users, list):
                self.message(**{"error": "We received not list."})
                defer.returnValue(False)

            # Get uniq users
            list_users = list(set(list_users))

            # Get status about users and send notification, if success
            result = yield getStatus(**{'user_id': self.avatar.pk})
            result = yield self.sendStatusNotification(result, list_users)

            return_value = True

        except Exception as e:
            self.message(**{"error": e.__str__()})

        finally:
            defer.returnValue(return_value)

    @defer.inlineCallbacks
    def sendStatusNotification(self, result, list_users):
        instance = result.first()
        if not instance is None:
            if instance.status == settings.APP_USER_LOGINED:
                instance.status = settings.APP_CONNECTED
                instance.users = list_users
                self.sendBroadcastMessage(self.avatar.username, instance)

                yield update_or_create_status(self.avatar.pk, self.transport.getPeer().host,
                                        instance.status, instance.users)

            msg = [[item, instance.host, instance.status] for item in list_users if item in self.factory.users]
            #TODO: переделать на ф-цию message
            self.sendLine(json.dumps(msg))

        defer.returnValue(True)

    def sendBroadcastMessage(self, name, obj=None):
        if name in self.factory.users and not obj is None:
            msg = json.dumps([name, obj.host, obj.status])
            for item in obj.users:
                if item in self.factory.users and self.factory.users[item] != self:
                    self.factory.users[item].sendLine(msg)

    def message(self, result=None, **kwargs):
        self.sendLine(json.dumps(kwargs))

    def manualCloseConnection(self, failure, **kwargs):
        # send message
        msg = 'Error: %s' % failure.message
        self.factory.amqp.send_message(*self.amqp['log'], msg=msg)

        self.message(**{"error": failure.message})
        self.transport.loseConnection()


#############################################################################
# Factory
class NotifyFactory(protocol.ServerFactory):
    protocol = NotifyProtocol
    __slots__ = ['users']

    def __init__(self, service):
        self.users = {}
        self.service = service

    def buildProtocol(self, addr):
        proto = self.protocol(self)
        return proto
