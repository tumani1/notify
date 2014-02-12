# coding: utf-8

import json

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


#############################################################################
# Implement interface
class IPortocolAvatar(Interface):
    def logout():
        """
        Prototype for custom logout function
        """


class ServerAvatar(object):
    implements(IPortocolAvatar)

    def __init__(self, name):
        self.name = name

    def logout(self):
        pass


#############################################################################
# Credentials checker
class DBCredentialsChecker(object):
    implements(ICredentialsChecker)

    def __init__(self, runQuery):
        self.runQuery = runQuery
        self.sql = "SELECT username, password FROM user WHERE username = %s"
        self.credentialInterfaces = (IUsernamePassword, IUsernameHashedPassword,)

    def requestAvatarId(self, credentials):
        for interface in self.credentialInterfaces:
            if interface.providedBy(credentials):
                break
        else:
            raise error.UnhandledCredentials()

        # Query
        dbDeferred = self.runQuery(self.sql, (credentials.username,))

        # Defered result
        d = defer.Deferred()
        dbDeferred.addCallbacks(self._cbAuthenticate, self._ebAuthenticate,
                                callbackArgs=(credentials, d), errbackArgs=(credentials, d))

        return d

    def _cbAuthenticate(self, result, credentials, deferred):
        if not len(result):
            deferred.errback(error.UnauthorizedLogin("Username not found."))
        else:
            username, password = result[0]
            if IUsernameHashedPassword.providedBy(credentials):
                if credentials.checkPassword(password):
                    deferred.callback(credentials.username)
                else:
                    deferred.errback(error.UnauthorizedLogin("Password mismatch."))

            elif IUsernamePassword.providedBy(credentials):
                if password == credentials.password:
                    deferred.callback(credentials.username)
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
            avatar = ServerAvatar(avatarId)
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
            name = self.avatar.name
            if name in self.users:
                self.users[name]["state"] = APP_DISCONECTED
                self.send_broadcast_message(name)

        self.avatar = None
        self.logout = None

    def lineReceived(self, line):
        if not self.avatar:
            username, password = line.strip().split("@", 1)
            self.try_auth_user(username, password)
        else:
            self.get_states(line)

    def try_auth_user(self, username, password):
        self.portal.login(UsernamePassword(username, password), None, IPortocolAvatar)\
                    .addCallbacks(self._cbAuth, self._ebAuth)

    def _cbAuth(self, (interface, avatar, logout)):
        self.avatar = avatar
        self.logout = logout

        self.users[avatar.name] = {
            "self" : self,
            "host" : self.transport.getPeer().host,
            "state": APP_USER_LOGINED,
            "users": [],
        }

        self.sendLine(json.dumps({"success": "Login sucessful, please proceed."}))

    def _ebAuth(self, failure):
        self.sendLine(json.dumps({"error": failure.value.message}))
        self.transport.loseConnection()

    def get_states(self, data):
        try:
            list_users = json.loads(data)

            if not isinstance(list_users, list):
                self.sendLine(json.dumps({"error": "We received not list."}))
                return

            # Get uniq users
            list_users = list(set(list_users))

            name = self.avatar.name
            if self.users[name]["state"] == APP_USER_LOGINED:
                self.users[name]["users"] = list_users
                self.users[name]["state"] = APP_CONNECTED
                self.send_broadcast_message(name)

            result = [[item, self.users[name]["host"], self.users[name]["state"]] for item in list_users if item in self.users]
            self.sendLine(json.dumps(result))

        except Exception as e:
            self.sendLine(json.dumps({"error": e.__str__()}))

    def send_broadcast_message(self, name):
        if name in self.users:
            msg = [name, self.users[name]["host"], self.users[name]["state"]]
            for item in self.users[name]['users']:
                if item in self.users and self.users[item]['self'] != self:
                    self.users[item]['self'].sendLine(json.dumps(msg))


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

    # Set connection to the DB
    pool = adbapi.ConnectionPool(**DB_CONFIG['mysql'])

    # Class for authentificate
    checker = DBCredentialsChecker(pool.runQuery)

    # Set Portal and Realm
    realm = ServerRealm()
    server_portal = Portal(realm)
    server_portal.registerChecker(checker)

    # Start reactor
    reactor.listenTCP(8000, ServerFactory(server_portal))
    reactor.run()


if __name__ == '__main__':
    main()
