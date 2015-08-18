from time import time
from collections import deque


from circuits.protocols.irc import request, Message
from circuits import handler, Component, Event, Timer

from funcy import rpartial, take


from ..plugin import BasePlugin


def avg(xs):
    return sum(xs) / len(xs) if xs else 0


def averages(xs):
    return tuple(map(avg, map(rpartial(take, xs), range(5, 20, 5))))


class keepalive(Event):
    """keepalive Event"""


class Commands(Component):

    channel = "commands"

    def lag(self, source, target, args):
        """Display lag (latency) averages

        Syntax: LAG
        """

        lag = self.parent.data["lag"]

        return "Lag: {0:d}ms {1:d}ms {2:d}ms ".format(
            *averages(lag)
        )


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

        self.interval = int(self.config.get("keepalive", {}).get("interval", 60))

        # We want at most 15mins worth of data points
        self.data.init(
            {
                "lag": deque([], (60 * 15) / self.interval)
            }
        )

        # Keep-Alive Timer
        Timer(self.interval, keepalive(), persist=True).register(self)

        Commands().register(self)

    @handler("keepalive")
    def keepalive(self):
        timestamp = int(time() * 1000)
        self.fire(request(Message("PING", "LAG{0}".format(timestamp))))

    @handler("pong")
    def pong(self, source, target, timestamp):
        latency = int(time() * 1000) - int(timestamp[3:])
        self.data["lag"].append(latency)
