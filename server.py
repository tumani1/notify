# coding: utf-8

import json

from pika.adapters.twisted_connection import TwistedProtocolConnection
from pika.connection import ConnectionParameters
from pika import BasicProperties

from twisted.python import log as twisted_log

from twisted.cred import error
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernameHashedPassword, IUsernamePassword, UsernamePassword

from twisted.internet import protocol, reactor, defer
from twisted.protocols.basic import LineReceiver

from zope.interface import implements, Interface

from settings import *
from queries import *




#############################################################################
# Implement interface
class IPortocolAvatar(Interface):
    def logout():
        """
        Prototype for custom logout function
        """


class ServerAvatar(object):
    implements(IPortocolAvatar)

    def __init__(self, pk, username, password):
        self.pk = pk
        self.username = username
        self.password = password

    def logout(self):
        pass


#############################################################################
# Credentials checker
class DBCredentialsChecker(object):
    implements(ICredentialsChecker)

    def __init__(self):
        self.credentialInterfaces = (IUsernamePassword, IUsernameHashedPassword,)

    @defer.inlineCallbacks
    def requestAvatarId(self, credentials):
        for interface in self.credentialInterfaces:
            if interface.providedBy(credentials):
                break
        else:
            raise error.UnhandledCredentials()

        try:
            result = yield getUser(credentials.username)
        except:
            msg = "Database Error"
            raise error.UnhandledCredentials(msg)

        result = list(result)
        if not len(result):
            raise error.UnauthorizedLogin("Username not found.")
        else:
            password = result[0].password
            if IUsernameHashedPassword.providedBy(credentials):
                if credentials.checkPassword(password):
                    defer.returnValue(result[0])
                else:
                    raise error.UnauthorizedLogin("Password mismatch.")

            elif IUsernamePassword.providedBy(credentials):
                if password == credentials.password:
                    defer.returnValue(result[0])
                else:
                    raise error.UnauthorizedLogin("Password mismatch.")

            else:
                raise error.UnhandledCredentials()


#############################################################################
# Realm
class ServerRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IPortocolAvatar in interfaces:
            avatar = ServerAvatar(avatarId.id, avatarId.username, avatarId.password)
            logout = avatar.logout

            return IPortocolAvatar, avatar, logout

        raise NotImplementedError("no interface")


#############################################################################
# Protocol
class ServerProtocol(LineReceiver):
    avatar = None
    logout = None

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.sendLine("User@Passwd:")

    @defer.inlineCallbacks
    def connectionLost(self, reason):
        if not self.avatar is None:
            name = self.avatar.username
            if name in self.factory.users:
                args = (self.avatar.pk, self.transport.getPeer().host, APP_DISCONECTED, None)
                try:
                    result = yield update_or_create_status(*args)

                   # result = result.first()
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

            # Send message
            self.message(**{"success": "Logged successfully."})
        except Exception as err:
            return_value = False
            self.manualCloseConnection(err)

        defer.returnValue(return_value)

    @defer.inlineCallbacks
    def getStates(self, data):
        return_value = False
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
            if instance.status == APP_USER_LOGINED:
                instance.status = APP_CONNECTED
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
        self.message(**{"error": failure.message})
        self.transport.loseConnection()


#############################################################################
# Factory
class ServerFactory(protocol.Factory):
    def __init__(self, portal):
        self.users = {}
        self.portal = portal

    def buildProtocol(self, addr):
        proto = ServerProtocol(self)
        return proto


def main():
    # Logging
    file = open(os.path.join(LOG_PATH, 'server.log'), 'w')
    twisted_log.startLogging(file)

    # Class for authentificate
    checker = DBCredentialsChecker()

    # Set Portal and Realm
    realm = ServerRealm()
    server_portal = Portal(realm)
    server_portal.registerChecker(checker)

    # Start reactor
    reactor.listenTCP(8000, ServerFactory(server_portal))
    reactor.run()


if __name__ == '__main__':
    main()
