from collections import deque


from circuits import Component
from circuits.protocols.irc import PRIVMSG


from ..utils import log
from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def rlog(self, source, target, args):
        """Display Remote Message Logs

        Syntax: rlog
        """

        data = self.parent.data

        rmessages = data["rmessages"]

        yield "Last 5 Remote Messages:"
        for i, message in enumerate(rmessages):
            yield " {0:d}: {1:s}".format((i + 1), message)


class RPC(Component):

    channel = "rpc"

    def message(self, source, target, message):
        self.parent.data["rmessages"].append(message)

        message = "<{0:s}> {1:s}".format(source, message)
        self.fire(PRIVMSG(target, message), "bot")
        return log("Remote Message sent to {0:s}", target)


class RMessage(BasePlugin):
    """RMessage plugin

    This doesn't have any user commands available.
    This plugin listens for remote message events and
    sends a Message Event into the system and returning
    any replies generated.

    Depends on: xmlrpc
    """

    __version__ = "0.0.3"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(RMessage, self).init(*args, **kwargs)

        self.data.init(
            {
                "rmessages": deque([], 5)
            }
        )

        RPC().register(self)
        Commands().register(self)
