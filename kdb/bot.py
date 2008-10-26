# Filename: bot.py
# Module:	bot
# Date:		17th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""bot - Bot Module

This module defines the Bot Component which connects to an IRC
Network and reacts to IRC Events. The Bot Component consists
of the TCPClient and IRC Components.
"""

from circuits.lib.irc import IRC
from circuits.lib.sockets import TCPClient

from kdb import __name__ as systemName
from kdb import __description__ as systemDesc

class Bot(TCPClient, IRC):
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
			ssl=False, bind=None, auth=None):
		"initializes x; see x.__class__.__doc__ for signature"

		super(Bot, self).__init__()

		self.env = env
		self.port = port
		self.address = address
		self.ssl = ssl
		self.bind = bind
		self.auth = auth

	def connect(self):
		"""B.connect()

		Connect to the irc network by sending an optional apssword
		if required and sending our user details and nickname.
		"""

		auth = self.auth

		if auth.has_key("password"):
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

		THis will send the given data along with a \\r\\n
		"""

		self.write(data + "\r\n")
