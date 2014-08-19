# Plugin:   drone
# Date:     22th December 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Drone Mode

This plugin enables drone-mode. For now this means
just setting the bot's nickname to the system hostname.
"""


__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from socket import gethostname


from circuits import handler
from circuits.protocols.irc import NICK


from ..plugin import BasePlugin


class Drone(BasePlugin):
    "Drone Mode"

    def init(self, *args, **kwargs):
        super(Drone, self).init(*args, **kwargs)

        if self.data.state["nick"] != gethostname():
            self.fire(NICK(gethostname()))

    @handler("connected", "registered", "nick")
    def update_nick(self, *args, **kwargs):
        if self.data.state["nick"] != gethostname():
            self.fire(NICK(gethostname()))
