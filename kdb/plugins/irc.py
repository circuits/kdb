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
from circuits.lib.irc import Quit, Nick
from circuits.lib.sockets import Connect

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

    def cmdJUMP(self, source, server, port=6667, ssl=False):
        """Connect to another server.

        Syntax: JUMP <server> [<port>] [<ssl>]
        """

        self.push(Quit("Reconnecting to %s:%s" % (server, port)), "QUIT")
        self.push(Connect(host, port, ssl), "connect")

    def cmdIRCINFO(self, source):
        """Display current IRC information such as server,
        network, current nick, etc.

        Syntax: IRCINFO
        """

        msg = "I am %s on the %s IRC Network connected to " \
                "%s running version %s" % ("%s!%s@%s" % (
                    self("getNick"), self("getIdent"),
                    self("getHost")),
                    self("getNetwork"), self("getServer"),
                    self("getServerVersion"))

        return msg

    def cmdQUIT(self, source, message="Bye! Bye!"):
        """Quit from the current server

        Syntax: QUIT [<message>]
        """

        self.push(Quit(message), "QUIT")

        return "Okay"

    def cmdDIE(self, source, message="Terminating! Bye!"):
        """Quit and Terminate

        Syntax: DIE [<message>]
        """

        self.cmdQUIT(source, message)
        self.push(Event(), "stop", "core")

        return "Terminating"

    def cmdNICK(self, source, nick):
        """Change current nickname

        Syntax: NICK <newnick>
        """

        self.push(Nick(nick), "NICK")

        return "Okay"
