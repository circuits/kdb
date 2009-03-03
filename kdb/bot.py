# Filename: bot.py
# Module:   bot
# Date:     17th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""bot - Bot Module

This module defines the Bot Component which connects to an IRC
Network and reacts to IRC Events. The Bot Component consists
of the TCPClient and IRC Components.
"""

from circuits.lib.log import Info as LogInfo
from circuits.lib.irc import IRC, Pass, User, Nick
from circuits.lib.sockets import TCPClient, Connect
from circuits import handler, Event, Component, Timer

from kdb import __name__ as systemName
from kdb import __description__ as systemDesc

###
### Events
###

class Reconnect(Event):
    "Reconnect Event"

###
### Components
###

class Bot(Component):
    """Bot(env, port=6667, address="127.0.0.1") -> Bot Component

    Arguments:
       env     - System Environment
       port    - irc port to connect to
       address - irc server to connect to
       ssl     - If True, enable SSL Encryption
       bind    - (address, port) to bind to
       auth    - Authentication Dictionary

    Call connect() to connect to the given irc server given by
    port and address.
    """

    def __init__(self, env, host="127.0.0.1", port=6667, ssl=False, bind=None,
            auth=None, channel="bot"):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Bot, self).__init__(channel=channel)

        self.env = env
        self.auth = auth

        irc = IRC(channel=channel)
        client = TCPClient(host, port, ssl, bind, channel=channel)
        self += (client + irc)

    def reconnect(self):
        self.push(Connect(), "connect")
    
    def connected(self, host, port):
        if self.auth.has_key("password"):
            self.push(Pass(auth["password"]), "PASS")

        self.push(User(
                self.auth.get("ident", systemName),
                self.auth.get("host", "localhost"),
                self.auth.get("server", "localhost"),
                self.auth.get("name", systemDesc)), "USER")

        self.push(Nick(self.auth.get("nick", systemName)), "NICK")

    def disconnected(self):
        s = 60
        self.push(LogInfo("Disconnected. Reconnecting in %ds" % s), "info", "log")
        self += Timer(s, Reconnect(), "reconnect", self)
