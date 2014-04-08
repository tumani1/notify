# coding: utf-8

from zope.interface import implements, Interface

from twisted.cred import error
from twisted.cred.portal import IRealm
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernameHashedPassword, IUsernamePassword

from twisted.internet import defer

from queries import getUser


#############################################################################
# Implement interface
class IPortocolAvatar(Interface):
    def logout(self):
        """
        Prototype for custom logout function
        """


class ServerAvatar(object):
    implements(IPortocolAvatar)
    __slots__ = ['pk', 'username', 'password']

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
