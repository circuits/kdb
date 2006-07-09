# Filename: bot.py
# Module:	bot
# Date:		17th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""The Bot

This module defines the Bot class which connects to an IRC
Network and reacts to IRC Events. The Bot class is just
a thin layer which sub-classes pymills.sockets.TCPClient
and pymills.irc.IRC
"""

from pymills.irc import IRC
from pymills.event import filter, listener
from pymills.sockets import TCPClient

from kdb import __name__ as systemName
from kdb import __desc__ as systemDesc

class Bot(TCPClient, IRC):
	"""Bot(event, env) -> new bot object

	Create a new bot object. This implements a
	TCP Socket and the IRC protocol and is a
	sub-class of pymills.sockets.TCPClient and
	pymills.irc.IRC

	A method is defined to allow the newly created
	bot to connect to an IRC Server.
	"""

	def __init__(self, event, env):
		"initializes x; see x.__class__.__doc__ for signature"

		TCPClient.__init__(self)
		IRC.__init__(self)

		self.env = env
	
	def connect(self, auth):
		"""B.connect(auth)

		Connect to a given IRC Server using the options
		found in the auth dict.

		At minimum the auth dict must contains:
		 * ident
		 * host
		 * server
		 * name
		 * nick
		"""

		if auth.has_key("pass"):
			self.ircPASS(auth["password"])

		self.ircUSER(
				auth.get("ident", systemName),
				auth.get("host", "localhost"),
				auth.get("server", "localhost"),
				auth.get("name", systemDesc))

		self.ircNICK(auth.get("nick", systemName))

	def ircRAW(self, data):
		"""B.ircRAW(data) -> None

		Send a raw message.

		THis will send the given data along with a \r\n to
		the connected TCP Client (pymills.sockets.TCPClient)
		"""

		self.write(data + "\r\n")

	@listener("read")
	def onREAD(self, line):
		"""Read Event

		Process read events by both the TCPClient and IRC
		sub-classes.
		"""

		TCPClient.onREAD(self, line)
		IRC.onREAD(self, line)
