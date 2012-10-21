# Module:   irc
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""IRC

This plugin provides various commands to control the
IRC specific features of kdb. eg: Changing it's nickname.
"""

__version__ = "0.0.9"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import sleep

from circuits import Event
from circuits.net.sockets import Connect
from circuits.net.protocols.irc import QUIT, NICK

from kdb.bot import Terminate
from kdb.plugin import BasePlugin

class Irc(BasePlugin):

    """IRC Support plugin

    Provides various general irc commands and support functions.
    eg: NICK, QUIT, etc
    See: commands irc
    """

    def numeric(self, source, target, numeric, arg, message):
        if numeric == 1:
            self.fire(Event.create("joinchannels"))
        elif numeric == 433:
            self.fire(Event.create("nicksollision"))

    def cmdJUMP(self, source, target, server, port=6667, ssl=False):
        """Connect to another server.

        Syntax: JUMP <server> [<port>] [<ssl>]
        """

        self.fire(QUIT("Reconnecting to %s:%s" % (server, port)))
        self.fire(Connect(host, port, ssl), "connect")

    def cmdIRCINFO(self, source, target):
        """Display current IRC information such as server,
        network, current nick, etc.

        Syntax: IRCINFO
        """

        auth = self.env.bot.auth.get

        msg = "I am %s on the %s IRC Network connected to " \
                "%s running version %s" % ("%s!%s@%s" % (
                    auth("nick"),
                    auth("ident"),
                    auth("host")),
                    auth("network", "unknown"),
                    auth("server"),
                    auth("serverVersion", "unknown"))

        return msg

    def cmdQUIT(self, source, target, message="Bye! Bye!"):
        """Quit from the current server

        Syntax: QUIT [<message>]
        """

        self.fire(QUIT(message))

        return "Okay"

    def cmdDIE(self, source, target, message="Terminating! Bye!"):
        """Quit and Terminate

        Syntax: DIE [<message>]
        """

        self.cmdQUIT(source, target, message)
        self.fire(Terminate(), self.env.bot)

        return "Terminating"

    def cmdNICK(self, source, target, nick):
        """Change current nickname

        Syntax: NICK <newnick>
        """

        self.fire(NICK(nick))

        return "Okay"
