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

from circuits import listener

from kdb.plugin import BasePlugin

class Drone(BasePlugin):
    "Drone Mode"

    def __init__(self, *args, **kwargs):
        super(Drone, self).__init__(*args, **kwargs)

        if self.bot.irc.getNick() != gethostname():
            self.bot.irc.ircNICK(gethostname())

    @listener("connected")
    def onCONNECTED(self):
        if self.bot.irc.getNick() != gethostname():
            self.bot.irc.ircNICK(gethostname())

    @listener("nicksollision")
    def onNICKCOLLISION(self):
        if self.bot.irc.getNick() != gethostname():
            self.bot.irc.ircNICK(gethostname())
