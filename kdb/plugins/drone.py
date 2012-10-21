# Module:   drone
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
from circuits.net.protocols.irc import NICK

from kdb.plugin import BasePlugin

class Drone(BasePlugin):
    "Drone Mode"

    def __init__(self, *args, **kwargs):
        super(Drone, self).__init__(*args, **kwargs)

        if self.env.bot.auth["nick"] != gethostname():
            self.fire(NICK(gethostname()))

    @handler("connected")
    def onCONNECTED(self):
        if self.env.bot.auth["nick"] != gethostname():
            self.fire(NICK(gethostname()))

    @handler("nicksollision")
    def onNICKCOLLISION(self):
        if self.env.bot.auth["nick"] != gethostname():
            self.fire(NICK(gethostname()))
