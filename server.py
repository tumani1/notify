# coding: utf-8

try:
    import json
except ImportError:
    import simplejson as json

from twisted.enterprise import adbapi
from twisted.python import log

from twisted.cred import error
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernameHashedPassword, IUsernamePassword, UsernamePassword

from twisted.internet import protocol, reactor, defer
from twisted.protocols.basic import LineReceiver

from zope.interface import implements, Interface

from settings import *
from models import *
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

    def requestAvatarId(self, credentials):
        for interface in self.credentialInterfaces:
            if interface.providedBy(credentials):
                break
        else:
            raise error.UnhandledCredentials()

        # Defered result
        d = defer.Deferred()
        getUser(credentials.username).addCallbacks(self._cbAuthenticate, self._ebAuthenticate,
                                callbackArgs=(credentials, d), errbackArgs=(credentials, d))

        return d

    def _cbAuthenticate(self, result, credentials, deferred):
        result = list(result)
        if not len(result):
            deferred.errback(error.UnauthorizedLogin("Username not found."))
        else:
            password = result[0].password
            if IUsernameHashedPassword.providedBy(credentials):
                if credentials.checkPassword(password):
                    deferred.callback(result[0])
                else:
                    deferred.errback(error.UnauthorizedLogin("Password mismatch."))

            elif IUsernamePassword.providedBy(credentials):
                if password == credentials.password:
                    deferred.callback(result[0])
                else:
                    deferred.errback(error.UnauthorizedLogin("Password mismatch."))

            else:
                deferred.errback(error.UnhandledCredentials())

    def _ebAuthenticate(self, message, credentials, deferred):
        deferred.errback(error.LoginFailed(message))


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
    portal = None
    avatar = None
    logout = None

    def __init__(self, users):
        self.users = users

    def connectionMade(self):
        self.sendLine("User@Passwd:")

    def connectionLost(self, reason):
        if not self.avatar is None:
            name = self.avatar.username
            if name in self.users:
                def _cbOK(result):
                    result = result.first()
                    if not result is None:
                        self.send_broadcast_message(result.username, obj=result)

                update_or_create_status(self.avatar.pk, self.transport.getPeer().host, APP_DISCONECTED, None).\
                    addCallback(_cbOK)

        self.avatar = None
        self.logout = None

    def lineReceived(self, line):
        if not self.avatar:
            username, password = line.strip().split("@", 1)
            self.try_auth_user(username, password)
        else:
            self.get_states(line)

    def try_auth_user(self, username, password):
        self.portal.\
            login(UsernamePassword(username, password), None, IPortocolAvatar).\
            addCallbacks(self._cbAuth, self._ebAuth)

    def _cbAuth(self, (interface, avatar, logout)):
        self.avatar = avatar
        self.logout = logout
        self.users[avatar.username] = self

        update_or_create_status(avatar.pk, self.transport.getPeer().host).\
            addCallbacks(self._cbSuccessNotify, self._ebAuth)

    def _ebAuth(self, failure):
        self.sendLine(json.dumps({"error": failure.value.message}))
        self.transport.loseConnection()

    # т.к. в sql есть Replace ф-ция. она делает Insert или Update
    def _cbSuccessNotify(self, result):
        self.sendLine(json.dumps({"success": "Login sucessful, please proceed."}))

    def get_states(self, data):
        try:
            list_users = json.loads(data)

            if not isinstance(list_users, list):
                self.sendLine(json.dumps({"error": "We received not list."}))
                return

            # Get uniq users
            list_users = list(set(list_users))

            getStatus(**{'user_id': self.avatar.pk}).addCallback(self._cbSendStatusNotify, list_users)

        except Exception as e:
            self.sendLine(json.dumps({"error": e.__str__()}))

    def _cbSendStatusNotify(self, result, list_users):
        instance = result.first()
        if not instance is None:
            if instance.status == APP_USER_LOGINED:
                instance.status = APP_CONNECTED
                instance.users = list_users
                self.send_broadcast_message(self.avatar.username, instance)

                update_or_create_status(self.avatar.pk, self.transport.getPeer().host,
                                        instance.status, instance.users)

            msg = [[item, instance.host, instance.status] for item in list_users if item in self.users]
            self.sendLine(json.dumps(msg))

    def send_broadcast_message(self, name, obj=None):
        if name in self.users and not obj is None:
            msg = json.dumps([name, obj.host, obj.status])
            for item in obj.users:
                if item in self.users and self.users[item] != self:
                    self.users[item].sendLine(msg)


#############################################################################
# Factory
class ServerFactory(protocol.Factory):
    def __init__(self, portal):
        self.users = {}
        self.portal = portal

    def buildProtocol(self, addr):
        proto = ServerProtocol(self.users)
        proto.portal = self.portal
        return proto


def main():
    # Logging
    file = open(os.path.join(LOG_PATH, 'server.log'), 'w')
    log.startLogging(file)

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
