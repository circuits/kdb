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

from circuits.app.log import Log
from circuits import Event, Component, Timer
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, PASS, USER, NICK

###
### Events
###

class Reconnect(Event):
    "Reconnect Event"

class Terminate(Event):
    """Terminate Event"""

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

        self.terminate = False

        self.host = self.env.config.get("server", "host", "0.0.0.0")
        self.port = self.env.config.getint("server", "port", 80)
        self.ssl  = self.env.config.getboolean("server", "ssl", False)
        self.bind = self.env.config.get("server", "bind", None)

        self.auth = {
                "host": socket.gethostname(),
                "server": self.host,
                "nick": self.env.config.get("bot", "nick", "kdb"),
                "ident": self.env.config.get("bot", "ident", "kdb"),
                "name": self.env.config.get("bot", "name",
                    "Knowledge (IRC) Database Bot")
        }
        if self.env.config.has_option("server", "password"):
            self.auth["password"] = self.env.config.get("server", "password")

        irc = IRC(channel=self.channel)
        client = TCPClient(self.bind, channel=self.channel)
        self += (client + irc)

    def ready(self, component):
        self.fire(Connect(self.host, self.port, self.ssl))

    def reconnect(self):
        self.fire(Connect(self.host, self.port, self.ssl))
    
    def connected(self, host, port=None):
        if "password" in self.auth:
            self.fire(PASS(auth["password"]))

        auth = self.auth.get

        ident = auth("ident")
        host = auth("host")
        server = auth("server")
        name = auth("name")
        self.fire(USER(ident, host, server, name))

        nick = auth("nick")
        self.fire(NICK(nick))

    def disconnected(self):
        if self.terminate:
            raise SystemExit(0)

        s = 60
        self.fire(Log("info", "Disconnected. Reconnecting in %ds" % s))
        Timer(s, Reconnect(), "reconnect", self).register(self)

    def terminate(self):
        self.terminate = True
