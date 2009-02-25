# Module:   rmessage
# Date:     24th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""RMessage

This plugin listens for xmlrpc.message events and
sends a Message Event into the system and returning
any replies generated.
"""

__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import listener
from pymills.datatypes import Stack
from circuits.lib.irc import Message

from kdb.plugin import BasePlugin

class RMessage(BasePlugin):

    """RMessage plugin

    This doesn't have any user commands available.
    This plugin listens for xmlrpc.message events and
    sends a Message Event into the system and returning
    any replies generated.

    Depends on: xmlrpc
    """

    def __init__(self, env, bot, *args, **kwargs):
        super(RMessage, self).__init__(env, bot, *args, **kwargs)

        self._rlog = Stack(5)

    def cmdRLOG(self, source):
        """View Remote Log

        Syntax: RLOG
        """

        return ["Last 5 remote messages:"] + list(self._rlog)

    @listener("xmlrpc.message")
    def onXMLRPCMESSAGE(self, user="anonymous", message=""):

        self._rlog.push(message)

        e = Message(str(user), self.bot.getNick(), message)
        r = self.iter(e, "message", self.channel)
        reply = "\n".join([x for x in r if x is not None])

        return reply.strip()
