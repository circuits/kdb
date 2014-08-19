# Plugin:   irc
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""IRC

This plugin provides various commands to control the
IRC specific features of kdb. eg: Changing it's nickname.
"""


__version__ = "0.0.9"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from re import search


from circuits.net.events import connect
from circuits import handler, Component
from circuits.protocols.irc import QUIT, NICK, RPL_WELCOME, RPL_YOURHOST

from funcy import first, second


from ..utils import log
from ..events import terminate
from ..plugins import BasePlugin


class Commands(Component):

    channel = "commands"

    def jump(self, source, target, args):
        """Connect to another server.

        Syntax: JUMP <server> [<port>]
        """

        if not args:
            return "Usage: JUMP <server> [<port]"

        tokens = args.split(" ", 2)
        host = first(tokens)
        port = second(tokens)
        port = (port and int(port)) or 6667

        msg = log("Jumping to {0:s}:{1:d}", host, port)

        self.fire(QUIT(msg), "bot")
        self.fire(connect(host, port), "bot")

        return msg

    def ircinfo(self, source, target, args):
        """Display current IRC information

        Syntax: IRCINFO
        """

        if not self.parent.bot.transport.connected:
            return "No IRC information available."

        state = self.parent.data.state.get

        msg = (
            "I am {0:s} on the {1:s} IRC Network. "
            "Connected to {2:s} "
            "Running version {3:s}".format(
                "{0:s}!{1:s}@{2:s}".format(
                    state("nick"),
                    state("ident"),
                    state("host")
                ),
                state("network", "Unknown"),
                state("server_host", "Unknown"),
                state("server_version", "Unknown"),
            )
        )

        return msg

    def status(self, source, target, args):
        """Report IRC Status

        Syntax: STATUS
        """

        if not self.parent.bot.transport.connected:
            return "IRC: Offline"
        return "IRC: Online"

    def quit(self, source, target, args):
        """Quit from the current server

        Syntax: QUIT [<message>]
        """

        if not args:
            message = "Quitting..."
        else:
            message = args

        self.fire(QUIT(message), "bot")

    def die(self, source, target, args):
        """Quit and Terminate

        Syntax: DIE [<message>]
        """

        if not args:
            message = "Shutting down..."
        else:
            message = args

        self.fire(QUIT(message), "bot")
        self.fire(terminate(), "bot")

        return log(message)

    def nick(self, source, target, args):
        """Change current nickname

        Syntax: NICK <nick>
        """

        if not args:
            return "No nick specified."

        nick = first(args.split(" ", 1))

        self.fire(NICK(nick), "bot")


class IRC(BasePlugin):
    """IRC Support plugin

    Provides various general irc commands and support functions.
    eg: NICK, QUIT, etc
    See: commands irc
    """

    def init(self, *args, **kwargs):
        super(IRC, self).init(*args, **kwargs)

        Commands().register(self)

    @handler("numeric")
    def _on_numeric(self, source, numeric, *args):
        if numeric == RPL_WELCOME:
            message = args[1]

            m = search(
                "Welcome to the ([a-zA-Z0-9]*) Internet Relay Chat Network",
                message
            )
            self.data.state["network"] = (
                m is not None and m.group(1)
            ) or "Unknown"
        elif numeric == RPL_YOURHOST:
            message = args[1]

            m = search("Your host is ([a-zA-Z.-]*)", message)
            self.data.state["server_host"] = (
                m is not None and m.group(1)
            ) or self.bot.host

            m = search("running version (.*)", message)
            self.data.state["server_version"] = (
                m is not None and m.group(1)
            ) or "unknown"
