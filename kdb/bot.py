# Filename: bot.py
# Module:   bot
# Date:     17th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""bot - Bot Module

This module defines the Bot Component which connects to an IRC
Network and reacts to IRC Events. The Bot Component consists
of the TCPClient and IRC Components.
"""

from circuits.lib.irc import IRC
from circuits.lib.sockets import TCPClient
from circuits.lib.log import Info as LogInfo
from circuits import listener, Event, Component, Timer

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

    def __init__(self, env, port=6667, address="127.0.0.1",
            ssl=False, bind=None, auth=None, channel="bot"):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Bot, self).__init__(channel=channel)

        self.env = env
        self.port = port
        self.address = address
        self.ssl = ssl
        self.bind = bind
        self.auth = auth

        self.irc = IRC(channel=channel)
        self.client = TCPClient(channel=channel)

        self.client += self.irc
        self += self.client

    def connect(self):
        """B.connect()

        Connect to the irc network by sending an optional apssword
        if required and sending our user details and nickname.
        """

        self.client.open(self.address, self.port, self.ssl)

    @listener("timer:reconnect")
    def onTIMERRECONNECT(self):
        self.connect()
    
    def connected(self, host, port):
        if self.auth.has_key("password"):
            self.irc.ircPASS(auth["password"])

        self.irc.ircUSER(
                self.auth.get("ident", systemName),
                self.auth.get("host", "localhost"),
                self.auth.get("server", "localhost"),
                self.auth.get("name", systemDesc))

        self.irc.ircNICK(self.auth.get("nick", systemName))

    def disconnected(self):
        s = 60
        self.push(LogInfo("Disconnected. Reconnecting in %ds" % s), "info", "log")
        self.manager += Timer(s, Reconnect(), "timer:reconnect", self.channel)
