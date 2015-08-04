from hashlib import md5, sha1

from circuits import handler, Component, Event
from circuits.web.tools import check_auth, basic_auth

from funcy import imap, rpartial


from ..plugin import BasePlugin


HASHERS = {
    "md5": md5,
    "sha": sha1,
}


def load_config(config):
    if "basicauth" not in config:
        raise ConfigError("Basic Auth not configured!")

    for param in ("passwd",):
        if param not in config["basicauth"]:
            raise ConfigError("Basic Auth not configured! Missing: {0}".format(repr(param)))

    config = config["basicauth"]

    realm = config.get("realm", "kdb")
    hasher = config.get("hasher", "sha")

    if hasher not in HASHERS:
        raise ConfigError("Unsupported hasher: {0}".format(repr(hasher)))

    with open(config["passwd"], "r") as f:
        users = dict(imap(rpartial(str.split, ":"), imap(str.strip, f)))

    return users, realm, hasher


class ConfigError(Exception):
    """Config Error"""


class loggedin(Event):
    """loggedin Event"""


class loggedout(Event):
    """loggedout Event"""


class whois(Event):
    """whois Event"""


class Session(object):

    def __init__(self, user, username):
        self.user = user
        self.username = username


class BasicAuthFilter(Component):

    channel = "web"

    def init(self, users, realm, encrypt=md5):
        self.users = users
        self.realm = realm
        self.encrypt = encrypt

    @handler("request", priority=1.0)
    def on_request(self, event, req, res):
        if not check_auth(req, res, self.realm, self.users):
            event.stop()
            return basic_auth(req, res, self.realm, self.users)


class Commands(Component):

    channel = "commands"

    def init(self, users, encrypt=md5):
        self.users = users
        self.encrypt = encrypt

    def login(self, source, target, args):
        """Login

        Syntax: LOGIN <username> <password>
        """

        args = iter(args.split())

        username = next(args, None)
        password = next(args, None)

        if not (username and password):
            return "No Username and/or Password specified."

        if self.encrypt(password).hexdigest() != self.users.get(username, None):
            return "Invalid Username or Password."

        self.fire(loggedin(source, username))

        return "Okay"

    def logout(self, source, target, args):
        """Logout

        Syntax: LOGOUT
        """

        self.fire(loggedout(source))

        return "Okay"

    def whoami(self, source, targets, args):
        """Who am I logged in as?

        Syntax: WHOAMI
        """

        result = yield self.call(whois(source))
        session = result.value

        if session is None:
            yield "No sessions(s) found."
            return

        yield "You are {0} logged in as {1}".format(source[0], session.username)

    def adduser(self, source, target, args):
        """Add a new user account

        Syntax: ADDUSER <username> <password>
        """

        args = iter(args.split())

        username = next(args, None)
        password = next(args, None)

        if not (username and password):
            return "No Username and/or Password specified."

        if username in self.users:
            return "User already exists!"

        self.users[username] = self.encrypt(password)

        return "Okay"

    def deluser(self, source, target, args):
        """Delete a new user account

        Syntax: DELUSER <username>
        """

        args = iter(args.split())

        username = next(args, None)

        if not username:
            return "No Username specified."

        if username not in self.users:
            return "User does not  exist!"

        del self.users[username]

        return "Okay"


class StateManager(Component):

    def init(self, data):
        self.data = data

    def loggedin(self, user, username):
        self.data["sessions"][user] = Session(user, username)

    def loggedout(self, user):
        del self.data["sessions"][user]

    def whois(self, user):
        return self.data["sessions"].get(user, None)


class BasicAuth(BasePlugin):
    """Basic Auth Plugin

    A simple Basic Auth Plugin that provides
    user registration and authentication for
    access to both Web and IRC interfaces.

    Credentials are stored in an Apache-style
    password file specified by the following
    configuration:

    [basicauth]
    passwd = /path/to/passwd
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(BasicAuth, self).init(*args, **kwargs)

        self.data.init(
            {
                "basicauth": {
                    "sessions": {},
                }
            }
        )

        data = self.data["basicauth"]

        users, realm, hasher = load_config(self.config)

        BasicAuthFilter(users, realm).register(self)
        StateManager(data).register(self)
        Commands(users).register(self)
