from time import time


from circuits import handler, Event, Timer
from circuits.protocols.irc import request, Message


from ..plugin import BasePlugin


class keepalive(Event):
    """keepalive Event"""


class KeepAlive(BasePlugin):
    """KeepAlive Plugin

    A KeepAlive Plugin to help keep the bot connected
    and detect when the connection might have gone
    dead by periodically sending null byte packets.

    There are no commands for this plugin.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(KeepAlive, self).init(*args, **kwargs)

        # Keep-Alive Timer
        Timer(60, keepalive(), persist=True).register(self)

    @handler("keepalive")
    def keepalive(self):
        timestamp = int(time() * 10000)
        self.fire(request(Message("PING", "LAB{0}".format(timestamp))))
