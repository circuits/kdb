# Module:   rmessage
# Date:     24th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""RMessage

This plugin listens for remote message events and
sends a Message Event into the system and returning
any replies generated.
"""

__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import handler
from pymills.datatypes import Stack
from circuits.net.protocols.irc import PRIVMSG

from kdb.plugin import BasePlugin

class RMessage(BasePlugin):

    """RMessage plugin

    This doesn't have any user commands available.
    This plugin listens for remote message events and
    sends a Message Event into the system and returning
    any replies generated.

    Depends on: remote
    """

    def __init__(self, env):
        super(RMessage, self).__init__(env)

        self._rlog = Stack(5)

    def cmdRLOG(self, source, target):
        """View Remote Log

        Syntax: RLOG
        """

        return ["Last 5 remote messages:"] + list(self._rlog)

    @handler("message", channel="remote")
    def remote_message(self, source="anonymous", target=None, message=""):
        self._rlog.push(message)

        ourself = self.env.bot.auth["nick"]

        if not (target is None or target == ourself):
            message = "<%s> %s" % (source, message)
            self.fire(PRIVMSG(target, message))
            return "Message to %s" % target
        else:
            if target is None:
                target = ourself

            r = self.fire(PRIVMSG(source, target, message)
            reply = r or ""
            return reply.strip()
