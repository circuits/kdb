from hashlib import md5, sha1

from circuits import handler, Component
from circuits.web.tools import check_auth, basic_auth

from funcy import imap, rpartial


from ..plugin import BasePlugin


HASHERS = {
    "md5": md5,
    "sha": sha1,
}


class ConfigError(Exception):
    """Config Error"""


class BasicAuthFilter(Component):

    channel = "web"

    def init(self, config):
        self.config = config

        if "basicauth" not in self.config:
            raise ConfigError("Basic Auth not configured!")

        for param in ("passwd", "realm",):
            if param not in self.config["basicauth"]:
                raise ConfigError("Basic Auth not configured! Missing: {0}".format(repr(param)))

        config = self.config["basicauth"]

        self.realm = config["realm"]
        self.hasher = config.get("hasher", "md5")

        if self.hasher not in HASHERS:
            raise ConfigError("Unsupported hasher: {0}".format(repr(self.hasher)))

        self.encrypt = HASHERS[self.hasher]

        with open(config["passwd"], "r") as f:
            self.users = dict(imap(rpartial(str.split, ":"), imap(str.strip, f)))

    @handler("request", priority=1.0)
    def on_request(self, event, req, res):
        if not check_auth(req, res, self.realm, self.users):
            event.stop()
            return basic_auth(req, res, self.realm, self.users)


class BasicAuth(BasePlugin):
    """Basic Auth Plugin

    A simple Basic Auth Plugin that protects
    the web interface from unauthorized access.

    Credentials are stored in an Apache-style
    password file specified by the following
    configuration:

    [basicauth]
    passwd = /path/to/passwd

    Note: There are no commands for this plugin.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(BasicAuth, self).init(*args, **kwargs)

        BasicAuthFilter(self.config).register(self)
