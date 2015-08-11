from circuits.net.events import connect
from circuits import Event, Component, Timer


from ..plugin import BasePlugin


class reconnect(Event):
    """reconnect Event"""


class Reconnector(Component):

    def init(self, host, port, interval=5, increment=5):
        self.host = host
        self.port = port

        self.interval = interval
        self.increment = increment

        self.tries = 0
        self.connected = False

        self.timer = Timer(self.retryin, reconnect()).register(self)

    def connected(self, *args):
        self.tries = 0
        self.connected = True
        if self.timer:
            self.timer.unregister()
            self.timer = None

    def disconnected(self):
        self.connected = False
        if not self.timer:
            self.timer = Timer(self.retryin, reconnect()).register(self)

    def error(self, *args, **kwargs):
        self.connected = False
        if not self.timer:
            self.timer = Timer(self.retryin, reconnect()).register(self)

    def reconnect(self):
        self.tries += 1
        self.fire(connect(self.host, self.port))

    @property
    def retryin(self):
        return self.interval + (self.tries * self.increment)


class Reconnect(BasePlugin):
    """Reconnect Plugin

    A plugin to automatically reconnect if the bot has
    lost it's connection for whatever reason.

    This plugin has no commands.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Reconnect, self).init(*args, **kwargs)

        Reconnector(self.bot.host, self.bot.port).register(self)
