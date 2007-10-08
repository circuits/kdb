# Filename: bot.py
# Module:	bot
# Date:		17th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""IRC Bot Component

This module defines the Bot class which connects to an IRC
Network and reacts to IRC Events. The Bot class is just
a thin layer which sub-classes pymills.sockets.TCPClient
and pymills.irc.IRC
"""

from pymills.net.irc import IRC
from pymills.event import listener
from pymills.net.sockets import TCPClient

from kdb import __name__ as systemName
from kdb import __description__ as systemDesc

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

		super(Bot, self).__init__(event)

		self.env = env

	def connect(self, auth):
		"""B.connect(auth)

		Connect to a given IRC Server using the options
		found in the auth dict.

		At minimum the auth dict must contain:
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

		THis will send the given data along with a \\r\\n to
		the connected TCP Client (pymills.sockets.TCPClient)
		"""

		self.write(data + "\r\n")
