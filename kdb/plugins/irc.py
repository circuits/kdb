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
from circuits.net.protocols.irc import Quit, Nick

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
            self.push(Event(), "joinchannels", self.channel)
        elif numeric == 433:
            self.push(Event(), "nicksollision", self.channel)

    def cmdJUMP(self, source, target, server, port=6667, ssl=False):
        """Connect to another server.

        Syntax: JUMP <server> [<port>] [<ssl>]
        """

        self.push(Quit("Reconnecting to %s:%s" % (server, port)), "QUIT")
        self.push(Connect(host, port, ssl), "connect")

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

        self.push(Quit(message), "QUIT")

        return "Okay"

    def cmdDIE(self, source, target, message="Terminating! Bye!"):
        """Quit and Terminate

        Syntax: DIE [<message>]
        """

        self.cmdQUIT(source, target, message)
        self.push(Terminate(), target=self.env.bot)

        return "Terminating"

    def cmdNICK(self, source, target, nick):
        """Change current nickname

        Syntax: NICK <newnick>
        """

        self.push(Nick(nick), "NICK")

        return "Okay"
