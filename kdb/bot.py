# Filename: bot.py
# Module:   bot
# Date:     17th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""bot - Bot Module

This module defines the Bot Component which connects to an IRC
Network and reacts to IRC Events. The Bot Component consists
of the TCPClient and IRC Components.
"""

import socket

from circuits import Event, Component, Timer
from circuits.app.log import Info as LogInfo
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, Pass, User, Nick

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

    channel = "bot"

    def __init__(self, env):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Bot, self).__init__()

        self.env = env

        self.host = self.env.config.get("server", "host", "0.0.0.0")
        self.port = self.env.config.getint("server", "port", 80)
        self.ssl  = self.env.config.getboolean("server", "ssl", False)
        self.bind = self.env.config.get("server", "bind", None)

        self.auth = {
                "host": socket.gethostname(),
                "server": self.host,
                "nick": self.env.config.get("bot", "nick", systemName),
                "ident": self.env.config.get("bot", "ident", systemName),
                "name": self.env.config.get("bot", "name", systemDesc)
        }
        if self.env.config.has_option("server", "password"):
            self.auth["password"] = self.env.config.get("server", "password")

        irc = IRC(channel=self.channel)
        client = TCPClient(self.bind, channel=self.channel)
        self += (client + irc)

    def registered(self, component, manager):
        if component == self:
            self.push(Connect(self.host, self.port, self.ssl), "connect")

    def reconnect(self):
        self.push(Connect(self.host, self.port, self.ssl), "connect")
    
    def connected(self, host, port):
        if "password" in self.auth:
            self.push(Pass(auth["password"]), "PASS")

        auth = self.auth.get

        self.push(User(
            auth("ident"), auth("host"), auth("server"), auth("name")), "USER")

        self.push(Nick(auth("nick")), "NICK")

    def disconnected(self):
        s = 60
        self.push(LogInfo("Disconnected. Reconnecting in %ds" % s), "info", "log")
        self += Timer(s, Reconnect(), "reconnect", self)
